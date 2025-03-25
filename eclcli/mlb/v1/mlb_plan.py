# -*- coding: utf-8 -*-

try:
    import json
except ImportError:
    import simplejson as json

import copy
from eclcli.common import command, utils
from eclcli.i18n import _  # noqa


class ListPlan(command.Lister):
    _description = _("List plans of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(ListPlan, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        columns = [
            'ID',
            'Name',
            'Bandwidth',
            'Redundancy',
            'Enabled',
            'Max Number of Interfaces',
            'Max Number of Health monitors',
            'Max Number of Listeners',
            'Max Number of Policies',
            'Max Number of Server Name Indications',
            'Max Number of Rules',
            'Max Number of Conditions',
            'Max Number of Routes',
            'Max Number of Target groups',
            'Max Number of Members',
        ]
        column_headers = copy.deepcopy(columns)

        data = client.plans()

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={'Metadata': utils.format_dict},
                ) for s in data))


class ShowPlan(command.ShowOne):
    _description = _("Show plan of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(ShowPlan, self).\
            get_parser(prog_name)
        parser.add_argument(
            'plan_id',
            metavar='<plan-id>',
            help='ID of plan id to look up.')
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        rows = [
            'ID',
            'Name',
            'Bandwidth',
            'Redundancy',
            'Enabled',
            'Max Number of Interfaces',
            'Max Number of Health monitors',
            'Max Number of Listeners',
            'Max Number of Policies',
            'Max Number of Server Name Indications',
            'Max Number of Rules',
            'Max Number of Conditions',
            'Max Number of Routes',
            'Max Number of Target groups',
            'Max Number of Members',
        ]
        row_headers = rows

        data = client.get_plan(
            parsed_args.plan_id)

        return row_headers, (utils.get_item_properties(data, rows))
