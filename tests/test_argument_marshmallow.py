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


"""Module argument marshmallowing tests."""

import datetime
import uuid

import pytest
from marshmallow import ValidationError

from invenio_circulation.validators import CancelArgument, ExtensionArgument, \
    LoanArgument, RequestArgument, validate


@pytest.mark.parametrize('argument_schema', [LoanArgument, RequestArgument])
def test_marshmallow_loan_request(app, argument_schema):
    """Loan and request argument validation using marshmallow schema."""
    CLP = app.config['CIRCULATION_LOAN_PERIOD']

    # Validate empty arguments
    assert not validate(argument_schema(), {})

    # Check the default value behavior
    defaults = argument_schema().dump({}).data
    assert defaults['start_date'] == datetime.date.today()
    assert defaults['end_date'] == (datetime.date.today() +
                                    datetime.timedelta(days=CLP))
    assert defaults['waitlist'] is False
    assert defaults['delivery'] == 'mail'

    # Test correct arguments
    arguments = {'start_date': datetime.date.today(),
                 'end_date': datetime.date.today(),
                 'waitlist': False,
                 'delivery': 'mail',
                 }
    assert not validate(argument_schema(), arguments)

    # Test correct arguments with dates in isoformat
    arguments = {'start_date': datetime.date.today().isoformat(),
                 'end_date': datetime.date.today().isoformat(),
                 'waitlist': False,
                 'delivery': 'mail',
                 }
    assert not validate(argument_schema(), arguments)

    # Test correct arguments with dates as datetime.datetime
    arguments = {'start_date': datetime.datetime.now(),
                 'end_date': datetime.datetime.now(),
                 }
    assert not validate(argument_schema(), arguments)

    # Test correct arguments with dates as datetime.datetime in isoformat
    arguments = {'start_date': datetime.datetime.now().isoformat(),
                 'end_date': datetime.datetime.now().isoformat(),
                 }
    assert not validate(argument_schema(), arguments)

    # Test incorrect arguments
    arguments = {'start_date': 'foo',
                 'end_date': 'bar',
                 'waitlist': 'baz',
                 'delivery': 'quux',
                 }
    with pytest.raises(ValidationError):
        validate(argument_schema(), arguments)


def test_marshmallow_cancel(app):
    """Cancel argument validation using marshmallow schema."""

    # Validate empty arguments fail
    with pytest.raises(ValidationError):
        validate(CancelArgument(), {})

    # Validate given uuid
    assert not validate(CancelArgument(), {'id': uuid.uuid4()})

    # Validate given uuid as string
    assert not validate(CancelArgument(), {'id': str(uuid.uuid4())})


def test_marshmallow_extend_loan(app):
    """Extend Loan argument validation using marshmallow schema."""
    CLP = app.config['CIRCULATION_LOAN_PERIOD']

    # Validate empty arguments
    assert not validate(ExtensionArgument(), {})

    # Check the default value behavior
    defaults = ExtensionArgument().dump({}).data
    assert defaults['requested_end_date'] == (
            datetime.date.today() + datetime.timedelta(days=CLP))

    # Check date
    arguments = {'requested_end_date': datetime.date.today()}
    assert not validate(ExtensionArgument(), arguments)

    arguments = {'requested_end_date': datetime.date.today().isoformat()}
    assert not validate(ExtensionArgument(), arguments)
