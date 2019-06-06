from eclcli.common import command
from eclcli.common import utils
from ..networkclient.common import utils as to_obj


class ListFICInterface(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListFICInterface, self).get_parser(prog_name)
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

        data = [to_obj.FICInterface(ficsv) for ficsv in
                network_client.list_fic_interfaces().get('fic_interfaces')]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowFICInterface(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(ShowFICInterface, self).get_parser(prog_name)
        parser.add_argument(
            'fic_interface_id',
            metavar="FIC_INTERFACE_ID",
            help="ID of FIC Interface to show."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        fic_interface_id = parsed_args.fic_interface_id

        dic = network_client.show_fic_interface(fic_interface_id).get(
            'fic_interface')
        columns = utils.get_columns(dic)
        obj = to_obj.FICInterface(dic)
        data = utils.get_item_properties(
            obj, columns, )
        return columns, data
