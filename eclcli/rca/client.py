import logging

from eclcli.common import exceptions
from eclcli.common import utils

LOG = logging.getLogger(__name__)

DEFAULT_API_VERSION = '2'
API_VERSION_OPTION = 'os_rca_api_version'
API_NAME = 'rca'
API_VERSIONS = {
    "2": "rcaclient.client",
}

# Save the microversion if in use
_rca_api_version = None


def make_client(instance):
    """Returns a compute service client."""

    # Defer client import until we actually need them
    from rcaclient.v2 import client as rca_client

    if _rca_api_version is not None:
        version = _rca_api_version
    else:
        version = instance._api_version[API_NAME]

    LOG.debug('Instantiating rca client for V%s', version)

    # Set client http_log_debug to True if verbosity level is high enough
    http_log_debug = utils.get_effective_log_level() <= logging.DEBUG

    # Remember interface only if it is set
    kwargs = utils.build_kwargs_dict('endpoint_type', instance._interface)

    client = rca_client.Client(
        version,
        session=instance.session,
        http_log_debug=http_log_debug,
        timings=instance.timing,
        region_name=instance._region_name,
        **kwargs
    )

    return client


def build_option_parser(parser):
    """Hook to add global options"""
    # parser.add_argument(
    #     '--os-rca-api-version',
    #     metavar='<rca-api-version>',
    #     default=utils.env('OS_RCA_API_VERSION'),
    #     help='RCA API version, default=' +
    #          DEFAULT_API_VERSION +
    #          ' (Env: OS_RCA_API_VERSION)')
    return parser


def check_api_version(check_version):
    return True
