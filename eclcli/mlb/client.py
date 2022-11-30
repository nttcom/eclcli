import logging

LOG = logging.getLogger(__name__)

DEFAULT_API_VERSION = '1'
API_VERSION_OPTION = 'os_mlb_api_version'
API_NAME = "mlb"


def build_option_parser(parser):
    return parser