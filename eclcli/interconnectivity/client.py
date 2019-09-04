import logging


LOG = logging.getLogger(__name__)

DEFAULT_API_VERSION = '1'
API_VERSION_OPTION = 'os_interconnectivity_api_version'
API_NAME = "interconnectivity"
API_VERSIONS = {
    "1": "interconnectivityclient.v1.client.Client",
}


def make_client(instance):
    """Returns a network proxy"""
    from .interconnectivityclient.v1 import client as interconnectivity_client
    c = interconnectivity_client.Client(session=instance.session)
    return c


def build_option_parser(parser):
    return parser
