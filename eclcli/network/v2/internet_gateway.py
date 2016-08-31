from eclcli.common import command
from eclcli.common import utils
from ..networkclient.common import utils as to_obj


class ListInternetGateway(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListInternetGateway, self).get_parser(prog_name)
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

        data = [to_obj.InternetGateway(inetgw)
            for inetgw in network_client.list_internet_gateways().get('internet_gateways')]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowInternetGateway(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(ShowInternetGateway, self).get_parser(prog_name)
        parser.add_argument(
            'internet_gateway_id',
            metavar="INTERNET_GATEWAY_ID",
            help="ID of Internet Gateway to show."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        internet_gateway_id = parsed_args.internet_gateway_id

        dic = network_client.show_internet_gateway(internet_gateway_id).get('internet_gateway')
        columns = utils.get_columns(dic)
        obj = to_obj.InternetGateway(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data


class CreateInternetGateway(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(CreateInternetGateway, self).get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar='<string>',
            help='Name of internet gateway to create.')
        parser.add_argument(
            '--description',
            metavar='<string>',
            help='Description of internet gateway to create.')
        parser.add_argument(
            'internet_service_id',
            metavar='INTERNET_SERVICE_ID',
            help='Internet Service ID of internet gateway to create.')
        parser.add_argument(
            '--qos_option_id',
            metavar='QOS_OPTION_ID',
            help='QoS Option ID of internet gateway to create.')
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        body = {}
        if parsed_args.name is not None:
            body['name'] = str(parsed_args.name)
        if parsed_args.description is not None:
            body['description'] = str(parsed_args.description)
        body['internet_service_id'] = parsed_args.internet_service_id
        body['qos_option_id'] = parsed_args.qos_option_id

        dic = network_client.create_internet_gateway({'internet_gateway': body}).get('internet_gateway')
        columns = utils.get_columns(dic)
        obj = to_obj.InternetGateway(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data


class SetInternetGateway(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(SetInternetGateway, self).get_parser(prog_name)
        parser.add_argument(
            'internet_gateway_id',
            metavar='INTERNET_GATEWAY_ID',
            help='ID of internet gateway to update.')
        parser.add_argument(
            '--name',
            metavar='<string>',
            help='Name of internet gateway to update.')
        parser.add_argument(
            '--description',
            metavar='<string>',
            help='Description of internet gateway to update.')
        parser.add_argument(
            '--qos_option_id',
            metavar='QOS_OPTION_ID',
            help='QoS Option ID of internet gateway to update.')
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        body = {}
        internet_gateway_id = parsed_args.internet_gateway_id
        if parsed_args.name is not None:
            body['name'] = str(parsed_args.name)
        if parsed_args.description is not None:
            body['description'] = str(parsed_args.description)
        if parsed_args.qos_option_id is not None:
            body['qos_option_id'] = parsed_args.qos_option_id

        dic = network_client.update_internet_gateway(
            internet_gateway_id, body={'internet_gateway': body}).get('internet_gateway')
        columns = utils.get_columns(dic)
        obj = to_obj.InternetGateway(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data


class DeleteInternetGateway(command.Command):
    def get_parser(self, prog_name):
        parser = super(DeleteInternetGateway, self).get_parser(prog_name)
        parser.add_argument(
            'internet_gateway_id',
            metavar="INTERNET_GATEWAY_ID",
            nargs="+",
            help="ID(s) of Internet Gateway to delete."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        for inetgw_id in parsed_args.internet_gateway_id:
            network_client.delete_internet_gateway(inetgw_id)
