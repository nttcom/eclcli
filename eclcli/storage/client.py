import logging

from eclcli.common import utils

LOG = logging.getLogger(__name__)

DEFAULT_API_VERSION = '2'
API_VERSION_OPTION = 'os_storage_api_version'
API_NAME = "storage"
API_VERSIONS = {
    "2": "storageclient.v2.client.Client"
}


def make_client(instance):
    from storageclient.v2 import client as storage_client

    http_log_debug = utils.get_effective_log_level() <= logging.DEBUG
    kwargs = utils.build_kwargs_dict('endpoint_type', instance._interface)

    client = storage_client.Client(
        session=instance.session,
        http_log_debug=http_log_debug,
        **kwargs
    )

    return client


def build_option_parser(parser):
    # parser.add_argument(
    #     '--os-storage-api-version',
    #     metavar='<storage-api-version>',
    #     default=utils.env('OS_STORAGE_API_VERSION'),
    #     help='Storage API version, default=' +
    #          DEFAULT_API_VERSION +
    #          ' (Env: OS_STORAGE_API_VERSION)')
    return parser
