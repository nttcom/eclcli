from eclcli.common import command
from eclcli.common import utils
from ..networkclient.common import utils as to_obj


class ListFICGateway(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListFICGateway, self).get_parser(prog_name)
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

        data = [to_obj.FICGateway(ficgw) for ficgw in
                network_client.list_fic_gateways().get('fic_gateways')]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowFICGateway(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(ShowFICGateway, self).get_parser(prog_name)
        parser.add_argument(
            'fic_gateway_id',
            metavar="FIC_GATEWAY_ID",
            help="ID of FIC Gateway to show."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        fic_gateway_id = parsed_args.fic_gateway_id

        dic = network_client.show_fic_gateway(fic_gateway_id).get('fic_gateway')
        columns = utils.get_columns(dic)
        obj = to_obj.FICGateway(dic)
        data = utils.get_item_properties(
            obj, columns, )
        return columns, data
