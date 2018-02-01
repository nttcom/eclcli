import logging

from eclcli.common import utils

LOG = logging.getLogger(__name__)

DEFAULT_API_VERSION = '1'
API_VERSION_OPTION = 'os_vnf_api_version'
API_NAME = "vnf"


def build_option_parser(parser):
    # parser.add_argument(
    #     '--os-storage-api-version',
    #     metavar='<storage-api-version>',
    #     default=utils.env('OS_STORAGE_API_VERSION'),
    #     help='Storage API version, default=' +
    #          DEFAULT_API_VERSION +
    #          ' (Env: OS_STORAGE_API_VERSION)')
    return parser
