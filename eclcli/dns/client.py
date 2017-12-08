import logging

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
    return parser
