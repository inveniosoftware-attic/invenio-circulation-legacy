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


"""Elasticsearch tests."""

from invenio_indexer.api import RecordIndexer
from invenio_search import current_search

from invenio_circulation.api import Item
from invenio_circulation.search import ItemSearch


def test_basic_search(app, db, es):
    """Test basic search functionality."""
    # The index should be empty
    assert len(ItemSearch().execute()) == 0

    # Create item1, search for everything
    item1 = Item.create({})
    item1.commit()

    record_indexer = RecordIndexer()
    record_indexer.index(item1)

    current_search.flush_and_refresh('_all')

    assert len(ItemSearch().execute()) == 1

    # Create item2, search for everything again
    item2 = Item.create({'foo': 'bar'})
    item2.commit()
    record_indexer.index(item2)

    current_search.flush_and_refresh('_all')

    assert len(ItemSearch().execute()) == 2

    # Search for item2
    assert len(ItemSearch().query('match', foo='bar').execute()) == 1

    # Search for nonsense
    assert len(ItemSearch().query('match', foo='banana').execute()) == 0
