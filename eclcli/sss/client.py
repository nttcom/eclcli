import logging

from ecl import connection

from eclcli.common import utils


LOG = logging.getLogger(__name__)

DEFAULT_API_VERSION = '1'
API_VERSION_OPTION = 'os_sss_api_version'
API_NAME = "sss"
API_VERSIONS = {
    "1": "sssclient.v1.client.Client",
}


def make_client(instance):
    """Returns a network proxy"""
    from sssclient.v1 import client as sss_client
    c = sss_client.Client(session=instance.session)
    return c


def build_option_parser(parser):
    """Hook to add global options"""
    # parser.add_argument(
    #     '--os-sss-api-version',
    #     metavar='<sss-api-version>',
    #     default=utils.env('OS_SSS_API_VERSION'),
    #     help='SSS API version, default=' +
    #          DEFAULT_API_VERSION +
    #          ' (Env: OS_SSS_API_VERSION)')
    return parser
