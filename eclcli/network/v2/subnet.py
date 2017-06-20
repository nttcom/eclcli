from eclcli.common import command
from eclcli.common import utils
from ..networkclient.common import utils as to_obj


class ListSubnet(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListSubnet, self).get_parser(prog_name)

        parser.add_argument(
            '--cidr',
            metavar="cidr",
            help="filter by cidr")
        parser.add_argument(
            '--description',
            metavar="description",
            help="filter by description")
        parser.add_argument(
            '--gateway_ip',
            metavar="gateway_ip",
            help="filter by gateway_ip")
        parser.add_argument(
            '--id',
            metavar="id",
            help="filter by id")
        parser.add_argument(
            '--ip_version',
            metavar="ip_version",
            help="filter by ip_version")
        parser.add_argument(
            '--ipv6_address_mode',
            metavar="ipv6_address_mode",
            help="filter by ipv6_address_mode")
        parser.add_argument(
            '--ipv6_ra_mode',
            metavar="ipv6_ra_mode",
            help="filter by ipv6_ra_mode")
        parser.add_argument(
            '--name',
            metavar="name",
            help="filter by name")
        parser.add_argument(
            '--network_id',
            metavar="network_id",
            help="filter by network_id")
        parser.add_argument(
            '--status',
            metavar="status",
            help="filter by status")

        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        columns = (
            'id',
            'name',
            'cidr',
            'status',
        )
        column_headers = (
            'ID',
            'Name',
            'CIDR',
            'Status',
        )

        search_opts = {}
        if parsed_args.cidr:
            search_opts.update({"cidr": parsed_args.cidr})
        if parsed_args.description:
            search_opts.update({"description": parsed_args.description})
        if parsed_args.gateway_ip:
            search_opts.update({"gateway_ip": parsed_args.gateway_ip})
        if parsed_args.id:
            search_opts.update({"id": parsed_args.id})
        if parsed_args.ip_version:
            search_opts.update({"ip_version": parsed_args.ip_version})
        if parsed_args.ipv6_address_mode:
            search_opts.update({"ipv6_address_mode": parsed_args.ipv6_address_mode})
        if parsed_args.ipv6_ra_mode:
            search_opts.update({"ipv6_ra_mode": parsed_args.ipv6_ra_mode})
        if parsed_args.name:
            search_opts.update({"name": parsed_args.name})
        if parsed_args.network_id:
            search_opts.update({"network_id": parsed_args.network_id})
        if parsed_args.status:
            search_opts.update({"status": parsed_args.status})

        data = [to_obj.Subnet(subnet)
                for subnet in network_client.list_subnets(
                    **search_opts).get('subnets')]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowSubnet(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(ShowSubnet, self).get_parser(prog_name)
        parser.add_argument(
            'subnet_id',
            metavar="<uuid>",
            help="Subnet ID to show."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        subnet_id = parsed_args.subnet_id

        dic = network_client.show_subnet(subnet_id).get('subnet')
        columns = utils.get_columns(dic)
        obj = to_obj.Subnet(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data


class CreateSubnet(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(CreateSubnet, self).get_parser(prog_name)
        parser.add_argument(
            'network_id',
            metavar='NETWORK_ID',
            help='Network ID this subnet belongs to.')
        parser.add_argument(
            'cidr',
            metavar='CIDR',
            help='CIDR of subnet to create.')
        parser.add_argument(
            '--name',
            metavar='<string>',
            help='Name of this subnet.')
        parser.add_argument(
            '--description',
            metavar='<string>',
            help='Description of this subnet.')
        parser.add_argument(
            '--gateway_ip',
            metavar='<ipv4>',
            help='Gateway IP of this subnet.')
        parser.add_argument(
            '--no_gateway',
            metavar='<boolean>',
            type=utils.parse_bool,
            choices=[True, False],
            default=False,
            help='No gateway for this subnet.')
        parser.add_argument(
            '--ip_version',
            metavar='<integer>',
            type=int,
            choices=[4],
            default=4,
            help="IP version for this subnet.")
        parser.add_argument(
            '--enable_dhcp',
            metavar='<boolean>',
            type=utils.parse_bool,
            choices=[True, False],
            default=True,
            help='Enable DHCP for this subnet.')
        parser.add_argument(
            '--allocation_pools',
            metavar='<ipv4,ipv4>',
            action='append',
            type=utils.parse_allocation_pools,
            help='Allocation pool IP addresses for this subnet. '
                 'Start IP,end IP format. '
                 'You can repeat this option.')
        parser.add_argument(
            '--dns_nameservers',
            metavar='<ipv4>',
            action='append',
            help='DNS name server for this subnet. '
                 'You can repeat this option.')
        parser.add_argument(
            '--ntp_servers',
            metavar='<ipv4>',
            action='append',
            help='NTP server for this subnet. '
                 'You can repeat this option.')
        parser.add_argument(
            '--host_routes',
            metavar='<cidr,ipv4>',
            action='append',
            type=utils.parse_host_routes,
            help='Host route for this subnet. '
                 '"Distination,nexthop" format '
                 'You can repeat this option.')
        parser.add_argument(
            '--tags',
            action='append',
            type=utils.parse_tags,
            metavar='<key=value>',
            help="Tags for this subnet. "
                 "You can repeat this option.")
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        body = {'subnet': {}}
        body['subnet'].update({'network_id': parsed_args.network_id})
        body['subnet'].update({'cidr': parsed_args.cidr})
        body['subnet'].update({'ip_version': parsed_args.ip_version})
        if parsed_args.name:
            body['subnet'].update({'name': parsed_args.name})
        if parsed_args.description:
            body['subnet'].update({'description': parsed_args.description})
        if parsed_args.no_gateway:
            body['subnet'].update({'gateway_ip': None})
        elif parsed_args.gateway_ip:
            body['subnet'].update({'gateway_ip': parsed_args.gateway_ip})
        body['subnet'].update({'enable_dhcp': parsed_args.enable_dhcp})
        if parsed_args.allocation_pools:
            body['subnet']['allocation_pools'] = parsed_args.allocation_pools
        if parsed_args.dns_nameservers:
            body['subnet']['dns_nameservers'] = parsed_args.dns_nameservers
        if parsed_args.ntp_servers:
            body['subnet']['ntp_servers'] = parsed_args.ntp_servers
        if parsed_args.host_routes:
            body['subnet']['host_routes'] = parsed_args.host_routes
        if parsed_args.tags:
            tags = {}
            for tag in parsed_args.tags:
                tags.update(tag)
            body['subnet'].update({'tags': tags})

        dic = network_client.create_subnet(body).get('subnet')
        columns = utils.get_columns(dic)
        obj = to_obj.Subnet(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return (columns, data)


class SetSubnet(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(SetSubnet, self).get_parser(prog_name)
        parser.add_argument(
            'subnet_id',
            metavar='SUBNET_ID',
            help='Subnet ID to update.')
        parser.add_argument(
            '--name',
            metavar='<string>',
            help='Name of this subnet.')
        parser.add_argument(
            '--description',
            metavar='<string>',
            help='Description of this subnet.')
        parser.add_argument(
            '--gateway_ip',
            metavar='<ipv4>',
            help='Gateway IP of this subnet.')
        parser.add_argument(
            '--no_gateway',
            metavar='<boolean>',
            type=utils.parse_bool,
            choices=[True, False],
            default=False,
            help='No gateway for this subnet.')
        parser.add_argument(
            '--enable_dhcp',
            metavar='<boolean>',
            type=utils.parse_bool,
            choices=[True, False],
            default=True,
            help='Enable DHCP for this subnet.')
        parser.add_argument(
            '--dns_nameservers',
            metavar='<ipv4>',
            action='append',
            help='DNS name server for this subnet. '
                 'You can repeat this option.')
        parser.add_argument(
            '--ntp_servers',
            metavar='<ipv4>',
            action='append',
            help='NTP server for this subnet. '
                 'You can repeat this option.')
        parser.add_argument(
            '--host_routes',
            metavar='<cidr,ipv4>',
            action='append',
            type=utils.parse_host_routes,
            help='Host route for this subnet. '
                 '"Distination,nexthop" format '
                 'You can repeat this option.')
        parser.add_argument(
            '--tags',
            action='append',
            type=utils.parse_tags,
            metavar='<key=value>',
            help="Tags for this subnet. "
                 "You can repeat this option.")
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        body = {'subnet': {}}
        subnet_id = parsed_args.subnet_id
        if parsed_args.name:
            body['subnet'].update({'name': parsed_args.name})
        if parsed_args.description:
            body['subnet'].update({'description': parsed_args.description})
        if parsed_args.no_gateway:
            body['subnet'].update({'gateway_ip': None})
        elif parsed_args.gateway_ip:
            body['subnet'].update({'gateway_ip': parsed_args.gateway_ip})
        if not (parsed_args.enable_dhcp is None):
            body['subnet'].update({'enable_dhcp': parsed_args.enable_dhcp})
        if parsed_args.dns_nameservers:
            body['subnet']['dns_nameservers'] = parsed_args.dns_nameservers
        if parsed_args.ntp_servers:
            body['subnet']['ntp_servers'] = parsed_args.ntp_servers
        if parsed_args.host_routes:
            body['subnet']['host_routes'] = parsed_args.host_routes
        if parsed_args.tags:
            tags = {}
            for tag in parsed_args.tags:
                tags.update(tag)
            body['subnet'].update({'tags': tags})

        dic = network_client.update_subnet(
            subnet_id, body=body).get('subnet')
        columns = utils.get_columns(dic)
        obj = to_obj.Subnet(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return (columns, data)


class DeleteSubnet(command.Command):
    def get_parser(self, prog_name):
        parser = super(DeleteSubnet, self).get_parser(prog_name)
        parser.add_argument(
            'subnet_id',
            metavar="SUBNET_ID",
            nargs="+",
            help=("Subnet(s) ID to delete.")
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        for sid in parsed_args.subnet_id:
            network_client.delete_subnet(sid)
