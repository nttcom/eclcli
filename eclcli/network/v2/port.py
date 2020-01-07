from eclcli.common import command
from eclcli.common import utils
from ..networkclient.common import utils as to_obj


class ListPort(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListPort, self).get_parser(prog_name)
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

        data = [to_obj.Port(port)
                for port in network_client.list_ports().get('ports')]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowPort(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(ShowPort, self).get_parser(prog_name)
        parser.add_argument(
            'port_id',
            metavar="<uuid>",
            help="Port ID to show."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        port_id = parsed_args.port_id

        dic = network_client.show_port(port_id).get('port')
        columns = utils.get_columns(dic)
        obj = to_obj.Port(dic)
        data = utils.get_item_properties(
            obj, columns, )
        return columns, data


class CreatePort(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(CreatePort, self).get_parser(prog_name)
        parser.add_argument(
            'network_id',
            metavar='NETWORK_ID',
            help='Network ID this port belongs to.')
        parser.add_argument(
            '--name',
            metavar='<string>',
            help='Name of this port.')
        parser.add_argument(
            '--description',
            metavar='<string>',
            help='Description of this port.')
        parser.add_argument(
            '--admin_state_up',
            metavar='{true|false}',
            type=utils.parse_bool,
            choices=[True, False],
            help='Admin State Up of this port.')
        parser.add_argument(
            '--fixed_ips',
            metavar='<subnet_id,ipv4>|<ipv4>',
            action='append',
            type=utils.parse_fixed_ips,
            help='Subnet and desired IP for this port: '
                 'subnet_id,ipv4 or ipv4 format. '
                 'You can repeat this option.')
        parser.add_argument(
            '--allowed_address_pairs',
            metavar='<cidr|ipv4>|<cidr|ipv4,mac>',
            action='append',
            type=utils.parse_allowed_address_pairs,
            help='Allowed address pairs of this port. '
                 'ipv4|cidr or ipv4|cidr,mac format. '
                 'You can repeat this option.')
        parser.add_argument(
            '--mac_address',
            metavar='<mac>',
            help='MAC address of this port.')
        parser.add_argument(
            '--segmentation_id',
            metavar='<integer>',
            type=int,
            help='Segmentation id of this port.')
        parser.add_argument(
            '--segmentation_type',
            metavar='{flat|vlan}',
            choices=['flat', 'vlan'],
            help='Segmentation type of this port.')
        parser.add_argument(
            '--device_id',
            metavar='<string>',
            help='Device ID of this port.')
        parser.add_argument(
            '--device_owner',
            metavar='<string>',
            help='Device owner of this port.')
        parser.add_argument(
            '--tags',
            action='append',
            type=utils.parse_tags,
            metavar='<key=value>',
            help="Tags of this port. "
                 "You can repeat this option.")
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        body = {'port': {}}
        body['port'].update({'network_id': parsed_args.network_id})
        if parsed_args.name:
            body['port'].update({'name': parsed_args.name})
        if parsed_args.description:
            body['port'].update({'description': parsed_args.description})
        if not (parsed_args.admin_state_up is None):
            body['port'].update({'admin_state_up': parsed_args.admin_state_up})
        if parsed_args.fixed_ips:
            result = [fixed_ip for fixed_ip in parsed_args.fixed_ips if fixed_ip != {}]
            body['port'].update({'fixed_ips': result})
        if parsed_args.allowed_address_pairs:
            body['port'].update({'allowed_address_pairs': parsed_args.allowed_address_pairs})
        if parsed_args.mac_address:
            body['port'].update({'mac_address': parsed_args.mac_address})
        if parsed_args.segmentation_id:
            body['port'].update({'segmentation_id': parsed_args.segmentation_id})
        if parsed_args.segmentation_type:
            body['port'].update({'segmentation_type': parsed_args.segmentation_type})
        if parsed_args.device_id:
            body['port'].update({'device_id': parsed_args.device_id})
        if parsed_args.device_owner:
            body['port'].update({'device_owner': parsed_args.device_owner})
        if parsed_args.tags:
            tags = {}
            for tag in parsed_args.tags:
                tags.update(tag)
            body['port'].update({'tags': tags})

        dic = network_client.create_port(body).get('port')
        columns = utils.get_columns(dic)
        obj = to_obj.Port(dic)
        data = utils.get_item_properties(
            obj, columns, )
        return columns, data


class SetPort(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(SetPort, self).get_parser(prog_name)
        parser.add_argument(
            'port_id',
            metavar='PORT_ID',
            help='Port ID to update.')
        parser.add_argument(
            '--name',
            metavar='<string>',
            help='Name of this port.')
        parser.add_argument(
            '--description',
            metavar='<string>',
            help='Description of this port.')
        parser.add_argument(
            '--admin_state_up',
            metavar='{true|false}',
            type=utils.parse_bool,
            choices=[True, False],
            help='Admin State Up of this port.')
        parser.add_argument(
            '--fixed_ips',
            metavar='<subnet_id,ipv4>|<ipv4>',
            action='append',
            type=utils.parse_fixed_ips,
            help='Subnet and desired IP for this port: '
                 'subnet_id,ipv4 or ipv4 format. '
                 'You can repeat this option.')
        parser.add_argument(
            '--allowed_address_pairs',
            metavar='<cidr|ipv4>|<cidr|ipv4,mac>',
            action='append',
            type=utils.parse_allowed_address_pairs,
            help='Allowed address pairs of this port. '
                 'ipv4|cidr or ipv4|cidr,mac format. '
                 'You can repeat this option.')
        parser.add_argument(
            '--segmentation_id',
            metavar='<integer>',
            type=int,
            help='Segmentation id of this port.')
        parser.add_argument(
            '--segmentation_type',
            metavar='{flat|vlan}',
            choices=['flat', 'vlan'],
            help='Segmentation type of this port.')
        parser.add_argument(
            '--device_id',
            metavar='<string>',
            help='Device ID of this port.')
        parser.add_argument(
            '--device_owner',
            metavar='<string>',
            help='Device owner of this port.')
        parser.add_argument(
            '--tags',
            action='append',
            type=utils.parse_tags,
            metavar='<key=value>',
            help="Tags of this port. "
                 "You can repeat this option.")
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        body = {'port': {}}
        port_id = parsed_args.port_id
        if parsed_args.name:
            body['port'].update({'name': parsed_args.name})
        if parsed_args.description:
            body['port'].update({'description': parsed_args.description})
        if not (parsed_args.admin_state_up is None):
            body['port'].update({'admin_state_up': parsed_args.admin_state_up})
        if parsed_args.fixed_ips:
            body['port'].update({'fixed_ips': parsed_args.fixed_ips})
        if parsed_args.allowed_address_pairs:
            result = [allowed_address_pair for allowed_address_pair in parsed_args.allowed_address_pairs
                      if allowed_address_pair != {}]
            body['port'].update({'allowed_address_pairs': result})
        if parsed_args.segmentation_id:
            body['port'].update({'segmentation_id': parsed_args.segmentation_id})
        if parsed_args.segmentation_type:
            body['port'].update({'segmentation_type': parsed_args.segmentation_type})
        if parsed_args.device_id:
            body['port'].update({'device_id': parsed_args.device_id})
        if parsed_args.device_owner:
            body['port'].update({'device_owner': parsed_args.device_owner})
        if parsed_args.tags:
            tags = {}
            for tag in parsed_args.tags:
                tags.update(tag)
            body['port'].update({'tags': tags})

        dic = network_client.update_port(
            port_id, body).get('port')
        columns = utils.get_columns(dic)
        obj = to_obj.Port(dic)
        data = utils.get_item_properties(
            obj, columns, )
        return columns, data


class DeletePort(command.Command):
    def get_parser(self, prog_name):
        parser = super(DeletePort, self).get_parser(prog_name)
        parser.add_argument(
            'port_id',
            metavar="<uuid>",
            nargs="+",
            help="Port(s) ID to delete."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        for pid in parsed_args.port_id:
            network_client.delete_port(pid)
