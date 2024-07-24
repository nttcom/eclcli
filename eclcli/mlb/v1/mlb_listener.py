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
    'Load Balancer ID',
    'Tenant ID',
    'IP Address',
    'Port',
    'Protocol',
]

ROWS_FOR_CHANGES = [
    'Current',
    'Staged',
]

ROWS_FOR_SHOW_STAGED = [
    'IP Address',
    'Port',
    'Protocol',
]


class ListListener(command.Lister):
    _description = _("List listeners of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(ListListener, self).get_parser(prog_name)
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
            'Load Balancer ID',
            'IP Address',
            'Port',
            'Protocol',
        ]
        column_headers = copy.deepcopy(columns)

        data = client.listeners()

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={'Metadata': utils.format_dict},
                ) for s in data))


class ShowListener(command.ShowOne):
    _description = _("Show listener of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(ShowListener, self).\
            get_parser(prog_name)
        parser.add_argument(
            'listener',
            metavar='<listener-id>',
            help='ID of listener id to look up.')

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

        data = client.get_listener(parsed_args.listener, changes)

        if changes:
            setattr(data, 'current', json.dumps(data.current, indent=2))
            setattr(data, 'staged', json.dumps(data.staged, indent=2))

        return row_headers, (utils.get_item_properties(data, rows))


class CreateListener(command.ShowOne):
    _description = _("Create new listener of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(CreateListener, self). \
            get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Name of listener'),
        )

        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description of listener'),
        )

        parser.add_argument(
            "--tags",
            help="Tags of listener"
                 " (e.g. '{\"tag1\": 1,\"tag2\": \"a\"...}' )",
            metavar='<string>'
        )

        parser.add_argument(
            '--ip-address',
            metavar='<ip-address>',
            required=True,
            help=_('IP address of the listener for listening'),
        )

        parser.add_argument(
            '--port',
            metavar='<port>',
            required=True,
            type=int,
            help=_('Port number of the listener for listening'),
        )

        parser.add_argument(
            '--protocol',
            metavar='<protocol>',
            required=True,
            choices=['icmp', 'tcp', 'http', 'https'],
            help=_('Protocol of the listener for listening'),
        )

        parser.add_argument(
            '--load-balancer-id',
            metavar='<load-balancer-id>',
            required=True,
            help=_('ID of the load balancer which the listener belongs to'),
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

        data = client.create_listener(
            name=parsed_args.name,
            description=parsed_args.description,
            tags=tags,
            ip_address=parsed_args.ip_address,
            port=parsed_args.port,
            protocol=parsed_args.protocol,
            load_balancer_id=parsed_args.load_balancer_id,
        )

        return row_headers, utils.get_item_properties(data, rows)


class DeleteListener(command.Command):
    _description = _("Delete listener of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(DeleteListener, self). \
            get_parser(prog_name)
        parser.add_argument(
            "listener",
            nargs="+",
            help="IDs of listener to be deleted",
            metavar='<listener-id>'
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna
        for listener_id in parsed_args.listener:
            client.delete_listener(listener_id)


class UpdateListener(command.ShowOne):
    _description = _("Update listener of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(UpdateListener, self). \
            get_parser(prog_name)
        parser.add_argument(
            "listener",
            help="ID of listener to be updated",
            metavar='<listener-id>'
        )

        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Name of listener'),
        )

        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description of listener'),
        )

        parser.add_argument(
            "--tags",
            help="Tags of listener"
                 " (e.g. '{\"tag1\": 1,\"tag2\": \"a\"...}' )",
            metavar='<string>'
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        rows = ROWS_FOR_SHOW
        row_headers = rows

        target = client.get_listener(parsed_args.listener)

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

        data = client.update_listener(
            parsed_args.listener, **patch)

        return row_headers, utils.get_item_properties(data, rows)


class CreateStagedListenerConfiguration(command.ShowOne):
    _description = _("Create new staged listener of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(CreateStagedListenerConfiguration, self). \
            get_parser(prog_name)
        parser.add_argument(
            'listener',
            metavar='<listener-id>',
            help='ID of listener to create staged')

        parser.add_argument(
            '--ip-address',
            metavar='<ip-address>',
            help=_('IP address of the listener for listening'),
        )

        parser.add_argument(
            '--port',
            metavar='<port>',
            type=int,
            help=_('Port number of the listener for listening'),
        )

        parser.add_argument(
            '--protocol',
            metavar='<protocol>',
            choices=['icmp', 'tcp', 'http', 'https'],
            help=_('Protocol of the listener for listening'),
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        rows = ROWS_FOR_SHOW_STAGED
        row_headers = rows

        data = client.create_staged_listener_configuration(
            parsed_args.listener,
            ip_address=parsed_args.ip_address,
            port=parsed_args.port,
            protocol=parsed_args.protocol,
        )

        return row_headers, utils.get_item_properties(data, rows)


class CancelStagedListenerConfiguration(command.Command):
    _description = _("Cancel staged listener of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(CancelStagedListenerConfiguration, self). \
            get_parser(prog_name)
        parser.add_argument(
            "listener",
            help="IDs of listener to be cancel configuration",
            metavar='<listener-id>'
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna
        listener_id = parsed_args.listener
        client.cancel_staged_listener_configuration(listener_id)


class ShowStagedListenerConfiguration(command.ShowOne):
    _description = _("Show staged listener of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(ShowStagedListenerConfiguration, self).\
            get_parser(prog_name)
        parser.add_argument(
            'listener',
            metavar='<listener-id>',
            help='ID of listener id to look up.')
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        rows = ROWS_FOR_SHOW_STAGED
        row_headers = rows

        data = client.get_staged_listener_configuration(parsed_args.listener)

        return row_headers, (utils.get_item_properties(data, rows))


class UpdateStagedListenerConfiguration(command.ShowOne):
    _description = _("Update staged listener of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(UpdateStagedListenerConfiguration, self). \
            get_parser(prog_name)
        parser.add_argument(
            'listener',
            metavar='<listener-id>',
            help='ID of listener to update staged')

        parser.add_argument(
            '--ip-address',
            metavar='<ip-address>',
            help=_('IP address of the listener for listening'),
        )

        parser.add_argument(
            '--port',
            metavar='<port>',
            type=int,
            help=_('Port number of the listener for listening'),
        )

        parser.add_argument(
            '--protocol',
            metavar='<protocol>',
            choices=['icmp', 'tcp', 'http', 'https'],
            help=_('Protocol of the listener for listening'),
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        rows = ROWS_FOR_SHOW_STAGED
        row_headers = rows

        data = client.update_staged_listener_configuration(
            parsed_args.listener,
            ip_address=parsed_args.ip_address,
            port=parsed_args.port,
            protocol=parsed_args.protocol,
        )

        return row_headers, utils.get_item_properties(data, rows)
