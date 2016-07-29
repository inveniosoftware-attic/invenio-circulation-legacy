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


"""Circulation webhooks."""

from invenio_db import db
from invenio_webhooks.models import Receiver

from .api import Item
from .validators import CancelItemSchema, ExtendItemSchema, LoanItemSchema, \
    RequestItemSchema, ReturnItemSchema, ReturnMissingItemSchema


class ReceiverBase(Receiver):
    """Reciever base class to handle incoming circulation requests."""

    def run(self, event):
        """Process the circulation event.

        This method builds the frame, fetching the item and calling *_run*
        in a nested transaction.
        """
        item = Item.get_record(event.payload['item_id'])
        if hasattr(self, 'circulation_event_schema'):
            self.circulation_event_schema.context['item'] = item
            data, errors = self.circulation_event_schema.load(event.payload)
            if errors:
                event.response_code = 400
                event.response = {'message': errors}
                return
        else:
            data = event.payload

        with db.session.begin_nested():
            self._run(item, data)
            item.commit()


class LoanReceiver(ReceiverBase):
    """Handle incomming loan requests."""

    circulation_event_schema = LoanItemSchema()

    def _run(self, item, payload):
        """Process a loan event."""
        item.loan_item(**payload)


class RequestReceiver(ReceiverBase):
    """Handle incomming requests."""

    circulation_event_schema = RequestItemSchema()

    def _run(self, item, payload):
        """Process a request event."""
        item.request_item(**payload)


class ReturnReceiver(ReceiverBase):
    """Handle incomming return requests."""

    circulation_event_schema = ReturnItemSchema()

    def _run(self, item, _):
        """Process a return event."""
        item.return_item()


class LoseReceiver(ReceiverBase):
    """Handle incomming return requests."""

    def _run(self, item, _):
        """Process a lose event."""
        item.lose_item()


class ReturnMissingReceiver(ReceiverBase):
    """Handle incomming return_missing requests."""

    circulation_event_schema = ReturnMissingItemSchema()

    def _run(self, item, _):
        """Process a return_missing event."""
        item.return_missing_item()


class CancelReceiver(ReceiverBase):
    """Handle incomming cancel requests."""

    circulation_event_schema = CancelItemSchema()

    def _run(self, item, payload):
        """Process a cancel event."""
        item.cancel_hold(payload['hold_id'])


class ExtendReceiver(ReceiverBase):
    """Handle incomming extension requests."""

    circulation_event_schema = ExtendItemSchema()

    def _run(self, item, payload):
        """Process an extend event."""
        item.extend_loan(payload['requested_end_date'])
