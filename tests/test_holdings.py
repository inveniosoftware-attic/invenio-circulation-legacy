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


"""Holding object tests."""

import uuid

from invenio_circulation.api import Holding, Item


def test_holdings(app, db):
    """Test basic Item.holdings functionality."""
    item = Item.create({})

    assert not item.holdings

    # Append an item

    id1 = str(uuid.uuid4())
    holding = Holding.create(id_=id1)

    item.holdings.append(holding)
    assert len(item.holdings) == 1
    assert id1 in item.holdings

    # Insert an item

    id2 = str(uuid.uuid4())
    holding = Holding.create(id_=id2)

    item.holdings.insert(0, holding)
    assert len(item.holdings) == 2
    assert [id2, id1] == [x['id'] for x in item.holdings]

    # Delete an item

    del item.holdings[id2]
    assert len(item.holdings) == 1
    assert id2 not in item.holdings
    assert id1 in item.holdings
