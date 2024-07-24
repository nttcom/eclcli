# -*- coding: utf-8 -*-

try:
    import json
except ImportError:
    import simplejson as json

import copy
from eclcli.common import command, utils
from eclcli.i18n import _  # noqa


class ListSystemUpdate(command.Lister):
    _description = _("List system-updates of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(ListSystemUpdate, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        columns = [
            'ID',
            'Name',
            'Href',
            'Publish Datetime',
            'Limit Datetime',
            'Current Revision',
            'Next Revision',
            'Applicable',
        ]
        column_headers = copy.deepcopy(columns)

        data = client.system_updates()

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={'Metadata': utils.format_dict},
                ) for s in data))


class ShowSystemUpdate(command.ShowOne):
    _description = _("Show system-update of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(ShowSystemUpdate, self).\
            get_parser(prog_name)
        parser.add_argument(
            'system_update_id',
            metavar='<system-update-id>',
            help='ID of system update id to look up.')
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        rows = [
            'ID',
            'Name',
            'Href',
            'Publish Datetime',
            'Limit Datetime',
            'Current Revision',
            'Next Revision',
            'Applicable',
        ]
        row_headers = rows

        data = client.get_system_update(parsed_args.system_update_id)

        return row_headers, (utils.get_item_properties(data, rows))
