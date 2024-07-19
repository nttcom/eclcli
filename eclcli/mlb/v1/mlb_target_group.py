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
    'Members',
]

ROWS_FOR_CHANGES = [
    'Current',
    'Staged',
]

ROWS_FOR_SHOW_STAGED = [
    'Members',
]


class ListTargetGroup(command.Lister):
    _description = _("List target-groups of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(ListTargetGroup, self).get_parser(prog_name)
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
        ]
        column_headers = copy.deepcopy(columns)

        data = client.target_groups()

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={'Metadata': utils.format_dict},
                ) for s in data))


class ShowTargetGroup(command.ShowOne):
    _description = _("Show target-group of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(ShowTargetGroup, self).\
            get_parser(prog_name)
        parser.add_argument(
            'target_group',
            metavar='<target-group-id>',
            help='ID of target group id to look up.')

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

        data = client.get_target_group(parsed_args.target_group, changes)

        setattr(data, 'members', json.dumps(data.members, indent=2))

        if changes:
            setattr(data, 'current', json.dumps(data.current, indent=2))
            setattr(data, 'staged', json.dumps(data.staged, indent=2))

        return row_headers, (utils.get_item_properties(data, rows))


class CreateTargetGroup(command.ShowOne):
    _description = _("Create new target-group of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(CreateTargetGroup, self). \
            get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Name of target group'),
        )

        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description of target group'),
        )

        parser.add_argument(
            "--tags",
            help="Tags of target group"
                 " (e.g. '{\"tag1\": 1,\"tag2\": \"a\"...}' )",
            metavar='<string>'
        )

        parser.add_argument(
            '--load-balancer-id',
            metavar='<load-balancer-id>',
            required=True,
            help=_('ID of the load balancer which the target group belongs to'),
        )

        parser.add_argument(
            '--members',
            metavar="<ip-address=ip-addr,"
                    "port=port,"
                    "weight=weight>",
            required=True,
            action='store',
            nargs='+',
            help=_("Members (real servers) of the target group"
                   "ip-address: IP address of the member (real server), "
                   "port: Port number of the member (real server), "
                   "weight: Weight for the member (real server). "
                   )
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

        members = []
        valid_keys = ['ip-address', 'port', 'weight']
        key_map = {'ip-address': 'ip_address',
                   'port': 'port',
                   'weight': 'weight'}
        for member_str in parsed_args.members:
            member_info = utils.parse_mlb_params(member_str, valid_keys, key_map)
            if member_info.get('port'):
                try:
                    member_info['port'] = int(member_info['port'])
                except ValueError:
                    msg = _("You must specify integer to port")
                    raise exceptions.CommandError(msg)

            if member_info.get('weight'):
                try:
                    member_info['weight'] = int(member_info['weight'])
                except ValueError:
                    msg = _("You must specify integer to weight")
                    raise exceptions.CommandError(msg)

            members.append(member_info)

        data = client.create_target_group(
            name=parsed_args.name,
            description=parsed_args.description,
            tags=tags,
            load_balancer_id=parsed_args.load_balancer_id,
            members=members,
        )

        setattr(data, 'members', json.dumps(data.members, indent=2))

        return row_headers, utils.get_item_properties(data, rows)


class DeleteTargetGroup(command.Command):
    _description = _("Delete target-group of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(DeleteTargetGroup, self). \
            get_parser(prog_name)
        parser.add_argument(
            "target_group",
            nargs="+",
            help="IDs of target group to be deleted",
            metavar='<target-group-id>'
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna
        for target_group_id in parsed_args.target_group:
            client.delete_target_group(target_group_id)


class UpdateTargetGroup(command.ShowOne):
    _description = _("Update target-group of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(UpdateTargetGroup, self). \
            get_parser(prog_name)
        parser.add_argument(
            "target_group",
            help="ID of target group to be updated",
            metavar='<target-group-id>'
        )

        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Name of target group'),
        )

        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description of target group'),
        )

        parser.add_argument(
            "--tags",
            help="Tags of target group"
                 " (e.g. '{\"tag1\": 1,\"tag2\": \"a\"...}' )",
            metavar='<string>'
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        rows = ROWS_FOR_SHOW
        row_headers = rows

        target = client.get_target_group(parsed_args.target_group)

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

        data = client.update_target_group(
            parsed_args.target_group, **patch)

        setattr(data, 'members', json.dumps(data.members, indent=2))

        return row_headers, utils.get_item_properties(data, rows)


class CreateStagedTargetGroupConfiguration(command.ShowOne):
    _description = _("Create new staged target-group of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(CreateStagedTargetGroupConfiguration, self). \
            get_parser(prog_name)
        parser.add_argument(
            'target_group',
            metavar='<target-group-id>',
            help='ID of target group to create staged')

        parser.add_argument(
            '--members',
            metavar="<ip-address=ip-addr,"
                    "port=port,"
                    "weight=weight>",
            action='store',
            nargs='+',
            help=_("Members (real servers) of the target group"
                   "ip-address: IP address of the member (real server), "
                   "port: Port number of the member (real server), "
                   "weight: Weight for the member (real server). "
                   )
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        rows = ROWS_FOR_SHOW_STAGED
        row_headers = rows

        members = []
        valid_keys = ['ip-address', 'port', 'weight']
        key_map = {'ip-address': 'ip_address',
                   'port': 'port',
                   'weight': 'weight'}
        for member_str in parsed_args.members:
            member_info = utils.parse_mlb_params(member_str, valid_keys, key_map)

            if member_info.get('port'):
                try:
                    member_info['port'] = int(member_info['port'])
                except ValueError:
                    msg = _("You must specify integer to port")
                    raise exceptions.CommandError(msg)

            if member_info.get('weight'):
                try:
                    member_info['weight'] = int(member_info['weight'])
                except ValueError:
                    msg = _("You must specify integer to weight")
                    raise exceptions.CommandError(msg)

            members.append(member_info)

        data = client.create_staged_target_group_configuration(
            parsed_args.target_group,
            members=members,
        )

        setattr(data, 'members', json.dumps(data.members, indent=2))

        return row_headers, utils.get_item_properties(data, rows)


class CancelStagedTargetGroupConfiguration(command.Command):
    _description = _("Cancel staged target-group of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(CancelStagedTargetGroupConfiguration, self). \
            get_parser(prog_name)
        parser.add_argument(
            "target_group",
            help="IDs of target group to be cancel configuration",
            metavar='<target-group-id>'
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna
        target_group_id = parsed_args.target_group
        client.cancel_staged_target_group_configuration(target_group_id)


class ShowStagedTargetGroupConfiguration(command.ShowOne):
    _description = _("Show staged target-group of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(ShowStagedTargetGroupConfiguration, self).\
            get_parser(prog_name)
        parser.add_argument(
            'target_group',
            metavar='<target-group-id>',
            help='ID of target group id to look up.')
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        rows = ROWS_FOR_SHOW_STAGED
        row_headers = rows

        data = client.get_staged_target_group_configuration(parsed_args.target_group)

        setattr(data, 'members', json.dumps(data.members, indent=2))

        return row_headers, (utils.get_item_properties(data, rows))


class UpdateStagedTargetGroupConfiguration(command.ShowOne):
    _description = _("Update staged target-group of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(UpdateStagedTargetGroupConfiguration, self). \
            get_parser(prog_name)
        parser.add_argument(
            'target_group',
            metavar='<target-group-id>',
            help='ID of target group to update staged')

        parser.add_argument(
            '--members',
            metavar="<ip-address=ip-addr,"
                    "port=port,"
                    "weight=weight>",
            action='store',
            nargs='+',
            help=_("Members (real servers) of the target group"
                   "ip-address: IP address of the member (real server), "
                   "port: Port number of the member (real server), "
                   "weight: Weight for the member (real server). "
                   )
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        rows = ROWS_FOR_SHOW_STAGED
        row_headers = rows

        members = []
        valid_keys = ['ip-address', 'port', 'weight']
        key_map = {'ip-address': 'ip_address',
                   'port': 'port',
                   'weight': 'weight'}
        for member_str in parsed_args.members:
            member_info = utils.parse_mlb_params(member_str, valid_keys, key_map)

            if member_info.get('port'):
                try:
                    member_info['port'] = int(member_info['port'])
                except ValueError:
                    msg = _("You must specify integer to port")
                    raise exceptions.CommandError(msg)

            if member_info.get('weight'):
                try:
                    member_info['weight'] = int(member_info['weight'])
                except ValueError:
                    msg = _("You must specify integer to weight")
                    raise exceptions.CommandError(msg)

            members.append(member_info)

        data = client.update_staged_target_group_configuration(
            parsed_args.target_group,
            members=members
        )

        setattr(data, 'members', json.dumps(data.members, indent=2))

        return row_headers, utils.get_item_properties(data, rows)
