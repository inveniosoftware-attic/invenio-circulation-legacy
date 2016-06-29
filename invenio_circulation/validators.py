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
from marshmallow import Schema, ValidationError, fields
from marshmallow.decorators import validates


def _today():
    return datetime.date.today()


def _max_loan_duration():
    loan_duration = current_app.config['CIRCULATION_LOAN_PERIOD']
    return _today() + datetime.timedelta(days=loan_duration)


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

    start_date = DateField(default=_today)
    end_date = DateField(default=_max_loan_duration)
    waitlist = fields.Boolean(default=False)
    delivery = fields.String(default='mail')

    @validates('delivery')
    def validate_delivery(self, obj):
        """Check if a given argument has the value *mail* or *pickup*."""
        if obj not in ['mail', 'pickup']:
            raise ValidationError('Delivery is neither *mail* nor *pickup*.')


class RequestArgument(LoanArgument):
    """Marshmallow Schema class to validate Item.loan_item arguments."""

    pass


class CancelArgument(Schema):
    """Marshmallow Schema class to validate Item.loan_item arguments."""

    id = UUIDField(required=True)


class ExtensionArgument(Schema):
    """Marshmallow Schema class to validate Item.loan_item arguments."""

    requested_end_date = DateField(default=_max_loan_duration)
