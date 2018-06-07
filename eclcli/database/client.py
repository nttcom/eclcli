from eclcli.api import eclsdk

DEFAULT_API_VERSION = '1'
API_VERSION_OPTION = ''
API_NAME = 'database'
API_VERSIONS = {
    '1': 'eclcli.database.client.v1',
}


def make_client(instance):
    """Returns a provider connectivity client."""
    client = eclsdk.ConnectionManager()
    return client


def build_option_parser(parser):
    """Hook to add global options"""
    return parser
