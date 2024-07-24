from eclcli.common import command
from eclcli.common import utils
from eclcli.i18n import _  # noqa
from ..networkclient.common import utils as to_obj


class ListColoPhysicalLink(command.Lister):
    _description = _("List colocation-physical-links")
    def get_parser(self, prog_name):
        parser = super(ListColoPhysicalLink, self).get_parser(prog_name)

        parser.add_argument(
            '--bandwidth',
            metavar="bandwidth",
            help="filter by bandwidth")
        parser.add_argument(
            '--colocation_space_id',
            metavar="colocation_space_id",
            help="filter by colocation space id")
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
        parser.add_argument(
            '--status',
            metavar="status",
            help="filter by status")
        parser.add_argument(
            '--type_a_physical_port_id',
            metavar="type_a_physical_port_id",
            help="filter by type_a_physical_port_id")
        parser.add_argument(
            '--type_a_rack_id',
            metavar="type_a_rack_id",
            help="filter by type_a_rack_id")
        parser.add_argument(
            '--type_b_physical_port_id',
            metavar="type_b_physical_port_id",
            help="filter by type_b_physical_port_id")
        parser.add_argument(
            '--type_b_rack_id',
            metavar="type_b_rack_id",
            help="filter by type_b_rack_id")

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

        search_opts = {}
        if parsed_args.bandwidth:
            search_opts.update({"bandwidth": parsed_args.bandwidth})
        if parsed_args.colocation_space_id:
            search_opts.update({"colocation_space_id": parsed_args.colocation_space_id})
        if parsed_args.description:
            search_opts.update({"description": parsed_args.description})
        if parsed_args.id:
            search_opts.update({"id": parsed_args.id})
        if parsed_args.name:
            search_opts.update({"name": parsed_args.name})
        if parsed_args.plane:
            search_opts.update({"plane": parsed_args.plane})
        if parsed_args.status:
            search_opts.update({"status": parsed_args.status})
        if parsed_args.type_a_physical_port_id:
            search_opts.update({"type_a_physical_port_id": parsed_args.type_a_physical_port_id})
        if parsed_args.type_a_rack_id:
            search_opts.update({"type_a_rack_id": parsed_args.type_a_rack_id})
        if parsed_args.type_b_physical_port_id:
            search_opts.update({"type_b_physical_port_id": parsed_args.type_b_physical_port_id})
        if parsed_args.type_b_rack_id:
            search_opts.update({"type_b_rack_id": parsed_args.type_b_rack_id})

        data = [to_obj.ColoPhysicalLink(cfp)
                for cfp in network_client.list_colo_physical_links(
                    **search_opts).get('colocation_physical_links')]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowColoPhysicalLink(command.ShowOne):
    _description = _("Show colocation-physical-link")
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
