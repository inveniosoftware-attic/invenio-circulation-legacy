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


"""Semantic argument marshmallowing tests."""

import datetime
import json
import uuid

from invenio_circulation.api import Item, ItemStatus
from invenio_circulation.validators import CancelItemSchema, \
    ExtendItemSchema, LoanItemSchema, RequestItemSchema, ReturnItemSchema, \
    ReturnMissingItemSchema


def test_loan_item_marshmallow(app, db):
    """Use LoanItemSchema to validate loan_item parameters."""
    item = Item.create({})
    db.session.commit()

    circulation_event_schema = LoanItemSchema()
    circulation_event_schema.context['item'] = item

    # Valid arguments
    arguments = {}
    assert not circulation_event_schema.validate(arguments)

    arguments = {
        'start_date': datetime.date.today(),
        'end_date':  datetime.date.today() + datetime.timedelta(weeks=4),
    }
    assert not circulation_event_schema.validate(arguments)

    # Invalid start date
    arguments = {
        'start_date': datetime.date.today() + datetime.timedelta(days=1),
        'end_date':  datetime.date.today() + datetime.timedelta(weeks=4),
    }
    errors = circulation_event_schema.validate(arguments)
    assert 'start_date' in errors

    # Invalid duration
    arguments = {
        'start_date': datetime.date.today(),
        'end_date':  datetime.date.today() + datetime.timedelta(weeks=5),
    }
    errors = circulation_event_schema.validate(arguments)
    assert '_schema' in errors

    # Invalid item status
    arguments = {}
    item['_circulation']['status'] = 'foo'
    circulation_event_schema.context['item'] = item

    errors = circulation_event_schema.validate(arguments)
    assert '_schema' in errors


def test_request_item_marshmallow(app, db):
    """Use LoanItemSchema to validate request_item parameters."""
    item = Item.create({})
    db.session.commit()

    circulation_event_schema = RequestItemSchema()
    circulation_event_schema.context['item'] = item

    # Valid arguments
    arguments = {}
    assert not circulation_event_schema.validate(arguments)

    arguments = {
        'start_date': datetime.date.today(),
        'end_date':  datetime.date.today() + datetime.timedelta(weeks=4),
    }
    assert not circulation_event_schema.validate(arguments)

    # Valid arguments date in the future
    arguments = {
        'start_date': datetime.date.today() + datetime.timedelta(days=1),
        'end_date':  datetime.date.today() + datetime.timedelta(weeks=4),
    }
    errors = circulation_event_schema.validate(arguments)
    assert not circulation_event_schema.validate(arguments)

    # Invalid start date
    arguments = {
        'start_date': datetime.date.today() + datetime.timedelta(days=-1),
        'end_date':  datetime.date.today() + datetime.timedelta(weeks=4),
    }
    errors = circulation_event_schema.validate(arguments)
    assert 'start_date' in errors

    # Invalid duration
    arguments = {
        'start_date': datetime.date.today(),
        'end_date':  datetime.date.today() + datetime.timedelta(weeks=5),
    }
    errors = circulation_event_schema.validate(arguments)
    assert '_schema' in errors

    # Invalid item status
    arguments = {}
    item['_circulation']['status'] = ItemStatus.MISSING
    circulation_event_schema.context['item'] = item

    errors = circulation_event_schema.validate(arguments)
    assert '_schema' in errors


def test_return_item_marshmallow(app, db):
    """Use LoanItemSchema to validate return_item parameters."""
    item = Item.create({})
    db.session.commit()

    circulation_event_schema = ReturnItemSchema()
    circulation_event_schema.context['item'] = item

    # No item to return arguments
    arguments = {}
    errors = circulation_event_schema.validate(arguments)
    assert '_schema' in errors


def test_return_missing_item_marshmallow(app, db):
    """Use LoanItemSchema to validate return_missing_item parameters."""
    item = Item.create({})
    db.session.commit()

    circulation_event_schema = ReturnMissingItemSchema()
    circulation_event_schema.context['item'] = item

    # Item not missing
    arguments = {}
    errors = circulation_event_schema.validate(arguments)
    assert '_schema' in errors

    item.lose_item()
    assert not circulation_event_schema.validate(arguments)


def test_cancel_item_marshmallow(app, db):
    """Use LoanItemSchema to validate cancel_hold parameters."""
    item = Item.create({})
    item.loan_item()
    db.session.commit()

    hold_id = item.holdings[0]['id']

    circulation_event_schema = CancelItemSchema()
    circulation_event_schema.context['item'] = item

    # No existing UUID
    arguments = {'hold_id': str(uuid.uuid4())}
    errors = circulation_event_schema.validate(arguments)
    assert '_schema' in errors

    # Valid argument
    arguments = {'hold_id': str(hold_id)}
    assert not circulation_event_schema.validate(arguments)


def test_extend_loan_marshmallow(app, db):
    """Use LoanItemSchema to validate extend_loan parameters."""
    item = Item.create({})
    db.session.commit()

    circulation_event_schema = ExtendItemSchema()
    circulation_event_schema.context['item'] = item

    # Valid arguments
    arguments = {}
    assert not circulation_event_schema.validate(arguments)

    # Date too far in the future
    requested_end_date = datetime.date.today() + datetime.timedelta(weeks=5)
    arguments = {'requested_end_date': requested_end_date}
    errors = circulation_event_schema.validate(arguments)
    assert '_schema' in errors
