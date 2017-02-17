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

import argparse
import logging

from eclcli.orchestration.heatclient.openstack.common._i18n import _


from eclcli.common import utils

LOG = logging.getLogger(__name__)

DEFAULT_ORCHESTRATION_API_VERSION = '1'
API_VERSION_OPTION = 'os_orchestration_api_version'
API_NAME = 'orchestration'
API_VERSIONS = {
    '1': 'eclcli.orchestration.heatclient.v1.client.Client',
}


def make_client(instance):
    """Returns an orchestration service client"""
    heat_client = utils.get_client_class(
        API_NAME,
        instance._api_version[API_NAME],
        API_VERSIONS)
    LOG.debug('Instantiating orchestration client: %s', heat_client)

    cli_args = instance._cli_options
    endpoint = cli_args.heat_url if cli_args.heat_url \
        else instance.get_endpoint_for_service_type(API_NAME)

    client = heat_client(
        endpoint=endpoint,
        # endpoint=instance.get_endpoint_for_service_type('orchestration'),
        session=instance.session,
        auth_url=instance._auth_url,
        username=instance._username,
        password=instance._password,
        region_name=instance._region_name,
    )

    return client


def build_option_parser(parser):
    parser.add_argument('--heat-url',
                        default=utils.env('HEAT_URL'),
                        help=_('Defaults to %(value)s.') % {
                            'value': 'env[HEAT_URL]'
                        })
    parser.add_argument('--heat_url',
                        help=argparse.SUPPRESS)
    return parser
