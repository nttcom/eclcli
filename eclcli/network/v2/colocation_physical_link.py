from eclcli.common import command
from eclcli.common import utils
from ..networkclient.common import utils as to_obj


class ListColoPhysicalLink(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListColoPhysicalLink, self).get_parser(prog_name)
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

        data = [to_obj.ColoPhysicalLink(cfp)
            for cfp in network_client.list_colo_physical_links().get('colocation_physical_links')]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowColoPhysicalLink(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(ShowColoPhysicalLink, self).get_parser(prog_name)
        parser.add_argument(
            'colocation_physical_link_id',
            metavar="COLOCATION_PHYSICAL_LINK_ID",
            help="ID of Colocation Physical Link to show."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        colocation_physical_link_id = parsed_args.colocation_physical_link_id

        dic = network_client.show_colo_physical_link(colocation_physical_link_id).get('colocation_physical_link')
        columns = utils.get_columns(dic)
        obj = to_obj.ColoPhysicalLink(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data
