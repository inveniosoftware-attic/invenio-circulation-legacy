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


"""Module minter tests."""

import uuid

import pytest

from invenio_circulation.minters import circulation_item_minter


def test_item_minter(db):
    data1 = {'record': {'control_number': '1'}}
    record_uuid1 = uuid.uuid4()
    pid1 = circulation_item_minter(record_uuid1, data1)

    assert data1['control_number'] == pid1.pid_value

    with pytest.raises(AssertionError):
        circulation_item_minter(uuid.uuid4(), data1)

    data2 = {'record': {'control_number': '1'}}
    record_uuid2 = uuid.uuid4()
    pid2 = circulation_item_minter(record_uuid2, data2)

    assert data2['control_number'] == pid2.pid_value

    assert int(pid1.pid_value) == int(pid2.pid_value) - 1
