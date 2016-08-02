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


"""Module webhook tests."""

import datetime
import json

from flask import url_for

from invenio_circulation.api import Item
from invenio_circulation.models import ItemStatus


def test_loan_return_receiver(app, db, access_token):
    """Use the webhooks api to loan and return an item."""
    item = Item.create({})
    db.session.commit()
    with app.test_request_context():
        with app.test_client() as client:
            url = url_for('invenio_webhooks.event_list',
                          receiver_id='circulation_loan')
            url += '?access_token=' + access_token
            data = {'item_id': str(item.id)}
            res = client.post(url, data=json.dumps(data),
                              content_type='application/json')

            assert res.status_code == 202

            item = Item.get_record(item.id)
            assert item['_circulation']['status'] == ItemStatus.ON_LOAN
            assert len(item['_circulation']['holdings']) == 1

            url = url_for('invenio_webhooks.event_list',
                          receiver_id='circulation_return')
            url += '?access_token=' + access_token
            data = {'item_id': str(item.id)}
            res = client.post(url, data=json.dumps(data),
                              content_type='application/json')

            assert res.status_code == 202

            item = Item.get_record(item.id)
            assert item['_circulation']['status'] == ItemStatus.ON_SHELF
            assert len(item['_circulation']['holdings']) == 0


def test_request_cancel_receiver(app, db, access_token):
    """Use the webhooks api to request and cancel an item."""
    item = Item.create({})
    db.session.commit()
    with app.test_request_context():
        with app.test_client() as client:
            url = url_for('invenio_webhooks.event_list',
                          receiver_id='circulation_request')
            url += '?access_token=' + access_token
            data = {'item_id': str(item.id)}
            res = client.post(url, data=json.dumps(data),
                              content_type='application/json')

            assert res.status_code == 202

            item = Item.get_record(item.id)
            assert item['_circulation']['status'] == ItemStatus.ON_SHELF
            assert len(item['_circulation']['holdings']) == 1

            url = url_for('invenio_webhooks.event_list',
                          receiver_id='circulation_cancel')
            url += '?access_token=' + access_token
            hold_id = item['_circulation']['holdings'][0]['id']
            data = {'item_id': str(item.id), 'hold_id': hold_id}
            res = client.post(url, data=json.dumps(data),
                              content_type='application/json')

            assert res.status_code == 202

            item = Item.get_record(item.id)
            assert item['_circulation']['status'] == ItemStatus.ON_SHELF
            assert len(item['_circulation']['holdings']) == 0


def test_lose_return_missing_receiver(app, db, access_token):
    """Use the webhooks api to lose and return an item."""
    item = Item.create({})
    db.session.commit()
    with app.test_request_context():
        with app.test_client() as client:
            url = url_for('invenio_webhooks.event_list',
                          receiver_id='circulation_lose')
            url += '?access_token=' + access_token
            data = {'item_id': str(item.id)}
            res = client.post(url, data=json.dumps(data),
                              content_type='application/json')

            assert res.status_code == 202

            item = Item.get_record(item.id)
            assert item['_circulation']['status'] == ItemStatus.MISSING

            url = url_for('invenio_webhooks.event_list',
                          receiver_id='circulation_return_missing')
            url += '?access_token=' + access_token
            data = {'item_id': str(item.id)}
            res = client.post(url, data=json.dumps(data),
                              content_type='application/json')

            assert res.status_code == 202

            item = Item.get_record(item.id)
            assert item['_circulation']['status'] == ItemStatus.ON_SHELF


def test_extend_receiver(app, db, access_token):
    """Use the webhooks api to an item loan."""
    item = Item.create({})
    db.session.commit()
    with app.test_request_context():
        with app.test_client() as client:
            url = url_for('invenio_webhooks.event_list',
                          receiver_id='circulation_loan')
            url += '?access_token=' + access_token
            data = {'item_id': str(item.id)}
            res = client.post(url, data=json.dumps(data),
                              content_type='application/json')

            assert res.status_code == 202

            item = Item.get_record(item.id)
            assert item['_circulation']['status'] == ItemStatus.ON_LOAN

            url = url_for('invenio_webhooks.event_list',
                          receiver_id='circulation_extend')
            url += '?access_token=' + access_token
            data = {'item_id': str(item.id),
                    'requested_end_date': datetime.date.today().isoformat()}
            res = client.post(url, data=json.dumps(data),
                              content_type='application/json')

            assert res.status_code == 202

            item = Item.get_record(item.id)
            assert item['_circulation']['status'] == ItemStatus.ON_LOAN
