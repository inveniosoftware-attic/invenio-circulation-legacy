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

"""Invenio-Circulation REST interface."""

from flask import Blueprint, abort
from invenio_records_rest.utils import obj_or_import_string
from invenio_records_rest.views import \
    create_url_rules as records_rest_url_rules
from invenio_rest import ContentNegotiatedMethodView


def create_blueprint(endpoints):
    """Create invenio-circulation REST blueprint."""
    blueprint = Blueprint(
        'circulation_rest',
        __name__,
        static_folder='./static',
        template_folder='./templates',
        url_prefix='',
    )

    for endpoint, options in endpoints.items():
        for rule in records_rest_url_rules(endpoint, **options):
            blueprint.add_url_rule(**rule)

    return blueprint
