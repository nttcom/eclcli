from eclcli.common import command
from eclcli.common import utils
from ..networkclient.common import utils as to_obj


class ListColoLogicalLink(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListColoLogicalLink, self).get_parser(prog_name)
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

        data = [to_obj.ColoLogicalLink(colocation_logical_link)
            for colocation_logical_link in network_client.list_colo_logical_links().get('colocation_logical_links')]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowColoLogicalLink(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(ShowColoLogicalLink, self).get_parser(prog_name)
        parser.add_argument(
            'colocation_logical_link_id',
            metavar="COLOCATION_LOGICAL_LINK_ID",
            help="ID of Colocation Logical Link to show."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        colocation_logical_link_id = parsed_args.colocation_logical_link_id

        dic = network_client.show_colo_logical_link(colocation_logical_link_id).get('colocation_logical_link')
        columns = utils.get_columns(dic)
        obj = to_obj.ColoLogicalLink(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data


class CreateColoLogicalLink(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(CreateColoLogicalLink, self).get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar='<string>',
            help='Name of colocation logical link to create.')
        parser.add_argument(
            '--description',
            metavar='<string>',
            help='Description of colocation logical link to create.')
        parser.add_argument(
            '--colocation_physical_link_id',
            metavar='COLOCATION_PHYSICAL_LINK_ID',
            required=True,
            help='Colocation physical link ID of colocation logical link to create.')
        parser.add_argument(
            '--network_id',
            metavar='NETWORK_ID',
            required=True,
            help='Network ID of colocation logical link to create.')
        parser.add_argument(
            '--vlan_id',
            metavar='<integer>',
            type=int,
            required=True,
            help='VLAN ID of colocation logical link to create.')
        parser.add_argument(
            '--tags',
            action='append',
            type=utils.parse_tags,
            metavar='<key=value>',
            help="Tags of logical link to create. "
                   "You can repeat this option.")
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        body = {'colocation_logical_link': {}}
        utils.update_dict(
            parsed_args,
            body['colocation_logical_link'],
            ['name', 'description',
             'colocation_physical_link_id',
             'network_id', 'vlan_id', 'tags'])

        dic = network_client.create_colo_logical_link(body).get('colocation_logical_link')
        columns = utils.get_columns(dic)
        obj = to_obj.ColoLogicalLink(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data


class SetColoLogicalLink(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(SetColoLogicalLink, self).get_parser(prog_name)
        parser.add_argument(
            'colocation_logical_link_id',
            metavar="COLOCATION_LOGICAL_LINK_ID",
            help="ID of Colocation Logical Link to update."
        )
        parser.add_argument(
            '--name',
            metavar='<string>',
            help='Name of colocation logical link to create.')
        parser.add_argument(
            '--description',
            metavar='<string>',
            help='Description of colocation logical link to create.')
        parser.add_argument(
            '--tags',
            action='append',
            type=utils.parse_tags,
            metavar='<key=value>',
            help="Tags of logical link to create. "
                   "You can repeat this option.")
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        body = {'colocation_logical_link': {}}
        colocation_logical_link_id = parsed_args.colocation_logical_link_id
        utils.update_dict(
            parsed_args,
            body['colocation_logical_link'],
            ['name', 'description', 'tags'])

        dic = network_client.update_colo_logical_link(
            colocation_logical_link_id, body).get('colocation_logical_link')
        columns = utils.get_columns(dic)
        obj = to_obj.ColoLogicalLink(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return (columns, data)


class DeleteColoLogicalLink(command.Command):
    def get_parser(self, prog_name):
        parser = super(DeleteColoLogicalLink, self).get_parser(prog_name)
        parser.add_argument(
            'colocation_logical_link_id',
            metavar="COLOCATION_LOGICAL_LINK_ID",
            nargs="+",
            help="ID(s) of Colocation Logical Link to delete."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        for cid in parsed_args.colocation_logical_link_id:
            network_client.delete_colo_logical_link(cid)
