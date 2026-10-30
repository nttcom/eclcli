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

"""Security order client"""

import logging

from eclcli.api import eclsdk
from eclcli.common import utils

LOG = logging.getLogger(__name__)

DEFAULT_API_VERSION = '4'
API_VERSION_OPTION = 'os_security_order_api_version'
API_NAME = 'security_order'
API_VERSIONS = {
    '3': 'eclcli.security_order.v3',
    '4': 'eclcli.security_order.v4',
}


def make_client(instance):
    """Returns a security order client."""
    client = eclsdk.ConnectionManager()
    return client


def build_option_parser(parser):
    """Hook to add global options"""
    parser.add_argument(
        '--os-security-order-api-version',
        metavar='<security-order-api-version>',
        default=utils.env('OS_SECURITY_ORDER_API_VERSION'),
        help='Security order API version, default=' +
             DEFAULT_API_VERSION +
             ' (Env: OS_SECURITY_ORDER_API_VERSION)')
    return parser


def check_api_version(check_version):
    if check_version == '3':
        LOG.warning(
            'Security order API v3 is deprecated. Please use v4 instead.')
    return True
