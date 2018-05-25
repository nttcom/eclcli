# -*- coding: utf-8 -*-

import copy
from eclcli.common import command
from eclcli.common import utils


class ListDatastore(command.Lister):

    def get_parser(self, prog_name):
        parser = super(ListDatastore, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.database
        columns = [
            'ID',
            'Name',
            'Versions'
        ]
        column_headers = copy.deepcopy(columns)
        data = client.datastores()
        return (column_headers,
                (utils.get_item_properties(d, columns, formatters={
                    'Versions': utils.format_versions}) for d in data))
