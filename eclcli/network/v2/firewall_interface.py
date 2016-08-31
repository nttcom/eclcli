from eclcli.common import command
from eclcli.common import utils
from ..networkclient.common import utils as to_obj


class ListFirewallInterface(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListFirewallInterface, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        columns = (
            'id',
            'name',
            'status',
        )
        column_headers = (
            'ID',
            'Name',
            'Status',
        )

        data = [to_obj.FirewallInterface(firewall_interface)
            for firewall_interface in network_client.list_firewall_interfaces().get('firewall_interfaces')]

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
            help='Network ID for firewall interface to attach.')
        parser.add_argument(
            '--ip_address',
            metavar='<ipv4>',
            help='Logical IP Address of firewall interface to be set.')
        parser.add_argument(
            '--virtual_ip_address',
            metavar='<ipv4>',
            help='Virtual IP Address of firewall interface to be set.')
        parser.add_argument(
            '--vrid',
            metavar='<integer>',
            type=int,
            help='VRID of firewall interface to be set.')
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

        dic = network_client.update_firewall_interface(
            firewall_interface_id, body).get('firewall_interface')
        columns = utils.get_columns(dic)
        obj = to_obj.FirewallInterface(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return (columns, data)
