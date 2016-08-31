from eclcli.common import command
from eclcli.common import utils
from ..networkclient.common import utils as to_obj


class ListVPNGateway(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListVPNGateway, self).get_parser(prog_name)
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

        data = [to_obj.VPNGateway(vpngw)
                for vpngw in network_client.list_vpn_gateways().get('vpn_gateways')]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowVPNGateway(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(ShowVPNGateway, self).get_parser(prog_name)
        parser.add_argument(
            'vpn_gateway_id',
            metavar="VPN_GATEWAY_ID",
            help="ID of VPN Gateway to show."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        vpn_gateway_id = parsed_args.vpn_gateway_id

        dic = network_client.show_vpn_gateway(vpn_gateway_id).get('vpn_gateway')
        columns = utils.get_columns(dic)
        obj = to_obj.VPNGateway(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data
