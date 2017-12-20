#   Copyright 2013 Nebula Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

"""Provider connectivity client"""

from eclcli.api import eclsdk

DEFAULT_API_VERSION = '1'
API_VERSION_OPTION = ''
API_NAME = 'provider_connectivity'
API_VERSIONS = {
    '1': 'eclcli.provider_connectivity.client.v1',
}


def make_client(instance):
    """Returns a provider connectivity client."""
    client = eclsdk.ConnectionManager()
    return client


def build_option_parser(parser):
    """Hook to add global options"""
    return parser
