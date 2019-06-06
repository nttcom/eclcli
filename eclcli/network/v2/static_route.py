from eclcli.common import command
from eclcli.common import utils
from ..networkclient.common import utils as to_obj


class ListStaticRoute(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListStaticRoute, self).get_parser(prog_name)

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
            '--nexthop',
            metavar="nexthop",
            help="filter by next hop")
        parser.add_argument(
            '--destination',
            metavar="destination",
            help="filter by destination")
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

        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        columns = (
            'id',
            'name',
            'service_type',
            'destination',
            'nexthop',
            'status',
        )
        column_headers = (
            'ID',
            'Name',
            'Service Type',
            'Destination',
            'Nexthop',
            'Status',
        )

        search_opts = {}
        if parsed_args.name:
            search_opts.update({"name": parsed_args.name})
        if parsed_args.id:
            search_opts.update({"id": parsed_args.id})
        if parsed_args.status:
            search_opts.update({"status": parsed_args.status})
        if parsed_args.destination:
            search_opts.update({"destination": parsed_args.destination})
        if parsed_args.nexthop:
            search_opts.update({"nexthop": parsed_args.nexthop})
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

        data = [to_obj.StaticRoute(static_route)
                for static_route in network_client.list_static_routes(
                            **search_opts).get('static_routes')]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowStaticRoute(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(ShowStaticRoute, self).get_parser(prog_name)
        parser.add_argument(
            'static_route_id',
            metavar="STATIC_ROUTE_ID",
            help="ID of Static Route to show."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        static_route_id = parsed_args.static_route_id

        dic = network_client.show_static_route(static_route_id).get('static_route')
        columns = utils.get_columns(dic)
        obj = to_obj.StaticRoute(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data


class CreateStaticRoute(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(CreateStaticRoute, self).get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar='<string>',
            help='Name of Static Route to create.')
        parser.add_argument(
            '--description',
            metavar='<string>',
            help='Description of Static Route to create.')
        parser.add_argument(
            '--destination',
            metavar='CIDR',
            required=True,
            help='Destination of Static Route to create.')
        parser.add_argument(
            '--nexthop',
            metavar='<ipv4>',
            required=True,
            help='Nexthop of Static Route to create.')
        parser.add_argument(
            '--service_type',
            metavar='{vpn|internet|interdc|fic}',
            choices=["vpn", "internet", "interdc", "fic"],
            required=True,
            help='SERVICE_TYPE of Static Route to create.')
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            '--internet_gw_id',
            metavar='INTERNET_GATEWAY_ID',
            help='Internet gateway id of Static Route to create.')
        group.add_argument(
            '--interdc_gw_id',
            metavar='INTERDC_GW_ID',
            help='InterDC gateway id of Static Route to create.')
        group.add_argument(
            '--vpn_gw_id',
            metavar='VPN_GATEWAY_ID',
            help='VPN gateway id of Static Route to create.')
        group.add_argument(
            '--fic_gw_id',
            metavar='FIC_GATEWAY_ID',
            help='FIC gateway id of Static Route to create.')
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        body = {'static_route': {}}
        utils.update_dict(
            parsed_args,
            body['static_route'],
            ['name', 'description', 'destination',
             'nexthop', 'service_type', 'internet_gw_id',
             'interdc_gw_id', 'vpn_gw_id', 'fic_gw_id'])

        dic = network_client.create_static_route(body).get('static_route')
        columns = utils.get_columns(dic)
        obj = to_obj.StaticRoute(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return (columns, data)


class SetStaticRoute(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(SetStaticRoute, self).get_parser(prog_name)
        parser.add_argument(
            'static_route_id',
            metavar='STATIC_ROUTE_ID',
            help='ID of Static Route to update.')
        parser.add_argument(
            '--name',
            metavar='<string>',
            help='Name of Static Route to update.')
        parser.add_argument(
            '--description',
            metavar='<string>',
            help='Description of Static Route to update.')
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        body = {'static_route': {}}
        static_route_id = parsed_args.static_route_id
        utils.update_dict(
            parsed_args,
            body['static_route'],
            ['name', 'description'])

        dic = network_client.update_static_route(
            static_route_id, body).get('static_route')
        columns = utils.get_columns(dic)
        obj = to_obj.StaticRoute(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data


class DeleteStaticRoute(command.Command):
    def get_parser(self, prog_name):
        parser = super(DeleteStaticRoute, self).get_parser(prog_name)
        parser.add_argument(
            'static_route_id',
            metavar="STATIC_ROUTE_ID",
            nargs="+",
            help="ID(s) of Static Route to delete."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        for giid in parsed_args.static_route_id:
            network_client.delete_static_route(giid)
