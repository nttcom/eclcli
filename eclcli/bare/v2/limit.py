from eclcli.common import command
from eclcli.bare import bare_utils
from eclcli.common import utils

import six


class ShowLimit(command.ShowOne):
    """Show tenant's limits"""

    def get_parser(self, prog_name):
        parser = super(ShowLimit, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        bare_client = self.app.client_manager.bare
        identity_client = self.app.client_manager.identity

        data = bare_client.limits.get()
        _info = bare_utils._tidy_data_info(data._info)

        return zip(*sorted(six.iteritems(_info)))
