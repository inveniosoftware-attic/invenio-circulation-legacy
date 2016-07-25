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

"""Circulation API."""

import uuid
from functools import partial, wraps
from operator import indexOf

from flask import current_app
from invenio_pidstore.errors import PIDInvalidAction
from invenio_records.api import Record

from invenio_circulation.models import ItemStatus


def check_status(method=None, statuses=None):
    """Check that the item has a defined status."""
    if method is None:
        return partial(check_status, statuses=statuses)

    statuses = statuses or []

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Check current deposit status."""
        if self['_circulation']['status'] not in statuses:
            raise PIDInvalidAction()

        return method(self, *args, **kwargs)
    return wrapper


class Holding(dict):
    """Holding class to create and maintain holdings."""

    @classmethod
    def create(cls, id_=None):
        """Create a valid holding."""
        return cls(id=id_ or str(uuid.uuid4()))


class HoldingIterator(object):
    """Data access object to manage holdings associated to an item."""

    def __init__(self, iterable):
        """Initialize iterator."""
        self._iterable = iterable

    def __len__(self):
        """Get number of files."""
        return len(self._iterable)

    def __iter__(self):
        """Get iterator."""
        self._it = iter(self._iterable)
        return self._it

    def next(self):
        """Python 2.7 compatibility."""
        return self.__next__()  # pragma: no cover

    def __next__(self):
        """Get next file item."""
        return next(self._it)   # pragma: no cover

    def __contains__(self, id_):
        """Check if HoldingIterator contains a Holding by id."""
        return id_ in (x['id'] for x in self)

    def __getitem__(self, key):
        """Get a specific file."""
        return self._iterable[key]  # pragma: no cover

    def __setitem__(self, key, obj):
        """Add file inside a deposit."""
        self._iterable[key] = obj   # pragma: no cover

    def __delitem__(self, id_):
        """Delete a Holding by id.

        :raises ValueError:
        """
        index = indexOf((x['id'] for x in self), id_)
        del self._iterable[index]

    def append(self, obj):
        """Append a holding to the end."""
        self._iterable.append(obj)

    def insert(self, index, obj):
        """Insert a holding before given index."""
        self._iterable.insert(index, obj)

    def pop(self, index):
        """Remove and return a holding at index (default is last)."""
        return self._iterable.pop(index)


class Location(Record):
    """Data model to store location information."""

    @classmethod
    def create(cls, data, id_=None):
        """Create a location instance and store it in database."""
        data = data or {}
        schema = current_app.config.get('CIRCULATION_LOCATION_SCHEMA', None)

        if schema:
            ptu = current_app.extensions['invenio-jsonschemas'].path_to_url
            data.setdefault('$schema', ptu(schema))
        return super(Location, cls).create(data, id_=id_)


class Item(Record):
    """Data model to store holding information."""

    @property
    def holdings(self):
        """Property of holdings associated with the given item."""
        return HoldingIterator(self['_circulation']['holdings'])

    @classmethod
    def create(cls, data, id_=None):
        """Create a location instance and store it in database."""
        data = data or {}
        schema = current_app.config.get('CIRCULATION_ITEM_SCHEMA', None)

        if schema:
            ptu = current_app.extensions['invenio-jsonschemas'].path_to_url
            data.setdefault('$schema', ptu(schema))
        if '_circulation' not in data:
            data['_circulation'] = {'status': ItemStatus.ON_SHELF,
                                    'holdings': []}
        if 'holdings' not in data:
            data['_circulation']['holdings'] = []
        if 'status' not in data:
            data['_circulation']['status'] = ItemStatus.ON_SHELF
        return super(Item, cls).create(data, id_=id_)

    @check_status(statuses=[ItemStatus.ON_SHELF])
    def loan_item(self, **kwargs):
        """Loan item to the user.

        Adds a loan to *_circulation.holdings*.

        :param user: Invenio-Accounts user.
        :param start_date: Start date of the loan. Must be today.
        :param end_date: End date of the loan.
        :param waitlist: If the desired dates are not available, the item will
                         be put on a waitlist.
        :param delivery: 'pickup' or 'mail'
        """
        self['_circulation']['status'] = ItemStatus.ON_LOAN
        self.holdings.insert(0, Holding.create())

    @check_status(statuses=[ItemStatus.ON_LOAN,
                            ItemStatus.ON_SHELF])
    def request_item(self, **kwargs):
        """Request item for the user.

        Adds a request to *_circulation.holdings*.

        :param user: Invenio-Accounts user.
        :param start_date: Start date of the loan. Must be today or a future
                           date.
        :param end_date: End date of the loan.
        :param waitlist: If the desired dates are not available, the item will
                         be put on a waitlist.
        :param delivery: 'pickup' or 'mail'
        """
        self.holdings.append(Holding.create())

    @check_status(statuses=[ItemStatus.ON_LOAN])
    def return_item(self):
        """Return given item.

        The item's status will be set to ItemStatus.ON_SHELF.
        """
        self['_circulation']['status'] = ItemStatus.ON_SHELF

        self.holdings.pop(0)

    @check_status(statuses=[ItemStatus.ON_LOAN,
                            ItemStatus.ON_SHELF])
    def lose_item(self):
        """Lose the given item.

        This sets the status to ItemStatus.MISSING.
        All existing holdings will be canceled.
        """
        self['_circulation']['status'] = ItemStatus.MISSING

        for holding in self.holdings:
            self.cancel_hold(holding['id'])

    @check_status(statuses=[ItemStatus.MISSING])
    def return_missing_item(self):
        """Return the missing item.

        The item's status will be set to ItemStatus.ON_SHELF.
        """
        self['_circulation']['status'] = ItemStatus.ON_SHELF

    def cancel_hold(self, id_):
        """Cancel the identified hold.

        The item's corresponding hold information wil be removed.
        This action updates the waitlist.
        """
        del self.holdings[id_]

    @check_status(statuses=[ItemStatus.ON_LOAN])
    def extend_loan(self, requested_end_date=None):
        """Request a new end date for the active loan.

        A possible status ItemStatus.OVERDUE will be removed.
        """
        self['_circulation']['status'] = ItemStatus.ON_LOAN
