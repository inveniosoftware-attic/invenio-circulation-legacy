# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Invenio circulation configuration file."""


CIRCULATION_EMAIL_SENDER = None
CIRCULATION_LOAN_PERIOD = 28

CIRCULATION_LOCATION_SCHEMA = 'circulation/location-v1.0.0.json'
CIRCULATION_ITEM_SCHEMA = 'circulation/item/default-v1.0.0.json'

CIRCULATION_DATE_FORMAT = '%Y-%m-%d'
"""Datetime format used to parse date strings."""

CIRCULATION_REST_ENDPOINTS = {
    'crcitm': {
        'pid_type': 'crcitm',
        'pid_minter': 'circulation_item',
        'pid_fetcher': 'circulation_item',
        'record_class': 'invenio_circulation.api:Item',
        'record_serializers': {
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_response'),
        },
        'search_class': 'invenio_circulation.search:ItemSearch',
        'search_index': None,
        'search_type': None,
        'search_serializers': {
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_search'),
        },
        'list_route': '/circulation/items/',
        'item_route': '/circulation/items/<pid(crcitm):pid_value>',
        'default_media_type': 'application/json',
        'max_result_window': 10000,
    }
}
"""Basic REST circulation configuration."""

CIRCULATION_ITEM_SEARCH_API = '/circulation/items/'
"""Configure the item search engine endpoint."""

CIRCULATION_USER_SEARCH_API = '/users/'
"""Configure the user search engine endpoint."""
