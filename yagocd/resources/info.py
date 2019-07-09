#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# The MIT License
#
# Copyright (c) 2016 Grigory Chernyshev
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

import re
from distutils.version import LooseVersion

from easydict import EasyDict
# noinspection PyUnresolvedReferences
from six.moves import html_parser

from yagocd.resources import BaseManager
from yagocd.util import since


@since('19.5.0')
class InfoManager(BaseManager):
    """
    Class for getting general information about GoCD server.
    Mostly this class returns some system information about the
    server and not assumed to be used often.

    :versionadded: 19.5.0.

    Right now this class just parses /about page, for more robust approach
    you can use yagocd.resources.version.VersionManager class.
    """

    VERSION_NUMBER_RE = re.compile(r'[\d.-]+')

    def __init__(self, session):
        super(InfoManager, self).__init__(session)
        self._parsed = None

    def _get_about_page(self):
        result = self._session.get(
            path='go/about',
            headers={'Accept': 'text/html'}
        )
        return result.text

    def _get_server_info(self):
        about_page = BeautifulSoup(self._get_about_page())
        server_info = json.loads(about_page.body.attrs['data-meta'])
        self.go_server_version = server_info['go_server_version']
        self.jvm_version = server_info['jvm_version']
        self.os_info = server_info['os_information']
        self.artifact_free_space = server_info['usable_space_in_artifacts_repository']
        self.db_schema_version = server_info['database_schema_version']

        return server_info

    @property
    def version(self):
        version_match = self.VERSION_NUMBER_RE.match(self.go_server_version)
        if version_match:
            return version_match.group()

    def support(self):
        """
        Method for getting different server support information.
        """
        response = self._session.get(
            path='{base_api}/support'.format(base_api=self.base_api),
            headers={
                'Accept': 'application/json',
            },
        )

        if LooseVersion(self._session.server_version) <= LooseVersion('16.3.0'):
            return response.text

        return EasyDict(response.json())

    def process_list(self):
        """
        Method for getting processes, executed by server.
        """
        response = self._session.get(
            path='{base_api}/process_list'.format(base_api=self.base_api),
            headers={
                'Accept': 'application/json',
            },
        )

        return EasyDict(response.json())
