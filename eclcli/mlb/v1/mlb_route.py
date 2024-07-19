# -*- coding: utf-8 -*-

try:
    import json
except ImportError:
    import simplejson as json

import copy
import json_merge_patch as jmp
from eclcli.common import command, exceptions, utils
from eclcli.i18n import _  # noqa

ROWS_FOR_SHOW = [
    'ID',
    'Name',
    'Description',
    'Tags',
    'Configuration Status',
    'Operation Status',
    'Destination CIDR',
    'Load Balancer ID',
    'Tenant ID',
    'Next hop IP Address',
]

ROWS_FOR_CHANGES = [
    'Current',
    'Staged',
]

ROWS_FOR_SHOW_STAGED = [
    'Next hop IP Address',
]


class ListRoute(command.Lister):
    _description = _("List routes of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(ListRoute, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        columns = [
            'ID',
            'Name',
            'Description',
            'Tags',
            'Configuration Status',
            'Operation Status',
            'Destination CIDR',
            'Load Balancer ID',
            'Next hop IP Address',
        ]
        column_headers = copy.deepcopy(columns)

        data = client.routes()

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={'Metadata': utils.format_dict},
                ) for s in data))


class ShowRoute(command.ShowOne):
    _description = _("Show route of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(ShowRoute, self).\
            get_parser(prog_name)
        parser.add_argument(
            'route',
            metavar='<route-id>',
            help='ID of route id to look up.')

        parser.add_argument(
            '--changes',
            action='store_true',
            help=_('current and staged are returned in response body'),
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna
        changes = parsed_args.changes
        rows = ROWS_FOR_SHOW + ROWS_FOR_CHANGES if changes else ROWS_FOR_SHOW
        row_headers = rows

        data = client.get_route(parsed_args.route, changes)

        if changes:
            setattr(data, 'current', json.dumps(data.current, indent=2))
            setattr(data, 'staged', json.dumps(data.staged, indent=2))

        return row_headers, (utils.get_item_properties(data, rows))


class CreateRoute(command.ShowOne):
    _description = _("Create new route of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(CreateRoute, self). \
            get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Name of route'),
        )

        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description of route'),
        )

        parser.add_argument(
            "--tags",
            help="Tags of route"
                 " (e.g. '{\"tag1\": 1,\"tag2\": \"a\"...}' )",
            metavar='<string>'
        )

        parser.add_argument(
            '--destination-cidr',
            metavar='<destination-cidr>',
            required=True,
            help=_('CIDR of destination for the (static) route'),
        )

        parser.add_argument(
            '--next-hop-ip-address',
            metavar='<next-hop-ip-address>',
            required=True,
            help=_('IP address of next hop for the (static) route'),
        )

        parser.add_argument(
            '--load-balancer-id',
            metavar='<load-balancer-id>',
            required=True,
            help=_('ID of the load balancer which the (static) route belongs to'),
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        rows = ROWS_FOR_SHOW
        row_headers = rows

        tags = parsed_args.tags or '{}'
        try:
            tags = json.loads(tags)
        except Exception:
            msg = _("You must specify JSON object format to tags")
            raise exceptions.CommandError(msg)

        data = client.create_route(
            name=parsed_args.name,
            description=parsed_args.description,
            tags=tags,
            destination_cidr=parsed_args.destination_cidr,
            next_hop_ip_address=parsed_args.next_hop_ip_address,
            load_balancer_id=parsed_args.load_balancer_id,
        )

        return row_headers, utils.get_item_properties(data, rows)


class DeleteRoute(command.Command):
    _description = _("Delete route of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(DeleteRoute, self). \
            get_parser(prog_name)
        parser.add_argument(
            "route",
            nargs="+",
            help="IDs of route to be deleted",
            metavar='<route-id>'
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna
        for route_id in parsed_args.route:
            client.delete_route(route_id)


class UpdateRoute(command.ShowOne):
    _description = _("Update route of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(UpdateRoute, self). \
            get_parser(prog_name)
        parser.add_argument(
            "route",
            help="ID of route to be updated",
            metavar='<route-id>'
        )

        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Name of route'),
        )

        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description of route'),
        )

        parser.add_argument(
            "--tags",
            help="Tags of route"
                 " (e.g. '{\"tag1\": 1,\"tag2\": \"a\"...}' )",
            metavar='<string>'
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        rows = ROWS_FOR_SHOW
        row_headers = rows

        target = client.get_route(parsed_args.route)

        # serialize request parameter as JSON
        requested_param = {}
        if hasattr(parsed_args, 'name') and parsed_args.name is not None:
            requested_param['name'] = parsed_args.name
        if hasattr(parsed_args, 'description') and \
                parsed_args.description is not None:
            requested_param['description'] = parsed_args.description
        if hasattr(parsed_args, 'tags') and parsed_args.tags is not None:
            tags = parsed_args.tags or '{}'
            try:
                requested_param['tags'] = json.loads(tags)
            except Exception:
                msg = _("You must specify JSON object format")
                raise exceptions.CommandError(msg)

        # serialize current parameter as JSON
        current_param = {
            'name': target.name,
            'description': target.description,
            'tags': target.tags,
        }
        origin_param = copy.deepcopy(current_param)
        merged_param = jmp.merge(current_param, requested_param)
        patch = jmp.create_patch(origin_param, merged_param)

        if 'tags' in requested_param and requested_param['tags'] != target.tags:
            patch['tags'] = requested_param['tags']

        if not patch:
            msg = _('No change will be expected')
            raise exceptions.CommandError(msg)

        data = client.update_route(
            parsed_args.route, **patch)

        return row_headers, utils.get_item_properties(data, rows)


class CreateStagedRouteConfiguration(command.ShowOne):
    _description = _("Create new staged route of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(CreateStagedRouteConfiguration, self). \
            get_parser(prog_name)
        parser.add_argument(
            "route",
            help="ID of route to be create staged",
            metavar='<route-id>'
        )

        parser.add_argument(
            '--next-hop-ip-address',
            metavar='<next-hop-ip-address>',
            help=_('IP address of next hop for the (static) route'),
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        rows = ROWS_FOR_SHOW_STAGED
        row_headers = rows

        data = client.create_staged_route_configuration(
            parsed_args.route,
            next_hop_ip_address=parsed_args.next_hop_ip_address
        )

        return row_headers, utils.get_item_properties(data, rows)


class CancelStagedRouteConfiguration(command.Command):
    _description = _("Cancel staged route of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(CancelStagedRouteConfiguration, self). \
            get_parser(prog_name)
        parser.add_argument(
            "route",
            help="IDs of route to be cancel configuration",
            metavar='<route-id>'
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna
        route_id = parsed_args.route
        client.cancel_staged_route_configuration(route_id)


class ShowStagedRouteConfiguration(command.ShowOne):
    _description = _("Show staged route of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(ShowStagedRouteConfiguration, self).\
            get_parser(prog_name)
        parser.add_argument(
            'route',
            metavar='<route-id>',
            help='ID of route id to look up.')
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        rows = ROWS_FOR_SHOW_STAGED
        row_headers = rows

        data = client.get_staged_route_configuration(parsed_args.route)

        return row_headers, (utils.get_item_properties(data, rows))


class UpdateStagedRouteConfiguration(command.ShowOne):
    _description = _("Update staged route of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(UpdateStagedRouteConfiguration, self). \
            get_parser(prog_name)
        parser.add_argument(
            "route",
            help="ID of route to be update staged",
            metavar='<route-id>'
        )

        parser.add_argument(
            '--next-hop-ip-address',
            metavar='<next-hop-ip-address>',
            help=_('IP address of next hop for the (static) route'),
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        rows = ROWS_FOR_SHOW_STAGED
        row_headers = rows

        data = client.update_staged_route_configuration(
            parsed_args.route,
            next_hop_ip_address=parsed_args.next_hop_ip_address
        )

        return row_headers, utils.get_item_properties(data, rows)
