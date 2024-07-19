# -*- coding: utf-8 -*-

try:
    import json
except ImportError:
    import simplejson as json
import copy
from eclcli.common import command
from eclcli.common import utils
from eclcli.i18n import _  # noqa


class ListOperation(command.Lister):
    _description = _("List operations of virtual network appliance")

    def get_parser(self, prog_name):
        parser = super(ListOperation, self).get_parser(prog_name)
        parser.add_argument(
            '--resource_id',
            metavar='<resource uuid>',
            help='Resource ID to query operations [Type: String]')
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.virtual_network_appliance

        columns = [
            'ID',
            'Resource ID',
            'Request Type',
            'Reception Datetime',
            'Commit Datetime',
            'Status',
        ]
        column_headers = copy.deepcopy(columns)

        data = client.operations()

        resource_id = getattr(parsed_args, 'resource_id', None)
        if resource_id:
            data = [datum for datum in data
                    if datum.resource_id == resource_id]

        sorted(data,
               key=lambda datum: datum.reception_datetime,
               reverse=True)

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={'Metadata': utils.format_dict},
                ) for s in data))


class ShowOperation(command.ShowOne):
    _description = _("Show operation of virtual network appliance")

    def get_parser(self, prog_name):
        parser = super(ShowOperation, self).\
            get_parser(prog_name)
        parser.add_argument(
            'operation_id',
            metavar='<operation-id>',
            help='ID of operation id to look up.')
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.virtual_network_appliance

        rows = [
            'ID',
            'Resource ID',
            'Request Type',
            'Status',
            'Reception Datetime',
            'Commit Datetime',
            'Request Body',
            'Warning',
            'Error',
            # 'Error Details',
            'Tenant ID',
            'Resource Type',
        ]
        row_headers = rows

        data = client.get_operation(parsed_args.operation_id)

        if data.request_body:
            req_body = data.request_body
            req_body_dict = json.loads(req_body) if type(req_body) is str else req_body
            setattr(data, 'request_body', json.dumps(req_body_dict, indent=2))

        return row_headers, (utils.get_item_properties(data, rows))
