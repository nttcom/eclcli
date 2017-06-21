from eclcli.common import command
from eclcli.common import utils
from ..networkclient.common import utils as to_obj


class ListColoSpace(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListColoSpace, self).get_parser(prog_name)
        parser.add_argument(
            '--description',
            metavar="description",
            help="filter by description")
        parser.add_argument(
            '--id',
            metavar="id",
            help="filter by id")
        parser.add_argument(
            '--name',
            metavar="name",
            help="filter by name")
        parser.add_argument(
            '--plane',
            metavar="plane",
            help="filter by plane")
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        columns = (
            'id',
            'name',
            'plane'
        )
        column_headers = (
            'ID',
            'Name',
            'Plane'
        )
        search_opts = {}
        if parsed_args.description:
            search_opts.update({"description": parsed_args.description})
        if parsed_args.id:
            search_opts.update({"id": parsed_args.id})
        if parsed_args.name:
            search_opts.update({"name": parsed_args.name})
        if parsed_args.plane:
            search_opts.update({"plane": parsed_args.plane})

        data = [to_obj.ColoSpace(cfp)
                for cfp in network_client.list_colo_spaces(
                    **search_opts).get('colocation_spaces')]

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
