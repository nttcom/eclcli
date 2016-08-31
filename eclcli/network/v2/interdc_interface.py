from eclcli.common import command
from eclcli.common import utils
from ..networkclient.common import utils as to_obj


class ListInterDCInterface(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListInterDCInterface, self).get_parser(prog_name)
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

        data = [to_obj.InterDCInterface(idcif)
            for idcif in network_client.list_interdc_interfaces().get('interdc_interfaces')]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowInterDCInterface(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(ShowInterDCInterface, self).get_parser(prog_name)
        parser.add_argument(
            'interdc_interface_id',
            metavar="INTERDC_INTERFACE_ID",
            help="ID of Inter Data Center Interface to show."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        interdc_interface_id = parsed_args.interdc_interface_id

        dic = network_client.show_interdc_interface(interdc_interface_id).get('interdc_interface')
        columns = utils.get_columns(dic)
        obj = to_obj.InterDCInterface(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return (columns, data)


class CreateInterDCInterface(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(CreateInterDCInterface, self).get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar='<string>',
            help='Name of InterDC interface to create.')
        parser.add_argument(
            '--description',
            metavar='<string>',
            help='Description of InterDC interface to create.')
        parser.add_argument(
            '--interdc_gw_id',
            metavar='INTERDC_GATEWAY_ID',
            required=True,
            help='InterDC Gateway ID of Gateway interface to create.')
        parser.add_argument(
            '--netmask',
            metavar='NETMASK',
            type=int,
            required=True,
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
        parser.add_argument(
            '--vrid',
            metavar='VRID',
            type=int,
            required=True,
            help='VRRP ID of InterDC interface to create.')
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

        body = {'interdc_interface': {}}
        utils.update_dict(
            parsed_args,
            body['interdc_interface'],
            ['name', 'description', 'netmask',
             'vrid', 'interdc_gw_id',
             'primary_ipv4', 'secondary_ipv4', 'gw_vipv4',
             'primary_ipv6', 'secondary_ipv6', 'gw_vipv6'])

        dic = network_client.create_interdc_interface(body).get('interdc_interface')
        columns = utils.get_columns(dic)
        obj = to_obj.InterDCInterface(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data


class SetInterDCInterface(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(SetInterDCInterface, self).get_parser(prog_name)
        parser.add_argument(
            'interdc_interface_id',
            metavar='<string>',
            help='ID of InterDC Interface to update.')
        parser.add_argument(
            '--name',
            metavar='<string>',
            help='Name of InterDC interface to update.')
        parser.add_argument(
            '--description',
            metavar='<string>',
            help='Description of InterDC interface to update.')
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        body = {'interdc_interface': {}}
        interdc_interface_id = parsed_args.interdc_interface_id
        utils.update_dict(
            parsed_args,
            body['interdc_interface'],
            ['name', 'description'])

        dic = network_client.update_interdc_interface(
            interdc_interface_id, body=body).get('interdc_interface')
        columns = utils.get_columns(dic)
        obj = to_obj.InterDCInterface(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data


class DeleteInterDCInterface(command.Command):
    def get_parser(self, prog_name):
        parser = super(DeleteInterDCInterface, self).get_parser(prog_name)
        parser.add_argument(
            'interdc_interface_id',
            metavar="<uuid>",
            nargs="+",
            help="ID(s) of InterDC Interface to delete."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        for idcif_id in parsed_args.interdc_interface_id:
            network_client.delete_interdc_interface(idcif_id)
