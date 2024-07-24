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
    'Port',
    'Protocol',
    'Interval',
    'Retry',
    'Timeout',
    'Path',
    'Http Status Code',
]

ROWS_FOR_CHANGES = [
    'Current',
    'Staged',
]

ROWS_FOR_SHOW_STAGED = [
    'Port',
    'Protocol',
    'Interval',
    'Retry',
    'Timeout',
    'Path',
    'Http Status Code',
]


class ListHealthMonitor(command.Lister):
    _description = _("List health-monitors of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(ListHealthMonitor, self).get_parser(prog_name)
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
            'Port',
            'Protocol',
            'Interval',
            'Retry',
            'Timeout',
            'Path',
            'Http Status Code',
        ]
        column_headers = copy.deepcopy(columns)

        data = client.health_monitors()

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={'Metadata': utils.format_dict},
                ) for s in data))


class ShowHealthMonitor(command.ShowOne):
    _description = _("Show health-monitor of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(ShowHealthMonitor, self).\
            get_parser(prog_name)
        parser.add_argument(
            'health_monitor',
            metavar='<health-monitor-id>',
            help='ID of health monitor id to look up.')

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

        data = client.get_health_monitor(parsed_args.health_monitor, changes)

        if changes:
            setattr(data, 'current', json.dumps(data.current, indent=2))
            setattr(data, 'staged', json.dumps(data.staged, indent=2))

        return row_headers, (utils.get_item_properties(data, rows))


class CreateHealthMonitor(command.ShowOne):
    _description = _("Create new health-monitor of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(CreateHealthMonitor, self). \
            get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Name of health monitor'),
        )

        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description of health monitor'),
        )

        parser.add_argument(
            "--tags",
            help="Tags of health monitor"
                 " (e.g. '{\"tag1\": 1,\"tag2\": \"a\"...}' )",
            metavar='<string>'
        )

        parser.add_argument(
            '--port',
            metavar='<port>',
            required=True,
            type=int,
            help=_('Port number of the health monitor for healthchecking'),
        )

        parser.add_argument(
            '--protocol',
            metavar='<protocol>',
            required=True,
            choices=['icmp', 'tcp', 'http', 'https'],
            help=_('Protocol of the health monitor for healthchecking'),
        )

        parser.add_argument(
            '--interval',
            metavar='<interval>',
            type=int,
            help=_('Interval of healthchecking (in seconds)'),
        )

        parser.add_argument(
            '--retry',
            metavar='<retry>',
            type=int,
            help=_('Retry of healthchecking'),
        )

        parser.add_argument(
            '--timeout',
            metavar='<timeout>',
            type=int,
            help=_('Timeout of healthchecking (in seconds)'),
        )

        parser.add_argument(
            '--path',
            metavar='<path>',
            help=_('URL path of healthchecking'),
        )

        parser.add_argument(
            '--http-status-code',
            metavar='<http-status-code>',
            help=_('HTTP status codes expected in healthchecking'),
        )

        parser.add_argument(
            '--load-balancer-id',
            metavar='<load-balancer-id>',
            required=True,
            help=_('ID of the load balancer which the health monitor belongs to'),
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

        data = client.create_health_monitor(
            name=parsed_args.name,
            description=parsed_args.description,
            tags=tags,
            port=parsed_args.port,
            protocol=parsed_args.protocol,
            interval=parsed_args.interval,
            retry=parsed_args.retry,
            timeout=parsed_args.timeout,
            path=parsed_args.path,
            http_status_code=parsed_args.http_status_code,
            load_balancer_id=parsed_args.load_balancer_id,
        )

        return row_headers, utils.get_item_properties(data, rows)


class DeleteHealthMonitor(command.Command):
    _description = _("Delete health-monitor of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(DeleteHealthMonitor, self). \
            get_parser(prog_name)
        parser.add_argument(
            "health_monitor",
            nargs="+",
            help="IDs of health monitor to be deleted",
            metavar='<health-monitor-id>'
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna
        for health_monitor_id in parsed_args.health_monitor:
            client.delete_health_monitor(health_monitor_id)


class UpdateHealthMonitor(command.ShowOne):
    _description = _("Update health-monitor of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(UpdateHealthMonitor, self). \
            get_parser(prog_name)
        parser.add_argument(
            "health_monitor",
            help="ID of health monitor to be updated",
            metavar='<health-monitor-id>'
        )

        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Name of health monitor'),
        )

        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description of health monitor'),
        )

        parser.add_argument(
            "--tags",
            help="Tags of health monitor"
                 " (e.g. '{\"tag1\": 1,\"tag2\": \"a\"...}' )",
            metavar='<string>'
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        rows = ROWS_FOR_SHOW
        row_headers = rows

        target = client.get_health_monitor(parsed_args.health_monitor)

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

        data = client.update_health_monitor(
            parsed_args.health_monitor, **patch)

        return row_headers, utils.get_item_properties(data, rows)


class CreateStagedHealthMonitorConfiguration(command.ShowOne):
    _description = _("Create new staged health-monitor of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(CreateStagedHealthMonitorConfiguration, self). \
            get_parser(prog_name)
        parser.add_argument(
            'health_monitor',
            metavar='<health-monitor-id>',
            help='ID of health monitor to create staged')

        parser.add_argument(
            '--port',
            metavar='<port>',
            type=int,
            help=_('Port number of the health monitor for healthchecking'),
        )

        parser.add_argument(
            '--protocol',
            metavar='<protocol>',
            choices=['icmp', 'tcp', 'http', 'https'],
            help=_('Protocol of the health monitor for healthchecking'),
        )

        parser.add_argument(
            '--interval',
            metavar='<interval>',
            type=int,
            help=_('Interval of healthchecking (in seconds)'),
        )

        parser.add_argument(
            '--retry',
            metavar='<retry>',
            type=int,
            help=_('Retry of healthchecking'),
        )

        parser.add_argument(
            '--timeout',
            metavar='<timeout>',
            type=int,
            help=_('Timeout of healthchecking (in seconds)'),
        )

        parser.add_argument(
            '--path',
            metavar='<path>',
            help=_('URL path of healthchecking'),
        )

        parser.add_argument(
            '--http-status-code',
            metavar='<http-status-code>',
            help=_('HTTP status codes expected in healthchecking'),
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        rows = ROWS_FOR_SHOW_STAGED
        row_headers = rows

        data = client.create_staged_health_monitor_configuration(
            parsed_args.health_monitor,
            port=parsed_args.port,
            protocol=parsed_args.protocol,
            interval=parsed_args.interval,
            retry=parsed_args.retry,
            timeout=parsed_args.timeout,
            path=parsed_args.path,
            http_status_code=parsed_args.http_status_code,
        )

        return row_headers, utils.get_item_properties(data, rows)


class CancelStagedHealthMonitorConfiguration(command.Command):
    _description = _("Cancel staged health-monitor of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(CancelStagedHealthMonitorConfiguration, self). \
            get_parser(prog_name)
        parser.add_argument(
            "health_monitor",
            help="IDs of health monitor to be cancel configuration",
            metavar='<health-monitor-id>'
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna
        health_monitor_id = parsed_args.health_monitor
        client.cancel_staged_health_monitor_configuration(health_monitor_id)


class ShowStagedHealthMonitorConfiguration(command.ShowOne):
    _description = _("Show staged health-monitor of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(ShowStagedHealthMonitorConfiguration, self).\
            get_parser(prog_name)
        parser.add_argument(
            'health_monitor',
            metavar='<health-monitor-id>',
            help='ID of health monitor id to look up.')
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        rows = ROWS_FOR_SHOW_STAGED
        row_headers = rows

        data = client.get_staged_health_monitor_configuration(parsed_args.health_monitor)

        return row_headers, (utils.get_item_properties(data, rows))


class UpdateStagedHealthMonitorConfiguration(command.ShowOne):
    _description = _("Update staged health-monitor of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(UpdateStagedHealthMonitorConfiguration, self). \
            get_parser(prog_name)
        parser.add_argument(
            'health_monitor',
            metavar='<health-monitor-id>',
            help='ID of health monitor to update staged')

        parser.add_argument(
            '--port',
            metavar='<port>',
            type=int,
            help=_('Port number of the health monitor for healthchecking'),
        )

        parser.add_argument(
            '--protocol',
            metavar='<protocol>',
            choices=['icmp', 'tcp', 'http', 'https'],
            help=_('Protocol of the health monitor for healthchecking'),
        )

        parser.add_argument(
            '--interval',
            metavar='<interval>',
            type=int,
            help=_('Interval of healthchecking (in seconds)'),
        )

        parser.add_argument(
            '--retry',
            metavar='<retry>',
            type=int,
            help=_('Retry of healthchecking'),
        )

        parser.add_argument(
            '--timeout',
            metavar='<timeout>',
            type=int,
            help=_('Timeout of healthchecking (in seconds)'),
        )

        parser.add_argument(
            '--path',
            metavar='<path>',
            help=_('URL path of healthchecking'),
        )

        parser.add_argument(
            '--http-status-code',
            metavar='<http-status-code>',
            help=_('HTTP status codes expected in healthchecking'),
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        rows = ROWS_FOR_SHOW_STAGED
        row_headers = rows

        data = client.update_staged_health_monitor_configuration(
            parsed_args.health_monitor,
            port=parsed_args.port,
            protocol=parsed_args.protocol,
            interval=parsed_args.interval,
            retry=parsed_args.retry,
            timeout=parsed_args.timeout,
            path=parsed_args.path,
            http_status_code=parsed_args.http_status_code,
        )

        return row_headers, utils.get_item_properties(data, rows)
