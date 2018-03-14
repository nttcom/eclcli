# -*- coding: utf-8 -*-

import copy
import six
from eclcli.common import command
from eclcli.common import utils


class ListAddressAssignment(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListAddressAssignment,
                       self).get_parser(prog_name)
        parser.add_argument(
            'tenant_connection_request_id',
            metavar='<TENANT CONNECTION REQUEST ID>',
            help='Tenant connection request ID of address assignments',
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.provider_connectivity
        request_id = parsed_args.tenant_connection_request_id

        columns = [
            'ID',
            'Request ID',
            'Tenant Connection ID',
            'Mac Address',
            'Network ID',
            'Fixed IPs',
            'Allowed Address Pairs',
          ]
        column_headers = copy.deepcopy(columns)

        data = client.address_assignments(request_id)

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowICCNetwork(command.ShowOne):
    """Display details"""

    def get_parser(self, prog_name):
        parser = super(ShowICCNetwork,
                       self).get_parser(prog_name)
        parser.add_argument(
            'tenant_connection_request_id',
            metavar='<TENANT CONNECTION REQUEST ID>',
            help='Tenant connection request ID of network',
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.provider_connectivity

        data = client.get_icc_network(
            parsed_args.tenant_connection_request_id)._body

        return zip(*sorted(six.iteritems(data)))


class ListICCSubnet(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListICCSubnet,
                       self).get_parser(prog_name)
        parser.add_argument(
            'tenant_connection_request_id',
            metavar='<TENANT CONNECTION REQUEST ID>',
            help='Tenant connection request ID of subnets to display',
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.provider_connectivity
        request_id = parsed_args.tenant_connection_request_id

        columns = [
            'ID',
            'Name',
            'Description',
            'Network ID',
            'CIDR',
            'Gateway IP',
            'Status',
          ]
        column_headers = copy.deepcopy(columns)

        data = client.icc_subnets(request_id)

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowICCSubnet(command.ShowOne):
    """Display details"""

    def get_parser(self, prog_name):
        parser = super(ShowICCSubnet,
                       self).get_parser(prog_name)
        parser.add_argument(
            'tenant_connection_request_id',
            metavar='<TENANT CONNECTION REQUEST ID>',
            help='Tenant connection request ID of network',
        )
        parser.add_argument(
            'subnet_id',
            metavar='<Subnet ID>',
            help='ID of subnet to display',
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.provider_connectivity

        data = client.get_icc_subnet(
            parsed_args.tenant_connection_request_id,
            parsed_args.subnet_id
        )._body

        return zip(*sorted(six.iteritems(data)))