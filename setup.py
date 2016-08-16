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

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()
history = open('CHANGES.rst').read()

tests_require = [
    'check-manifest>=0.25',
    'coverage>=4.0',
    'isort>=4.2.2',
    'psycopg2>=2.6.1',
    'pydocstyle>=1.0.0',
    'pytest-cache>=1.0',
    'pytest-cov>=1.8.0',
    'pytest-pep8>=1.0.6',
    'pytest>=2.9.2',
]

extras_require = {
    'docs': [
        'Sphinx>=1.4.2',
    ],
    'tests': tests_require,
}

extras_require['all'] = []
for reqs in extras_require.values():
    extras_require['all'].extend(reqs)

setup_requires = [
    'Babel>=1.3',
    'pytest-runner>=2.6.2',
]

install_requires = [
    'Flask-BabelEx>=0.9.2',
    'invenio-assets>=1.0.0b1',
    'invenio-db>=1.0.0a9',
    'invenio-indexer>=1.0.0a6',
    'invenio-jsonschemas>=1.0.0a3',
    'invenio-marc21>=1.0.0a3',
    'invenio-pidstore>=1.0.0a7',
    'invenio-records>=1.0.0a15',
    'invenio-records-rest>=1.0.0a15',
    'invenio-search>=1.0.0a7',
    'invenio-webhooks>=1.0.0a2',
    'jsmin>=2.2.1',
    'python-slugify>=1.2.0',
]

packages = find_packages()

# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('invenio_circulation', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='invenio-circulation',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    keywords='invenio circulation holdings library ILS',
    license='GPLv2',
    author='CERN',
    author_email='info@inveniosoftware.org',
    url='https://github.com/inveniosoftware/invenio-circulation',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'invenio_base.apps': [
            'invenio_circulation = invenio_circulation:InvenioCirculation',
        ],
        'invenio_base.api_apps': [
            'invenio_circulation_rest'
            ' = invenio_circulation:InvenioCirculationREST',
        ],
        'invenio_i18n.translations': [
            'messages = invenio_circulation',
        ],
        'invenio_pidstore.minters': [
            '{0} = invenio_circulation.minters:{0}_minter'.format(x)
            for x in ['circulation_item', 'circulation_location']
        ],
        'invenio_pidstore.fetchers': [
            '{0} = invenio_circulation.fetchers:{0}_fetcher'.format(x)
            for x in ['circulation_item']
        ],
        'invenio_jsonschemas.schemas': [
            'circulation = invenio_circulation.schemas',
        ],
        'invenio_webhooks.receivers': [
            'circulation_{0} = invenio_circulation.receivers:{1}Receiver'
            .format(x, y)
            for x, y in [('loan', 'Loan'), ('request', 'Request'),
                         ('return', 'Return'), ('lose', 'Lose'),
                         ('return_missing', 'ReturnMissing'),
                         ('cancel', 'Cancel'), ('extend', 'Extend')]
        ],
        'invenio_search.mappings': [
            'circulation = invenio_circulation.mappings',
        ],
        'invenio_assets.bundles': [
            'invenio_circulation_css = invenio_circulation.bundles:css',
            'invenio_circulation_js = invenio_circulation.bundles:js',
        ],
        'invenio_base.blueprints': [
            'circulation = invenio_circulation.views.ui:blueprint'
        ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Development Status :: 1 - Planning',
    ],
)
