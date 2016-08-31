from eclcli.common import command
from eclcli.common import utils
from ..networkclient.common import utils as to_obj


class ListInterDCGateway(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListInterDCGateway, self).get_parser(prog_name)
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

        data = [to_obj.InterDCGateway(idcgw)
            for idcgw in network_client.list_interdc_gateways().get('interdc_gateways')]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowInterDCGateway(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(ShowInterDCGateway, self).get_parser(prog_name)
        parser.add_argument(
            'interdc_gateway_id',
            metavar="INTERDC_GATEWAY_ID",
            help="ID of Inter Data Center Gateway to show."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        interdc_gateway_id = parsed_args.interdc_gateway_id

        dic = network_client.show_interdc_gateway(interdc_gateway_id).get('interdc_gateway')
        columns = utils.get_columns(dic)
        obj = to_obj.InterDCGateway(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data
