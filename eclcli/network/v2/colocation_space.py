from eclcli.common import command
from eclcli.common import utils
from ..networkclient.common import utils as to_obj


class ListColoSpace(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListColoSpace, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        columns = (
            'id',
            'name',
        )
        column_headers = (
            'ID',
            'Name',
        )

        data = [to_obj.ColoSpace(cfp)
            for cfp in network_client.list_colo_spaces().get('colocation_spaces')]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowColoSpace(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(ShowColoSpace, self).get_parser(prog_name)
        parser.add_argument(
            'colocation_space_id',
            metavar="COLOCATION_SPACE_ID",
            help="ID of Colocation Space to show."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        colocation_space_id = parsed_args.colocation_space_id

        dic = network_client.show_colo_space(colocation_space_id).get('colocation_space')
        columns = utils.get_columns(dic)
        obj = to_obj.ColoSpace(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data
