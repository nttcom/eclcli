# -*- coding: utf-8 -*-

import json
import copy
import six
from eclcli.common import command
from eclcli.common import utils
from eclcli.i18n import _  # noqa


class ListVirtualNetworkAppliancePlan(command.Lister):

    def get_parser(self, prog_name):
        parser = super(ListVirtualNetworkAppliancePlan, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.virtual_network_appliance

        columns = [
            'ID',
            'Name',
            'Enabled',
            'Number of Interfaces',
            'Max Number of AAP',
        ]
        column_headers = copy.deepcopy(columns)

        data = client.virtual_network_appliance_plans()

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={'Metadata': utils.format_dict},
                ) for s in data))


class ShowVirtualNetworkAppliancePlan(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(ShowVirtualNetworkAppliancePlan, self).\
            get_parser(prog_name)
        parser.add_argument(
            'virtual_network_appliance_plan_id',
            metavar='<virtual-network-appliance-plan-id>',
            help='ID of virtual network appliance plan id to look up.')
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.virtual_network_appliance

        rows = [
            'ID',
            'Name',
            'Appliance Type',
            'Version',
            'Flavor',
            'Number of Interfaces',
            'Max Number of AAP',
            'Enabled',
            'Licenses',
        ]
        row_headers = rows

        data = client.get_virtual_network_appliance_plan(
            parsed_args.virtual_network_appliance_plan_id)

        licenses = data.licenses
        licenses_json = json.dumps(licenses, indent=2)
        setattr(data, 'licenses', licenses_json)

        return (row_headers, (utils.get_item_properties(data, rows)))
