# -*- coding: utf-8 -*-

from eclcli.common import command
from eclcli.common import exceptions
from eclcli.common import utils
from eclcli.identity import common as identity_common
from ..sssclient.common.utils import objectify


class ListChannel(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListChannel, self).get_parser(prog_name)
        parser.add_argument(
            'get_contracts',
            metavar="<boolean>",
            type=utils.parse_bool,
            choices=[True, False],
            help=("The flag of whether getting contracts(true or false(default)).")
        )
        return parser

    def take_action(self, parsed_args):
        sss_client = self.app.client_manager.sss

        columns = (
            'channel_id',
            'channel_name',
            'language',
            'management_channel',
            'parent_channel_id',
            'contracts',
        )
        column_headers = (
            'Channel ID',
            'Channel NAME',
            'Language',
            'Management Channel',
            'Parent Channel ID',
            'Contracts',
        )

        get_contracts = str(parsed_args.get_contracts).lower() # TODO ちゃんと書く
        data = [objectify(user)
            for user in sss_client.list_channels(get_contracts).get('channels')]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={'contracts': utils.format_lister}
                ) for s in data))
