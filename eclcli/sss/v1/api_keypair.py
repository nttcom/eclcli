# -*- coding: utf-8 -*-

from eclcli.common import command
from eclcli.common import exceptions
from eclcli.common import utils
from eclcli.identity import common as identity_common
from ..sssclient.common.utils import objectify


class SetAPIKeypair(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(SetAPIKeypair, self).get_parser(prog_name)
        parser.add_argument(
            'user_id',
            metavar="<uuid>",
            help=(""),
        )
        return parser

    def take_action(self, parsed_args):
        sss_client = self.app.client_manager.sss
        user_id    = parsed_args.user_id
        keypair    = sss_client.set_api_keypair(user_id)
        columns    = utils.get_columns(keypair)
        obj        = objectify(keypair)
        data       = utils.get_item_properties(obj, columns)
        return (columns, data)

