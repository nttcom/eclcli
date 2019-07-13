#   Copyright 2012-2013 OpenStack, LLC.
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

import logging

from eclcli.common import utils

LOG = logging.getLogger(__name__)

DEFAULT_API_VERSION = '2'
API_VERSION_OPTION = 'os_monitoring_api_version'
API_NAME = 'monitoring'
API_VERSIONS = {
    "2": "monitoring.client",
}

# Save the microversion if in use
_monitoring_api_version = None


def make_client(instance):
    """Returns a monitoring service client."""

    # Defer client import until we actually need them
    from .monitoringclient import client as monitoring_client

    if _monitoring_api_version is not None:
        version = _monitoring_api_version
    else:
        version = instance._api_version[API_NAME]
    LOG.debug('Instantiating monitoring client for V%s', version)

    # Remember interface only if it is set
    kwargs = utils.build_kwargs_dict('endpoint_type', instance._interface)

    client = monitoring_client.Client(
        version,
        session=instance.session,
        timings=instance.timing,
        region_name=instance._region_name,
        **kwargs
    )
    return client


def build_option_parser(parser):
    """Hook to add global options"""
    return parser


def check_api_version(check_version):
    return True
