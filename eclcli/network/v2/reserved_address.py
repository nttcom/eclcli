from eclcli.common import command
from eclcli.common import utils
from ..networkclient.common import utils as to_obj


class ListReservedAddress(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListReservedAddress, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        columns = (
            'id',
            'name',
            'subnets',
        )
        column_headers = (
            'ID',
            'Name',
            'Subnets',
        )

        data = [to_obj.ReservedAddress(ra)
                for ra in network_client.list_reserve_addresses().get('reserve_addresses')]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowReservedAddress(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(ShowReservedAddress, self).get_parser(prog_name)
        parser.add_argument(
            'reserve_address_id',
            metavar="RESERVED_ADDRESS_ID",
            help="ID of Reserved Address to show."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        ra_id = parsed_args.reserve_address_id

        dic = network_client.show_reserve_address(ra_id).get('reserve_address')
        columns = utils.get_columns(dic)
        obj = to_obj.ReservedAddress(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data
