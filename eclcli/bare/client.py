import logging

from eclcli.common import utils

LOG = logging.getLogger(__name__)

DEFAULT_API_VERSION = '2'
API_VERSION_OPTION = 'os_bare_api_version'
API_NAME = 'bare'
API_VERSIONS = {
    "2": "bareclient.client",
}

# Save the microversion if in use
_bare_api_version = None


def make_client(instance):
    """Returns a compute service client."""

    # Defer client import until we actually need them
    from .bareclient import client as bare_client

    if _bare_api_version is not None:
        version = _bare_api_version
    else:
        version = instance._api_version[API_NAME]

    LOG.debug('Instantiating bare client for V%s', version)

    # Set client http_log_debug to True if verbosity level is high enough
    http_log_debug = utils.get_effective_log_level() <= logging.DEBUG

    # Remember interface only if it is set
    kwargs = utils.build_kwargs_dict('endpoint_type', instance._interface)

    client = bare_client.Client(
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
    #     '--os-bare-api-version',
    #     metavar='<bare-api-version>',
    #     default=utils.env('OS_BARE_API_VERSION'),
    #     help='Bare API version, default=' +
    #          DEFAULT_API_VERSION +
    #          ' (Env: OS_BARE_API_VERSION)')
    return parser


def check_api_version(check_version):
    return True
