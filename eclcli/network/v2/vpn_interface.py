from eclcli.common import command
from eclcli.common import utils
from ..networkclient.common import utils as to_obj


class ListVPNInterface(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListVPNInterface, self).get_parser(prog_name)
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

        data = [to_obj.VPNInterface(vpnsv)
                for vpnsv in network_client.list_vpn_interfaces().get('vpn_interfaces')]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowVPNInterface(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(ShowVPNInterface, self).get_parser(prog_name)
        parser.add_argument(
            'vpn_interface_id',
            metavar="VPN_INTERFACE_ID",
            help="ID of VPN Interface to show."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        vpn_interface_id = parsed_args.vpn_interface_id

        dic = network_client.show_vpn_interface(vpn_interface_id).get('vpn_interface')
        columns = utils.get_columns(dic)
        obj = to_obj.VPNInterface(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data
