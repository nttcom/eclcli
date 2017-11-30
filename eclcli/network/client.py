import logging

from ecl import connection

from eclcli.common import utils


LOG = logging.getLogger(__name__)

DEFAULT_API_VERSION = '2.0'
API_VERSION_OPTION = 'os_network_api_version'
API_NAME = "network"
API_VERSIONS = {
    "2.0": "openstack.connection.Connection",
    "2": "openstack.connection.Connection",
}


def make_client(instance):
    from networkclient.v2 import client as network_client
    c = network_client.Client(session=instance.session)
    return c


def build_option_parser(parser):
    # parser.add_argument(
    #     '--os-network-api-version',
    #     metavar='<network-api-version>',
    #     default=utils.env('OS_NETWORK_API_VERSION'),
    #     help='Network API version, default=' +
    #          DEFAULT_API_VERSION +
    #          ' (Env: OS_NETWORK_API_VERSION)')
    return parser
