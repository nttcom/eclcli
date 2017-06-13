from eclcli.common import command
from eclcli.common import utils
from ..networkclient.common import utils as to_obj


class ListFirewallInterface(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListFirewallInterface, self).get_parser(prog_name)

        parser.add_argument(
            '--firewall_id',
            metavar="firewall_id",
            help="filter by firewall id")
        parser.add_argument(
            '--id',
            metavar="id",
            help="filter by id")
        parser.add_argument(
            '--ip_address',
            metavar="ip_address",
            help="filter by ip address")
        parser.add_argument(
            '--name',
            metavar="name",
            help="filter by name")
        parser.add_argument(
            '--network_id',
            metavar="network_id",
            help="filter by network id")
        parser.add_argument(
            '--slot_number',
            metavar="slot_number",
            help="filter by slot number")
        parser.add_argument(
            '--status',
            metavar="status",
            help="filter by status")
        parser.add_argument(
            '--virtual_ip_address',
            metavar="virtual_ip_address",
            help="filter by virtual ip address")

        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        columns = (
            'id',
            'name',
            'firewall_id',
            'ip_address',
            'status',
        )
        column_headers = (
            'ID',
            'Name',
            'Firewall',
            'Address',
            'Status',
        )
        search_opts = {}
        if parsed_args.firewall_id:
            search_opts.update({"firewall_id": parsed_args.firewall_id})
        if parsed_args.id:
            search_opts.update({"id": parsed_args.id})
        if parsed_args.ip_address:
            search_opts.update({"ip_address": parsed_args.ip_address})
        if parsed_args.name:
            search_opts.update({"name": parsed_args.name})
        if parsed_args.network_id:
            search_opts.update({"network_id": parsed_args.network_id})
        if parsed_args.slot_number:
            search_opts.update({"slot_number": parsed_args.slot_number})
        if parsed_args.status:
            search_opts.update({"status": parsed_args.status})
        if parsed_args.virtual_ip_address:
            search_opts.update({"virtual_ip_address": parsed_args.virtual_ip_address})

        data = [to_obj.FirewallInterface(firewall_interface)
                for firewall_interface in
                network_client.list_firewall_interfaces(
                        **search_opts).get('firewall_interfaces')]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowFirewallInterface(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(ShowFirewallInterface, self).get_parser(prog_name)
        parser.add_argument(
            'firewall_interface_id',
            metavar="FIREWALL_INTERFACE_ID",
            help="ID of Firewall Interface to show."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        firewall_interface_id = parsed_args.firewall_interface_id

        dic = network_client.show_firewall_interface(firewall_interface_id).get('firewall_interface')
        columns = utils.get_columns(dic)
        obj = to_obj.FirewallInterface(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return (columns, data)


class SetFirewallInterface(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(SetFirewallInterface, self).get_parser(prog_name)
        parser.add_argument(
            'firewall_interface_id',
            metavar='FIREWALL_INTERFACE_ID',
            help='ID of Public IP to update.')
        parser.add_argument(
            '--description',
            metavar='<string>',
            help='Description of firewall interface.')
        parser.add_argument(
            '--network_id',
            metavar='NETWORK_ID',
            help='Network ID for firewall interface to attach.'
                 'If you want to set this param to null, please specified 0.')
        parser.add_argument(
            '--ip_address',
            metavar='<ipv4>',
            help='Logical IP Address of firewall interface to be set.'
                 'If you want to set this param to null, please specified 0.')
        parser.add_argument(
            '--virtual_ip_address',
            metavar='<ipv4>',
            help='Virtual IP Address of firewall interface to be set.'
                 'If you want to set this param to null, please specified 0.')
        parser.add_argument(
            '--vrid',
            metavar='<integer>',
            type=int,
            help='VRID of firewall interface to be set.'
                 'If you want to set this param to null, please specified 0.')
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        body = {'firewall_interface': {}}
        firewall_interface_id = parsed_args.firewall_interface_id
        utils.update_dict(
            parsed_args,
            body['firewall_interface'],
            ['description', 'network_id', 'ip_address',
             'virtual_ip_address'])

        if parsed_args.network_id == '0':
            body["firewall_interface"]["network_id"] = None

        if parsed_args.ip_address == '0':
            body["firewall_interface"]["ip_address"] = None

        if parsed_args.virtual_ip_address == '0':
            body["firewall_interface"]["virtual_ip_address"] = None

        if parsed_args.vrid == 0:
            body["firewall_interface"]["virtual_ip_properties"] = None
        elif parsed_args.vrid:
            body["firewall_interface"]["virtual_ip_properties"] = {
                "protocol": "vrrp",
                "vrid": parsed_args.vrid,
            }

        dic = network_client.update_firewall_interface(
            firewall_interface_id, body).get('firewall_interface')
        columns = utils.get_columns(dic)
        obj = to_obj.FirewallInterface(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return (columns, data)
