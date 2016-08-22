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


"""Pytest configuration."""

from __future__ import absolute_import, print_function

import os
import shutil
import subprocess
import tempfile

import pytest
from click.testing import CliRunner
from elasticsearch.exceptions import RequestError
from flask import Flask
from flask.cli import ScriptInfo
from flask_assets import assets
from flask_babelex import Babel
from flask_breadcrumbs import Breadcrumbs
from flask_menu import Menu
from flask_security.utils import encrypt_password
from invenio_accounts import InvenioAccounts
from invenio_assets import InvenioAssets
from invenio_assets.cli import collect, npm
from invenio_db import db as db_
from invenio_db import InvenioDB
from invenio_indexer import InvenioIndexer
from invenio_jsonschemas import InvenioJSONSchemas
from invenio_oauth2server import InvenioOAuth2Server
from invenio_oauth2server.models import Token
from invenio_oauth2server.views import server_blueprint, settings_blueprint
from invenio_pidstore import InvenioPIDStore
from invenio_records import InvenioRecords
from invenio_records_rest import InvenioRecordsREST
from invenio_records_rest.utils import PIDConverter
from invenio_search import InvenioSearch, current_search, current_search_client
from invenio_webhooks import InvenioWebhooks
from invenio_webhooks.views import blueprint as webhooks_blueprint
from sqlalchemy_utils.functions import create_database, database_exists
from werkzeug.local import LocalProxy

from invenio_circulation import InvenioCirculation, InvenioCirculationREST
from invenio_circulation.bundles import css, js
from invenio_circulation.views.ui import blueprint as circulation_blueprint


@pytest.yield_fixture()
def app(request):
    """Flask application fixture."""
    instance_path = tempfile.mkdtemp()

    app_ = Flask(__name__, instance_path=instance_path)
    app_.config.update(
        OAUTH2SERVER_CLIENT_ID_SALT_LEN=40,
        OAUTH2SERVER_CLIENT_SECRET_SALT_LEN=60,
        OAUTH2SERVER_TOKEN_PERSONAL_SALT_LEN=60,
        SECRET_KEY='changeme',
        SERVER_NAME='localhost:5000',
        REPLACE_REFS=False,
        TESTING=True,
    )

    app_.url_map.converters['pid'] = PIDConverter

    Babel(app_)
    Menu(app_)
    Breadcrumbs(app_)
    InvenioAccounts(app_)
    InvenioDB(app_)
    InvenioIndexer(app_)
    InvenioJSONSchemas(app_)
    InvenioPIDStore(app_)
    InvenioRecords(app_)
    InvenioRecordsREST(app_)
    InvenioWebhooks(app_)
    InvenioOAuth2Server(app_)
    InvenioCirculation(app_)
    InvenioCirculationREST(app_)
    InvenioSearch(app_)

    app_.register_blueprint(server_blueprint)
    app_.register_blueprint(settings_blueprint)
    app_.register_blueprint(webhooks_blueprint)
    app_.register_blueprint(circulation_blueprint)

    with app_.app_context():
        yield app_

    shutil.rmtree(instance_path)


@pytest.yield_fixture()
def db(app):
    """Database fixture."""
    if not database_exists(str(db_.engine.url)):
        create_database(str(db_.engine.url))

    db_.create_all()
    yield db_
    db_.session.remove()
    db_.drop_all()


@pytest.yield_fixture()
def access_token(app, db):
    _datastore = LocalProxy(lambda: app.extensions['security'].datastore)
    kwargs = dict(email='admin@inveniosoftware.org', password='123456',
                  active=True)
    kwargs['password'] = encrypt_password(kwargs['password'])
    user = _datastore.create_user(**kwargs)

    db.session.commit()
    token = Token.create_personal(
        'test-personal-{0}'.format(user.id),
        user.id,
        scopes=['webhooks:event'],
        is_internal=True,
    ).access_token
    db.session.commit()

    yield token


@pytest.yield_fixture()
def es(app):
    """Elasticsearch fixture."""
    try:
        list(current_search.create())
    except RequestError:
        list(current_search.delete(ignore=[404]))
        list(current_search.create(ignore=[400]))
    current_search_client.indices.refresh()
    yield current_search_client
    list(current_search.delete(ignore=[404]))


@pytest.yield_fixture()
def build_assets(app):
    """Get ScriptInfo object for testing CLI."""
    InvenioAssets(app)
    os.chdir(app.instance_path)

    # Register the assets
    _assets = app.extensions['invenio-assets']
    _assets.env.register('invenio_circulation_css', css)
    _assets.env.register('invenio_circulation_js', js)

    # Create static directory if necessary
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

    script_info_assets = ScriptInfo(create_app=lambda info: app)

    # Run `flask npm` to create `package.json`
    runner = CliRunner()
    runner.invoke(npm, obj=script_info_assets)

    # Run `npm install` to install the content of `package.json`
    os.chdir(static_dir)
    subprocess.call(['npm', 'install'])
    os.chdir(os.path.dirname(__file__))

    # Run `flask collect`
    runner.invoke(collect, obj=script_info_assets)

    # Build the bundles
    runner.invoke(assets, ['build'], obj=script_info_assets)

    yield

    # Cleanup
    os.chdir(app.instance_path)
    shutil.rmtree(static_dir)
