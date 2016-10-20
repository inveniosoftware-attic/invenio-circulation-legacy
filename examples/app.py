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


"""Minimal Flask application example for development.

Run example development server:

.. code-block:: console

   $ cd examples
   $ flask -a app.py --debug run
"""

from __future__ import absolute_import, print_function

import os

from flask import Flask, cli
from flask_babelex import Babel
from flask_breadcrumbs import Breadcrumbs
from flask_menu import Menu
from invenio_accounts import InvenioAccounts
from invenio_accounts.views import blueprint as accounts_blueprint
from invenio_accounts_rest import InvenioAccountsREST
from invenio_assets import InvenioAssets
from invenio_db import InvenioDB
from invenio_indexer import InvenioIndexer
from invenio_jsonschemas import InvenioJSONSchemas
from invenio_oauth2server import InvenioOAuth2Server, InvenioOAuth2ServerREST
from invenio_oauth2server.views import server_blueprint, settings_blueprint
from invenio_pidstore import InvenioPIDStore
from invenio_records import InvenioRecords
from invenio_records_rest import InvenioRecordsREST
from invenio_records_rest.utils import PIDConverter
from invenio_search import InvenioSearch
from invenio_webhooks import InvenioWebhooks
from invenio_webhooks.views import blueprint as webhooks_blueprint
from werkzeug.wsgi import DispatcherMiddleware

from invenio_circulation import InvenioCirculation, InvenioCirculationREST
from invenio_circulation.views.ui import blueprint as circulation_blueprint


# Create Flask application
def init_app(app):
    app.url_map.converters['pid'] = PIDConverter
    app.config.update(
        SQLALCHEMY_DATABASE_URI=os.getenv(
            'SQLALCHEMY_DATABASE_URI', 'postgresql+psycopg2://localhost/app'),
        OAUTH2SERVER_CLIENT_ID_SALT_LEN=40,
        OAUTH2SERVER_CLIENT_SECRET_SALT_LEN=60,
        OAUTH2SERVER_TOKEN_PERSONAL_SALT_LEN=60,
        SECRET_KEY='changeme',
        CIRCULATION_ACTION_LOAN_URL=(
            '/hooks/receivers/circulation_loan/events/'),
        CIRCULATION_ACTION_REQUEST_URL=(
            '/hooks/receivers/circulation_request/events/'),
        CIRCULATION_ACTION_RETURN_URL=(
            '/hooks/receivers/circulation_return/events/'),
        CIRCULATION_ACTION_EXTEND_URL=(
            '/hooks/receivers/circulation_extend/events/'),
        CIRCULATION_ACTION_LOSE_URL=(
            '/hooks/receivers/circulation_lose/events/'),
        CIRCULATION_ACTION_CANCEL_URL=(
            '/hooks/receivers/circulation_cancel/events/'),
    )

    Babel(app)
    Menu(app)
    Breadcrumbs(app)
    InvenioAccounts(app)
    InvenioAssets(app)
    InvenioDB(app)
    InvenioSearch(app)
    InvenioIndexer(app)
    InvenioJSONSchemas(app)
    InvenioPIDStore(app)
    InvenioRecords(app)
    InvenioWebhooks(app)
    InvenioOAuth2Server(app)
    InvenioCirculation(app)

api_app = Flask('api_' + __name__)
api_app.config.update(
    APPLICATION_ROOT='/api',
    ACCOUNTS_REGISTER_BLUEPRINT=False
)
init_app(api_app)
InvenioOAuth2ServerREST(api_app)
InvenioAccountsREST(api_app)
InvenioRecordsREST(api_app)
InvenioCirculationREST(api_app)

app = Flask(__name__)
init_app(app)

app.register_blueprint(server_blueprint)
app.register_blueprint(accounts_blueprint)
app.register_blueprint(settings_blueprint)
app.register_blueprint(webhooks_blueprint)
app.register_blueprint(circulation_blueprint)

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/api': api_app.wsgi_app
})


@app.cli.group()
def fixtures():
    """Command for working with test data."""


@fixtures.command()
@cli.with_appcontext
def items():
    """Create circulation items."""
    from invenio_db import db
    from invenio_indexer.api import RecordIndexer

    from invenio_circulation.api import Item
    from invenio_circulation.minters import circulation_item_minter

    for x in range(10):
        item = Item.create({
            'foo': 'bar{0}'.format(x),
            'title_statement': {'title': 'title{0}'.format(x)},
            'record': {'id': 1}
        })
        circulation_item_minter(item.id, item)
        item.commit()
        record_indexer = RecordIndexer()
        record_indexer.index(item)

    db.session.commit()


@fixtures.command()
@cli.with_appcontext
def user():
    """Create circulation admin user."""
    from werkzeug.local import LocalProxy
    from flask_security.utils import encrypt_password

    from invenio_db import db
    from invenio_oauth2server.models import Token

    _datastore = LocalProxy(lambda: app.extensions['security'].datastore)
    kwargs = dict(
        email='circulation_admin@inveniosoftware.org',
        password='123456',
        active=True
    )
    kwargs['password'] = encrypt_password(kwargs['password'])
    user = _datastore.create_user(**kwargs)

    Token.create_personal(
        'test-personal-{0}'.format(user.id),
        user.id,
        scopes=['webhooks:event'],
        is_internal=True,
    ).access_token

    db.session.commit()
