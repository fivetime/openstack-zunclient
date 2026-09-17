#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Microversion 1.54's parameters: sent when given, and only then."""

from unittest import mock
from urllib import parse

import testtools

from zunclient import api_versions
from zunclient.v1 import containers


class TestParameters(testtools.TestCase):

    def setUp(self):
        super(TestParameters, self).setUp()
        self.api = mock.Mock()
        self.api.json_request.return_value = (mock.Mock(), None)
        self.mgr = containers.ContainerManager(self.api)
        self.mgr.api_version = api_versions.APIVersion('1.54')

    def _query(self):
        url = self.api.json_request.call_args[0][1]
        return dict(parse.parse_qsl(parse.urlsplit(url).query))

    def test_stop_signal(self):
        self.mgr.stop('c', 5, signal='SIGINT')
        self.assertEqual({'timeout': '5', 'signal': 'SIGINT'}, self._query())
        self.mgr.stop('c', 5)
        self.assertEqual({'timeout': '5'}, self._query())

    def test_put_archive_options(self):
        self.mgr.put_archive('c', '/x', b'd', copy_uidgid=True,
                             no_overwrite_dir_non_dir=True)
        self.assertEqual({'path': '/x', 'copy_uidgid': 'true',
                          'no_overwrite_dir_non_dir': 'true'}, self._query())
        self.mgr.put_archive('c', '/x', b'd')
        self.assertEqual({'path': '/x'}, self._query())

    def test_commit_options(self):
        self.mgr.commit('c', 'r/app', '1', message='m', author='a',
                        changes=['ENV A=1', 'CMD ["sh"]'], pause=False)
        self.assertEqual({'repository': 'r/app', 'tag': '1', 'message': 'm',
                          'author': 'a', 'changes': 'ENV A=1\nCMD ["sh"]',
                          'pause': 'false'}, self._query())
        self.mgr.commit('c', 'r/app')
        self.assertEqual({'repository': 'r/app'}, self._query())

    def test_create_takes_the_1_54_fields_it_needs(self):
        self.assertIn('environment', containers.CREATION_ATTRIBUTES)
