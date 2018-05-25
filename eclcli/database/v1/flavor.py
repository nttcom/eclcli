# -*- coding: utf-8 -*-

import copy
from eclcli.common import command
from eclcli.common import utils


class ListFlavor(command.Lister):

    def get_parser(self, prog_name):
        parser = super(ListFlavor, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.database
        columns = [
            'Name',
            'vCPUs',
            'RAM',
            'Disk',
        ]
        column_headers = copy.deepcopy(columns)
        data = client.flavors()
        return (column_headers,
                (utils.get_item_properties(d, columns) for d in data))
