import logging

from eclcli.common import utils

LOG = logging.getLogger(__name__)


DEFAULT_API_VERSION = '2'
API_VERSION_OPTION = 'os_iam_api_version'
API_NAME = "iam"
API_VERSIONS = {
    "2": "iamclient.v2.client.Client",
}

_iam_api_version = None


def make_client(instance):
    from eclcli.sss.sssclient.v2 import client as iam_client

    if _iam_api_version is not None:
        version = _iam_api_version
    else:
        version = instance._api_version[API_NAME]

    LOG.debug('Instantiating iam client for V%s', version)

    # Set client http_log_debug to True if verbosity level is high enough
    http_log_debug = utils.get_effective_log_level() <= logging.DEBUG

    # Remember interface only if it is set
    kwargs = utils.build_kwargs_dict('endpoint_type', instance._interface)

    client = iam_client.Client(
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
    return parser


def check_api_version(check_version):
    return True
