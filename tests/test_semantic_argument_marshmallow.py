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
import uuid

import pytest

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
    assert not circulation_event_schema.validate({})
    assert not circulation_event_schema.validate({
        'start_date': datetime.date.today(),
        'end_date':  datetime.date.today() + datetime.timedelta(weeks=4),
    })

    # Invalid start date
    errors = circulation_event_schema.validate({
        'start_date': datetime.date.today() + datetime.timedelta(days=1),
        'end_date':  datetime.date.today() + datetime.timedelta(weeks=4),
    })
    assert 'start_date' in errors

    # Invalid duration
    errors = circulation_event_schema.validate({
        'start_date': datetime.date.today(),
        'end_date':  datetime.date.today() + datetime.timedelta(weeks=5),
    })
    assert '_schema' in errors

    # Invalid item status
    item['_circulation']['status'] = 'foo'
    circulation_event_schema.context['item'] = item

    errors = circulation_event_schema.validate({})
    assert '_schema' in errors


def test_request_item_marshmallow(app, db):
    """Use LoanItemSchema to validate request_item parameters."""
    item = Item.create({})
    db.session.commit()

    circulation_event_schema = RequestItemSchema()
    circulation_event_schema.context['item'] = item

    # Valid arguments
    assert not circulation_event_schema.validate({})
    assert not circulation_event_schema.validate({
        'start_date': datetime.date.today(),
        'end_date':  datetime.date.today() + datetime.timedelta(weeks=4),
    })

    # Valid arguments date in the future
    errors = circulation_event_schema.validate({
        'start_date': datetime.date.today() + datetime.timedelta(days=1),
        'end_date':  datetime.date.today() + datetime.timedelta(weeks=4),
    })
    assert not errors

    # Invalid start date
    errors = circulation_event_schema.validate({
        'start_date': datetime.date.today() + datetime.timedelta(days=-1),
        'end_date':  datetime.date.today() + datetime.timedelta(weeks=4),
    })
    assert 'start_date' in errors

    # Invalid duration
    errors = circulation_event_schema.validate({
        'start_date': datetime.date.today(),
        'end_date':  datetime.date.today() + datetime.timedelta(weeks=5),
    })
    assert '_schema' in errors

    # Invalid item status
    item['_circulation']['status'] = ItemStatus.MISSING
    circulation_event_schema.context['item'] = item

    errors = circulation_event_schema.validate({})
    assert '_schema' in errors


def test_return_item_marshmallow(app, db):
    """Use LoanItemSchema to validate return_item parameters."""
    item = Item.create({})
    db.session.commit()

    circulation_event_schema = ReturnItemSchema()
    circulation_event_schema.context['item'] = item

    # No item to return arguments
    errors = circulation_event_schema.validate({})
    assert '_schema' in errors

    # No active hold
    item.request_item(**RequestItemSchema().dump({
        'start_date': datetime.date.today() + datetime.timedelta(weeks=1),
    }).data)
    item.commit()
    errors = circulation_event_schema.validate({})
    assert '_schema' in errors


def test_return_missing_item_marshmallow(app, db):
    """Use LoanItemSchema to validate return_missing_item parameters."""
    item = Item.create({})
    db.session.commit()

    circulation_event_schema = ReturnMissingItemSchema()
    circulation_event_schema.context['item'] = item

    # Item not missing
    errors = circulation_event_schema.validate({})
    assert '_schema' in errors

    item.lose_item()
    assert not circulation_event_schema.validate({})


def test_cancel_item_marshmallow(app, db):
    """Use LoanItemSchema to validate cancel_hold parameters."""
    item = Item.create({})
    item.loan_item()
    db.session.commit()

    hold_id = item.holdings[0]['id']

    circulation_event_schema = CancelItemSchema()
    circulation_event_schema.context['item'] = item

    # No existing UUID
    errors = circulation_event_schema.validate({
        'hold_id': str(uuid.uuid4())
    })
    assert '_schema' in errors

    # Valid argument
    assert not circulation_event_schema.validate({
        'hold_id': str(hold_id)
    })


def test_extend_loan_marshmallow(app, db):
    """Use LoanItemSchema to validate extend_loan parameters."""
    item = Item.create({})
    db.session.commit()

    circulation_event_schema = ExtendItemSchema()
    circulation_event_schema.context['item'] = item

    # Valid arguments
    assert not circulation_event_schema.validate({})

    # Date too far in the future
    requested_end_date = datetime.date.today() + datetime.timedelta(weeks=5)
    errors = circulation_event_schema.validate({
        'requested_end_date': requested_end_date
    })
    assert '_schema' in errors


@pytest.mark.parametrize((
    'request_arguments',
    'validate_arguments',
    'assert_statement'
), [
    # Request non-overlapping
    # Existing: |---|
    # New:           |---|
    ({},
     {'start_date': datetime.date.today() + datetime.timedelta(weeks=5)},
     lambda errors: not errors
     ),
    # Try to request for the same period
    # Existing: |---|
    # New:      |---|
    ({},
     {},
     lambda errors: '_schema' in errors
     ),
    # Try to request with overlap
    # Existing: |---|
    # New:        |---|
    ({},
     {'start_date': datetime.date.today() + datetime.timedelta(weeks=2)},
     lambda errors: '_schema' in errors
     ),
    # Try to request with overlap
    # Existing:   |---|
    # New:      |---|
    ({'start_date': datetime.date.today() + datetime.timedelta(weeks=2)},
     {},
     lambda errors: '_schema' in errors
     ),
    # Try to request including
    # Existing:  |-|
    # New:      |---|
    ({'start_date': datetime.date.today() + datetime.timedelta(weeks=1),
      'end_date': datetime.date.today() + datetime.timedelta(weeks=2)},
     {},
     lambda errors: '_schema' in errors
     )
])
def test_blocking_holds(app, db,
                        request_arguments,
                        validate_arguments,
                        assert_statement):
    item = Item.create({})
    db.session.commit()

    circulation_event_schema = RequestItemSchema()
    circulation_event_schema.context['item'] = item

    item.request_item(**RequestItemSchema().dump(request_arguments).data)
    item.commit()
    errors = circulation_event_schema.validate(validate_arguments)
    assert assert_statement(errors)
