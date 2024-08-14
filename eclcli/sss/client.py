import logging


LOG = logging.getLogger(__name__)

DEFAULT_API_VERSION = '2'
API_VERSION_OPTION = 'os_sss_api_version'
API_NAME = "sss"
API_VERSIONS = {
    "2": "sssclient.v2.client.Client",
}


def make_client(instance):
    """Returns a network proxy"""
    from .sssclient.v2 import client as sss_client
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
