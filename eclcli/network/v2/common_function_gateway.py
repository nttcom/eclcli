from eclcli.common import command
from eclcli.common import utils
from ..networkclient.common import utils as to_obj


class ListCommonFunctionGateway(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListCommonFunctionGateway, self).get_parser(prog_name)
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

        data = [to_obj.CommonFunctionGateway(common_function_gateway)
            for common_function_gateway in network_client.list_cfgws().get('common_function_gateways')]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowCommonFunctionGateway(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(ShowCommonFunctionGateway, self).get_parser(prog_name)
        parser.add_argument(
            'common_function_gateway_id',
            metavar="COMMON_FUNCTION_GATEWAY_ID",
            help="ID of Common Function Gateway to show."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        common_function_gateway_id = parsed_args.common_function_gateway_id

        dic = network_client.show_cfgw(common_function_gateway_id).get('common_function_gateway')
        columns = utils.get_columns(dic)
        obj = to_obj.CommonFunctionGateway(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data


class CreateCommonFunctionGateway(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(CreateCommonFunctionGateway, self).get_parser(prog_name)
        parser.add_argument(
            'common_function_pool_id',
            metavar='COMMON_FUNCTION_POOL_ID',
            help='Commoun Function Pool ID of '
                 'common function gateway to create.')
        parser.add_argument(
            '--name',
            metavar='<string>',
            help='Name of common function gateway to create.')
        parser.add_argument(
            '--description',
            metavar='<string>',
            help='Description of common function gateway to create.')
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        body = {'common_function_gateway': {}}
        utils.update_dict(
            parsed_args,
            body['common_function_gateway'],
            ['name', 'description', 'common_function_pool_id'])

        dic = network_client.create_cfgw(body).get('common_function_gateway')
        columns = utils.get_columns(dic)
        obj = to_obj.CommonFunctionGateway(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return (columns, data)


class SetCommonFunctionGateway(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(SetCommonFunctionGateway, self).get_parser(prog_name)
        parser.add_argument(
            'common_function_gateway_id',
            metavar="COMMON_FUNCTION_GATEWAY_ID",
            help="ID of Common Function Gateway to update."
        )
        parser.add_argument(
            '--name',
            metavar='<string>',
            help='Name of common function gateway to update.')
        parser.add_argument(
            '--description',
            metavar='<string>',
            help='Description of common function gateway to update.')
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        body = {'common_function_gateway': {}}
        common_function_gateway_id = parsed_args.common_function_gateway_id
        utils.update_dict(
            parsed_args,
            body['common_function_gateway'],
            ['name', 'description'])

        dic = network_client.update_cfgw(
            common_function_gateway_id, body).get('common_function_gateway')
        columns = utils.get_columns(dic)
        obj = to_obj.CommonFunctionGateway(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data


class DeleteCommonFunctionGateway(command.Command):
    def get_parser(self, prog_name):
        parser = super(DeleteCommonFunctionGateway, self).get_parser(prog_name)
        parser.add_argument(
            'common_function_gateway_id',
            metavar="COMMON_FUNCTION_GATEWAY_ID",
            nargs="+",
            help="ID(s) Common Function Gateway to delete."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        for cid in parsed_args.common_function_gateway_id:
            network_client.delete_cfgw(cid)
