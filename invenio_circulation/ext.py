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

"""Invenio module for the circulation of bibliographic items."""

from __future__ import absolute_import, print_function

from . import config
from .views import rest


class InvenioCirculation(object):
    """Invenio-Circulation extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions['invenio-circulation'] = self

    def init_config(self, app):
        """Initialize configuration."""
        app.config.setdefault(
            'CIRCULATION_BASE_TEMPLATE',
            app.config.get('BASE_TEMPLATE',
                           'invenio_circulation/base.html'))

        for k in dir(config):
            if k.startswith('CIRCULATION_'):
                app.config.setdefault(k, getattr(config, k))


class InvenioCirculationREST(InvenioCirculation):
    """Invenio-Circulation extension."""

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.register_blueprint(rest.create_blueprint(
            app.config['CIRCULATION_REST_ENDPOINTS']
        ))
        app.config['RECORDS_REST_ENDPOINTS'].update(
            app.config['CIRCULATION_REST_ENDPOINTS']
        )
        app.extensions['invenio-circulation-rest'] = self
