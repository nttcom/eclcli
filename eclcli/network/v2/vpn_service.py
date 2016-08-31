from eclcli.common import command
from eclcli.common import utils
from ..networkclient.common import utils as to_obj


class ListVPNService(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListVPNService, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        columns = (
            'id',
            'name',
            'zone',
        )
        column_headers = (
            'ID',
            'Name',
            'Zone',
        )

        data = [to_obj.VPNService(vpnsv)
                for vpnsv in network_client.list_vpn_services().get('vpn_services')]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowVPNService(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(ShowVPNService, self).get_parser(prog_name)
        parser.add_argument(
            'vpn_service_id',
            metavar="VPN_SERVICE_ID",
            help="ID of VPN Service to show."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        vpnsv_id = parsed_args.vpn_service_id

        dic = network_client.show_vpn_service(vpnsv_id).get('vpn_service')
        columns = utils.get_columns(dic)
        obj = to_obj.VPNService(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data
