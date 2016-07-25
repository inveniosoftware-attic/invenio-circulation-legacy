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


"""Module entities tests."""

import pytest
from invenio_pidstore.errors import PIDInvalidAction

from invenio_circulation.api import Item, ItemStatus, Location


def test_location_create(app, db):
    loc = Location.create({})


def test_item_create(app, db):
    item = Item.create({})

    assert item['_circulation']['status'] == ItemStatus.ON_SHELF
    assert len(item['_circulation']['holdings']) == 0


def test_item_circulation_loan(app, db):
    item = Item.create({})

    # Loan the item
    item.loan_item()
    assert item['_circulation']['status'] == ItemStatus.ON_LOAN
    assert len(item['_circulation']['holdings']) == 1

    # Return the item
    item.return_item()
    assert item['_circulation']['status'] == ItemStatus.ON_SHELF
    assert len(item['_circulation']['holdings']) == 0

    # Loan the item
    item.loan_item()

    # Loan again
    with pytest.raises(PIDInvalidAction):
        item.loan_item(1)


def test_item_request(app, db):
    item = Item.create({})

    # Request the item
    item.request_item()
    assert item['_circulation']['status'] == ItemStatus.ON_SHELF
    assert len(item['_circulation']['holdings']) == 1


def test_item_lose(app, db):
    item = Item.create({})

    # Lose the item
    item.lose_item()
    assert item['_circulation']['status'] == ItemStatus.MISSING

    # Return missing item
    item.return_missing_item()
    assert item['_circulation']['status'] == ItemStatus.ON_SHELF

    # Request the item
    item.request_item()

    # Lose the item
    item.lose_item()
    assert item['_circulation']['status'] == ItemStatus.MISSING
    assert len(item['_circulation']['holdings']) == 0


def test_item_extend_loan(app, db):
    item = Item.create({})

    # Loan the item
    item.loan_item()

    # Extend the loan
    item.extend_loan()
    assert item['_circulation']['status'] == ItemStatus.ON_LOAN


def test_cancel_hold(app, db):
    item = Item.create({})

    # Loan the item
    item.request_item()

    item.cancel_hold(item['_circulation']['holdings'][0]['id'])

    assert len(item['_circulation']['holdings']) == 0

    with pytest.raises(Exception):
        item.cancel_hold(1)
