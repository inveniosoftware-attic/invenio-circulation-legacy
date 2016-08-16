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


"""Module REST API tests."""

import json

import pytest
from flask import url_for
from invenio_indexer.api import RecordIndexer
from invenio_search import current_search

from invenio_circulation.api import Item
from invenio_circulation.minters import circulation_item_minter


def test_crud_read(app, db, es):
    """Test REST API get functionality."""
    item = Item.create({'foo': 'bar'})
    circulation_item_minter(item.id, item)
    item.commit()
    db.session.commit()

    record_indexer = RecordIndexer()
    record_indexer.index(item)

    current_search.flush_and_refresh('_all')

    with app.test_request_context():
        with app.test_client() as client:
            url = url_for('circulation_rest.crcitm_item',
                          pid_value=item['control_number'])
            res = client.get(url)
            fetched_item = json.loads(res.data.decode('utf-8'))['metadata']

            assert fetched_item['control_number'] == item['control_number']


@pytest.mark.parametrize(('url_addition', 'count'), [
    # Empty parameters returns 'all'
    ('', 1),
    # Search for exisiting item
    ('?q=foo:bar', 1),
    # Search for non-exisiting item
    ('?q=foo:baz', 0)
])
def test_rest_search(app, db, es, url_addition, count):
    """Test REST API search functionality."""
    item = Item.create({'foo': 'bar'})
    circulation_item_minter(item.id, item)
    item.commit()
    db.session.commit()

    record_indexer = RecordIndexer()
    record_indexer.index(item)

    current_search.flush_and_refresh('_all')

    with app.test_request_context():
        with app.test_client() as client:
            base_url = url_for('circulation_rest.crcitm_list')
            url = base_url + url_addition

            res = client.get(url)
            hits = json.loads(res.data.decode('utf-8'))['hits']['hits']
            assert len(hits) == count
