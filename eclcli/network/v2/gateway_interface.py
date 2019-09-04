from eclcli.common import command
from eclcli.common import utils
from ..networkclient.common import utils as to_obj


class ListGwInterface(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListGwInterface, self).get_parser(prog_name)

        parser.add_argument(
            '--name',
            metavar="name",
            help="filter by name")
        parser.add_argument(
            '--id',
            metavar="id",
            help="filter by id")
        parser.add_argument(
            '--status',
            metavar="status",
            help="filter by status")
        parser.add_argument(
            '--service_type',
            metavar="service_type",
            help="filter by service_type")
        parser.add_argument(
            '--internet_gw_id',
            metavar="internet_gw_id",
            help="filter by internet gateway id")
        parser.add_argument(
            '--aws_gw_id',
            metavar="aws_gw_id",
            help="filter by aws gateway id")
        parser.add_argument(
            '--interdc_gw_id',
            metavar="interdc_gw_id",
            help="filter by interdc gateway id")
        parser.add_argument(
            '--vpn_gw_id',
            metavar="vpn_gw_id",
            help="filter by vpn gateway id")
        parser.add_argument(
            '--fic_gw_id',
            metavar="fic_gw_id",
            help="filter by fic gateway id")
        parser.add_argument(
            '--netmask',
            metavar="netmask",
            help="filter by netmask")
        parser.add_argument(
            '--network_id',
            metavar="network_id",
            help="filter by network id")
        parser.add_argument(
            '--gw_vipv4',
            metavar="gw_vipv4",
            help="filter by gateway ipv4")
        parser.add_argument(
            '--gw_vipv6',
            metavar="gw_vipv6",
            help="filter by gateway ipv6")
        parser.add_argument(
            '--primary_ipv4',
            metavar="primary_ipv4",
            help="filter by primary ipv4")
        parser.add_argument(
            '--primary_ipv6',
            metavar="primary_ipv6",
            help="filter by primary ipv6")
        parser.add_argument(
            '--secondary_ipv4',
            metavar="secondary_ipv4",
            help="filter by secondary ipv4")
        parser.add_argument(
            '--secondary_ipv6',
            metavar="secondary_ipv6",
            help="filter by secondary ipv6")
        parser.add_argument(
            '--vrid',
            metavar="vrid",
            help="filter by vrid")
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        columns = (
            'id',
            'name',
            'service_type',
            'network_id',
            'status',
        )
        column_headers = (
            'ID',
            'Name',
            'Service Type',
            'Network',
            'Status',
        )

        search_opts = {}
        if parsed_args.name:
            search_opts.update({"name": parsed_args.name})
        if parsed_args.id:
            search_opts.update({"id": parsed_args.id})
        if parsed_args.status:
            search_opts.update({"status": parsed_args.status})
        if parsed_args.service_type:
            search_opts.update({"service_type": parsed_args.service_type})
        if parsed_args.interdc_gw_id:
            search_opts.update({"interdc_gw_id": parsed_args.interdc_gw_id})
        if parsed_args.internet_gw_id:
            search_opts.update({"internet_gw_id": parsed_args.internet_gw_id})
        if parsed_args.aws_gw_id:
            search_opts.update({"aws_gw_id": parsed_args.aws_gw_id})
        if parsed_args.vpn_gw_id:
            search_opts.update({"vpn_gw_id": parsed_args.vpn_gw_id})
        if parsed_args.fic_gw_id:
            search_opts.update({"fic_gw_id": parsed_args.fic_gw_id})
        if parsed_args.netmask:
            search_opts.update({"netmask": parsed_args.netmask})
        if parsed_args.network_id:
            search_opts.update({"network_id": parsed_args.network_id})
        if parsed_args.gw_vipv4:
            search_opts.update({"gw_vipv4": parsed_args.gw_vipv4})
        if parsed_args.gw_vipv6:
            search_opts.update({"gw_vipv6": parsed_args.gw_vipv6})
        if parsed_args.primary_ipv4:
            search_opts.update({"primary_ipv4": parsed_args.primary_ipv4})
        if parsed_args.primary_ipv6:
            search_opts.update({"primary_ipv6": parsed_args.primary_ipv6})
        if parsed_args.secondary_ipv4:
            search_opts.update({"secondary_ipv4": parsed_args.secondary_ipv4})
        if parsed_args.secondary_ipv6:
            search_opts.update({"secondary_ipv6": parsed_args.secondary_ipv6})
        if parsed_args.vrid:
            search_opts.update({"vrid": parsed_args.vrid})

        data = [to_obj.GwInterface(gw_interface)
                for gw_interface in network_client.list_gw_interfaces(
                **search_opts).get('gw_interfaces')]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowGwInterface(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(ShowGwInterface, self).get_parser(prog_name)
        parser.add_argument(
            'gw_interface_id',
            metavar="GATEWAY_INTERFACE_ID",
            help="ID of Gateway Interface to show."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        gw_interface_id = parsed_args.gw_interface_id

        dic = network_client.show_gw_interface(gw_interface_id).get('gw_interface')
        columns = dic  # utils.get_columns(dic)
        obj = to_obj.GwInterface(dic)
        data = utils.get_item_properties(obj, columns,)
        return columns, data


class CreateGwInterface(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(CreateGwInterface, self).get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar='<string>',
            help='Name of Gateway interface to create.')
        parser.add_argument(
            '--description',
            metavar='<string>',
            help='Description of Gateway interface to create.')
        parser.add_argument(
            '--service_type',
            metavar='{vpn|internet|interdc|fic}',
            choices=["vpn", "internet", "interdc", "fic"],
            required=True,
            help='Service type of Gateway interface to create')
        parser.add_argument(
            '--vrid',
            metavar='VRID',
            type=int,
            required=True,
            help='VRRP ID of Gateway interface to create.')
        parser.add_argument(
            '--network_id',
            metavar='NETWORK_ID',
            required=True,
            help='Network ID of Gateway interface to create.')
        parser.add_argument(
            '--netmask',
            metavar='NETMASK',
            required=True,
            type=int,
            help='Netmask of Gateway interface to create.')
        parser.add_argument(
            '--primary_ipv4',
            metavar='<ipv4>',
            required=True,
            help='Primary IPv4 of Gateway interface to create.')
        parser.add_argument(
            '--secondary_ipv4',
            metavar='<ipv4>',
            required=True,
            help='Secondary IPv4 of Gateway interface to create.')
        parser.add_argument(
            '--gw_vipv4',
            metavar='<ipv4>',
            required=True,
            help='Secondary IPv4 of Gateway interface to create.')
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            '--internet_gw_id',
            metavar='INTERNET_GATEWAY_ID',
            help='Internet Gateway ID of Gateway interface to create.')
        group.add_argument(
            '--interdc_gw_id',
            metavar='INTERDC_GATEWAY_ID',
            help='InterDC Gateway ID of Gateway interface to create.')
        group.add_argument(
            '--vpn_gw_id',
            metavar='VPN_GATEWAY_ID',
            help='VPN Gateway ID of Gateway interface to create.')
        group.add_argument(
            '--fic_gw_id',
            metavar='FIC_GATEWAY_ID',
            help='FIC Gateway ID of Gateway interface to create.')
        parser.add_argument(
            '--primary_ipv6',
            metavar='<ipv6>',
            help='Primary IPv6 of Gateway interface to create.')
        parser.add_argument(
            '--secondary_ipv6',
            metavar='<ipv6>',
            help='Secondary IPv6 of Gateway interface to create.')
        parser.add_argument(
            '--gw_vipv6',
            metavar='<ipv6>',
            help='Secondary IPv6 of Gateway interface to create.')
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        body = {'gw_interface': {}}
        utils.update_dict(
            parsed_args,
            body['gw_interface'],
            ['name', 'description', 'service_type',
            'primary_ipv4', 'secondary_ipv4', 'gw_vipv4',
            'internet_gw_id', 'vpn_gw_id', 'fic_gw_id', 'interdc_gw_id',
            'primary_ipv6', 'secondary_ipv6', 'gw_vipv6',
            'vrid', 'network_id', 'netmask'])

        dic = network_client.create_gw_interface(body).get('gw_interface')
        columns = utils.get_columns(dic)
        obj = to_obj.GwInterface(dic)
        data = utils.get_item_properties(
            obj, columns, )
        return columns, data


class SetGwInterface(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(SetGwInterface, self).get_parser(prog_name)
        parser.add_argument(
            'gw_interface',
            metavar='GATEWAY_INTERFACE_ID',
            help='ID of gateway interface to update.')
        parser.add_argument(
            '--name',
            metavar='<string>',
            help='Name of Gateway interface to create.')
        parser.add_argument(
            '--description',
            metavar='<string>',
            help='Description of Gateway interface to create.')
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        body = {'gw_interface': {}}
        gw_interface_id = parsed_args.gw_interface
        utils.update_dict(
            parsed_args,
            body['gw_interface'],
            ['name', 'description'])

        dic = network_client.update_gw_interface(
            gw_interface_id, body).get('gw_interface')
        columns = utils.get_columns(dic)
        obj = to_obj.GwInterface(dic)
        data = utils.get_item_properties(
            obj, columns, )
        return columns, data


class DeleteGwInterface(command.Command):
    def get_parser(self, prog_name):
        parser = super(DeleteGwInterface, self).get_parser(prog_name)
        parser.add_argument(
            'gw_interface_id',
            metavar="GATEWAY_INTERFACE_ID",
            nargs="+",
            help="ID(s) of Gateway Interface to delete."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        for giid in parsed_args.gw_interface_id:
            network_client.delete_gw_interface(giid)
