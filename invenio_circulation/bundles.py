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

"""Bundles for Invenio-Circulation."""

from flask_assets import Bundle
from invenio_assets import NpmBundle

css = Bundle(
    'node_modules/angular-ui-bootstrap/dist/ui-bootstrap-csp.css',
    'css/circulation/app.css',
    filters='cleancss',
    output='gen/circulation.%(version)s.css',
)

js = NpmBundle(
    'node_modules/requirejs/require.js',
    'node_modules/angular/angular.js',
    'node_modules/invenio-search-js/dist/invenio-search-js.js',
    'node_modules/angular-ui-bootstrap/dist/ui-bootstrap.js',
    'js/circulation/app.js',
    'js/circulation/directives/circulationUserSearch.js',
    filters='requirejs',
    output='gen/circulation.%(version)s.js',
    npm={
        'requirejs': '~2.3.1',
        'angular': '~1.4.8',
        'angular-ui-bootstrap': '~2.1.4',
        'invenio-search-js': '~0.2.0',
    }
)
