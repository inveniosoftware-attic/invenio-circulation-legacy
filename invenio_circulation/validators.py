# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.


"""Circulation argument validation."""


import datetime
import uuid

from flask import current_app
from flask_login import current_user
from intervals import DateInterval, IllegalArgument
from marshmallow import Schema, ValidationError, fields
from marshmallow.decorators import validates, validates_schema

from .models import ItemStatus


def _today():
    return datetime.date.today()


def _max_loan_duration(start_date=None):
    start_date = start_date or _today()
    loan_duration = current_app.config['CIRCULATION_LOAN_PERIOD']
    return start_date + datetime.timedelta(days=loan_duration)


def _get_current_user_id():
    """Get the id of the current_user, if existing."""
    if current_user:
        return current_user.id
    return None


def validate(schema, kwargs):
    """Helper function to validate the given arguments against the schema."""
    errors = schema.validate(kwargs)
    if errors:
        raise ValidationError(errors)


class DateField(fields.Date):
    """Marshmallow date field to handle none string dates."""

    def _deserialize(self, value, attr, data):
        if isinstance(value, datetime.date):
            return value
        return super(DateField, self)._deserialize(value, attr, data)


class UUIDField(fields.UUID):
    """Marshmallow date field to handle none string dates."""

    def _deserialize(self, value, attr, data):
        if isinstance(value, uuid.UUID):
            return value
        return super(UUIDField, self)._deserialize(value, attr, data)


class LoanArgument(Schema):
    """Marshmallow Schema class to validate Item.loan_item arguments."""

    start_date = DateField(default=lambda: _today().isoformat())
    end_date = DateField(default=lambda: _max_loan_duration().isoformat())
    waitlist = fields.Boolean(default=False)
    delivery = fields.String(default='mail')
    user_id = fields.Integer(default=_get_current_user_id)

    @validates('delivery')
    def validate_delivery(self, obj):
        """Check if a given argument has the value *mail* or *pickup*."""
        if obj not in ['mail', 'pickup']:
            raise ValidationError('Delivery is neither *mail* nor *pickup*.')


class RequestArgument(LoanArgument):
    """Marshmallow Schema class to validate Item.loan_item arguments."""


class CancelArgument(Schema):
    """Marshmallow Schema class to validate Item.loan_item arguments."""

    hold_id = UUIDField(required=True)


class ExtensionArgument(Schema):
    """Marshmallow Schema class to validate Item.loan_item arguments."""

    requested_end_date = DateField(default=_max_loan_duration)


class ArgumentDurationMixin(object):
    """Marshmallow mixin to check the loan duration."""

    @validates_schema
    def validate_duration(self, data):
        """Check if loan duration is valid."""
        data.setdefault('start_date', _today())
        data.setdefault('end_date', _max_loan_duration(data['start_date']))

        duration = (data['end_date'] - data['start_date']).days
        if duration > current_app.config['CIRCULATION_LOAN_PERIOD']:
            raise ValidationError('Loan duration too long.')


class HoldingSchema(Schema):
    """Marshmallow mixin to check if holding overlaps with given interval."""

    start_date = DateField()
    end_date = DateField()

    @validates_schema
    def validate_interval(self, data):
        """Check if holding blocks the loan/request."""
        # Create an interval for the currently checked holding
        # holding['start_date'] -> holding['end_date']
        holding_interval = DateInterval([data['start_date'], data['end_date']])

        # If there is an intersection between those two intervals, then the
        # desired dates of the requested holding are not available
        try:
            intersection = holding_interval & self.context['request_interval']
            raise ValidationError(intersection)
        except IllegalArgument:
            pass


class ArgumentHoldingMixin(object):
    """Marshmallow mixin to check blocking holdings."""

    @validates_schema
    def validate_holdings(self, data):
        """Check if another holding blocks the loan/request."""
        item = self.context['item']

        start = data.get('start_date', _today())
        end = data.get('end_date', _max_loan_duration(start))

        # Create an interval for the requested/new holding
        holding_schema = HoldingSchema(
            context={'request_interval': DateInterval([start, end])}
        )

        errors = []
        for hold in item.holdings:
            current_error = holding_schema.validate(hold)

            if current_error:
                errors.append((hold['id'], current_error))

        if errors:
            raise ValidationError(errors)


class LoanItemSchema(ArgumentDurationMixin, ArgumentHoldingMixin,
                     LoanArgument):
    """Marshmallow Schema class to validate loan_item arguments."""

    @validates('start_date')
    def validate_start(self, start_date):
        """Check if start_date is today."""
        if start_date != datetime.date.today():
            raise ValidationError('Start date must be today.')

    @validates_schema
    def validate_status(self, data):
        """Check if the current status is on_shelf."""
        item = self.context['item']
        if item['_circulation']['status'] != ItemStatus.ON_SHELF:
            raise ValidationError('Status must be on_shelf.')


class RequestItemSchema(ArgumentDurationMixin, ArgumentHoldingMixin,
                        RequestArgument):
    """Marshmallow Schema class to validate request_item arguments."""

    @validates('start_date')
    def validate_start(self, start_date):
        """Check if start_date is today."""
        if start_date < datetime.date.today():
            raise ValidationError('Start date must be today or later.')

    @validates_schema
    def validate_status(self, data):
        """Check if the current status is on_shelf."""
        item = self.context['item']
        if item['_circulation']['status'] == ItemStatus.MISSING:
            raise ValidationError('The item is currently missing.')


class ReturnItemSchema(Schema):
    """Marshmallow Schema class to validate return_item arguments."""

    @validates_schema
    def validate_active_loan(self, data):
        """Assert the current holding to be a loan."""
        item = self.context['item']

        if not item.holdings:
            raise ValidationError('There is no active loan.')

        # An active loan exists if item.holding[0]['start_date'] is today (the
        # momemnt the item is returned) or earlier. Otherwise, it's a request
        holding_start_date = datetime.datetime.strptime(
            item.holdings[0]['start_date'],
            current_app.config['CIRCULATION_DATE_FORMAT']
        ).date()
        if _today() < holding_start_date:
            raise ValidationError('There is no active loan.')


class ReturnMissingItemSchema(Schema):
    """Marshmallow Schema class to validate return_missing_item arguments."""

    @validates_schema
    def validate_item_status(self, data):
        """Assert the item to be missing."""
        item = self.context['item']

        if item['_circulation']['status'] != ItemStatus.MISSING:
            raise ValidationError('The item must be missing.')


class CancelItemSchema(CancelArgument):
    """Marshmallow Schema class to validate cancel_hold arguments."""

    @validates_schema
    def validate_holding_id(self, data):
        """Assert the hold to be associated with the item."""
        item = self.context['item']

        if str(data['hold_id']) not in item.holdings:
            raise ValidationError('The hold is not associated with the item.')


class ExtendItemSchema(ExtensionArgument):
    """Marshmallow Schema class to validate exnted_loan arguments."""

    @validates_schema
    def validate_requested_end_date(self, data):
        """Assert the that the requested end date is valid."""
        if 'requested_end_date' not in data:
            return

        loan_duration = current_app.config['CIRCULATION_LOAN_PERIOD']
        max_loan = _today() + datetime.timedelta(days=loan_duration)

        if data['requested_end_date'] > max_loan:
            raise ValidationError('The requested end date is too late.')
