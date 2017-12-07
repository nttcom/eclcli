import logging

from eclcli.common import utils

LOG = logging.getLogger(__name__)

DEFAULT_API_VERSION = '2'
API_VERSION_OPTION = 'os_dns_api_version'
API_NAME = "dns"
API_VERSIONS = {
    "2": "dnsclient.client"
}


def make_client(instance):
    pass


def build_option_parser(parser):
    # parser.add_argument(
    #     '--os-storage-api-version',
    #     metavar='<storage-api-version>',
    #     default=utils.env('OS_STORAGE_API_VERSION'),
    #     help='Storage API version, default=' +
    #          DEFAULT_API_VERSION +
    #          ' (Env: OS_STORAGE_API_VERSION)')
    return parser
