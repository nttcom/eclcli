from eclcli.common import command
from eclcli.common import utils
from eclcli.i18n import _  # noqa
from ..networkclient.common import utils as to_obj


class ListNetwork(command.Lister):
    _description = _("List logical-networks")
    def get_parser(self, prog_name):
        parser = super(ListNetwork, self).get_parser(prog_name)

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

        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        columns = (
            'id',
            'name',
            'subnets',
            'status',
        )
        column_headers = (
            'ID',
            'Name',
            'Subnets',
            'Status',
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
        if parsed_args.status:
            search_opts.update({"status": parsed_args.status})
        data = [to_obj.Network(network)
                for network in network_client.list_networks(
                    **search_opts).get('networks')]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={'subnets': utils.format_lister}
                ) for s in data))


class ShowNetwork(command.ShowOne):
    _description = _("Show logical-network")
    def get_parser(self, prog_name):
        parser = super(ShowNetwork, self).get_parser(prog_name)
        parser.add_argument(
            'network_id',
            metavar="<uuid>",
            help="Network ID to show."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        network_id = parsed_args.network_id

        dic = network_client.show_network(network_id).get('network')
        columns = utils.get_columns(dic)
        obj = to_obj.Network(dic)
        data = utils.get_item_properties(
            obj, columns, formatters={'subnets': utils.format_list})
        return (columns, data)


class CreateNetwork(command.ShowOne):
    _description = _("Create new logical-network")
    def get_parser(self, prog_name):
        parser = super(CreateNetwork, self).get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar='<string>',
            help='Name of network to create.'
        )
        parser.add_argument(
            '--description',
            metavar='<string>',
            help='Description of network to create.'
        )
        parser.add_argument(
            '--plane',
            metavar='{data|storage}',
            choices=['data', 'storage'],
            help='Plane of network to create.'
        )
        parser.add_argument(
            '--admin_state_up',
            metavar='<boolean>',
            type=utils.parse_bool,
            choices=[True, False],
            help='Admin State Up of network to create.'
        )
        parser.add_argument(
            '--tags',
            action='append',
            type=utils.parse_tags,
            metavar='<key=value>',
            help="Tags of network to create. "
                 "You can repeat this option."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        body = {}
        if parsed_args.name is not None:
            body['name'] = str(parsed_args.name)
        if parsed_args.description is not None:
            body['description'] = str(parsed_args.description)
        if parsed_args.plane is not None:
            body['plane'] = parsed_args.plane
        if parsed_args.admin_state_up is not None:
            body['admin_state_up'] = parsed_args.admin_state_up
        if parsed_args.tags is not None:
            tags = {}
            for tag in parsed_args.tags:
                tags.update(tag)
            body['tags'] = tags

        dic = network_client.create_network({'network': body}).get('network')
        columns = utils.get_columns(dic)
        obj = to_obj.Network(dic)
        data = utils.get_item_properties(
            obj, columns, formatters={'subnets': utils.format_list})
        return (columns, data)


class SetNetwork(command.ShowOne):
    _description = _("Update logical-network")
    def get_parser(self, prog_name):
        parser = super(SetNetwork, self).get_parser(prog_name)
        parser.add_argument(
            'network_id',
            metavar="<uuid>",
            help=("Network ID to update.")
        )
        parser.add_argument(
            '--name',
            metavar='<string>',
            help='Name of network to create.'
        )
        parser.add_argument(
            '--description',
            metavar='<string>',
            help='Description of network to create.'
        )
        parser.add_argument(
            '--admin_state_up',
            metavar='<boolean>',
            type=utils.parse_bool,
            choices=[True, False],
            help='Admin State Up of network to create.'
        )
        parser.add_argument(
            '--tags',
            action='append',
            type=utils.parse_tags,
            metavar='<key=value>',
            help="Tags of network to create. "
                 "You can repeat this option."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        body = {}
        network_id = parsed_args.network_id
        if parsed_args.name is not None:
            body['name'] = str(parsed_args.name)
        if parsed_args.description is not None:
            body['description'] = str(parsed_args.description)
        if parsed_args.admin_state_up is not None:
            body['admin_state_up'] = parsed_args.admin_state_up
        if parsed_args.tags is not None:
            tags = {}
            for tag in parsed_args.tags:
                tags.update(tag)
            body['tags'] = tags

        dic = network_client.update_network(
            network_id, body={'network': body}).get('network')
        columns = utils.get_columns(dic)
        obj = to_obj.Network(dic)
        data = utils.get_item_properties(
            obj, columns, formatters={'subnets': utils.format_list})
        return (columns, data)


class DeleteNetwork(command.Command):
    _description = _("Delete logical-network")
    def get_parser(self, prog_name):
        parser = super(DeleteNetwork, self).get_parser(prog_name)
        parser.add_argument(
            'network_id',
            metavar="<uuid>",
            nargs="+",
            help=("Network(s) ID to delete.")
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        for nid in parsed_args.network_id:
            network_client.delete_network(nid)
