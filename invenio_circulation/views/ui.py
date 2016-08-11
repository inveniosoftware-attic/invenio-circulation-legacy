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

"""Invenio-Circulation interface."""

from flask import Blueprint, render_template

blueprint = Blueprint(
    'circulation',
    __name__,
    url_prefix='/circulation',
    template_folder='../templates',
    static_folder='../static'
)


@blueprint.route('/', methods=['GET'])
def index():
    """Circulation index page."""
    return render_template('invenio_circulation/index.html')
