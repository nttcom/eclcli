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
    'Policy ID',
    'Load Balancer ID',
    'Tenant ID',
    'Priority',
    'Target Group ID',
    'Backup Target Group ID',
    'Conditions',
]

ROWS_FOR_CHANGES = [
    'Current',
    'Staged',
]

ROWS_FOR_SHOW_STAGED = [
    'Priority',
    'Target Group ID',
    'Backup Target Group ID',
    'Conditions',
]


class ListRule(command.Lister):
    _description = _("List rules of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(ListRule, self).get_parser(prog_name)
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
            'Policy ID',
            'Load Balancer ID',
            'Priority',
            'Target Group ID',
            'Backup Target Group ID',
        ]
        column_headers = copy.deepcopy(columns)

        data = client.rules()

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={'Metadata': utils.format_dict},
                ) for s in data))


class ShowRule(command.ShowOne):
    _description = _("Show rule of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(ShowRule, self).\
            get_parser(prog_name)
        parser.add_argument(
            'rule',
            metavar='<rule-id>',
            help='ID of rule id to look up.')

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

        data = client.get_rule(parsed_args.rule, changes)

        setattr(data, 'conditions', json.dumps(data.conditions, indent=2))

        if changes:
            setattr(data, 'current', json.dumps(data.current, indent=2))
            setattr(data, 'staged', json.dumps(data.staged, indent=2))

        return row_headers, (utils.get_item_properties(data, rows))


class CreateRule(command.ShowOne):
    _description = _("Create new rule of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(CreateRule, self). \
            get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Name of rule'),
        )

        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description of rule'),
        )

        parser.add_argument(
            "--tags",
            help="Tags of rule"
                 " (e.g. '{\"tag1\": 1,\"tag2\": \"a\"...}' )",
            metavar='<string>'
        )

        parser.add_argument(
            '--priority',
            metavar='<priority>',
            type=int,
            help=_('Priority of the rule'),
        )

        parser.add_argument(
            '--target-group-id',
            metavar='<target-group-id>',
            required=True,
            help=_('ID of the target group that assigned to the rule'),
        )

        parser.add_argument(
            '--backup-target-group-id',
            metavar='<backup-target-group-id>',
            help=_('ID of the backup target group that assigned to the rule'),
        )

        parser.add_argument(
            '--policy-id',
            metavar='<policy-id>',
            required=True,
            help=_('ID of the policy which the rule belongs to'),
        )

        parser.add_argument(
            '--conditions',
            metavar='<conditions>',
            required=True,
            help=_("Conditions of the rules to distribute accesses to the target groups "
                   "path_patterns: URL path patterns (regular expressions) of the condition"
                   " (e.g. '{\"path_patterns\":[\"pattern1\", \"pattern2\"...]}' )"),
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

        try:
            conditions = json.loads(parsed_args.conditions)
        except Exception:
            msg = _("You must specify JSON object format to conditions")
            raise exceptions.CommandError(msg)

        data = client.create_rule(
            name=parsed_args.name,
            description=parsed_args.description,
            tags=tags,
            priority=parsed_args.priority,
            target_group_id=parsed_args.target_group_id,
            backup_target_group_id=parsed_args.backup_target_group_id,
            policy_id=parsed_args.policy_id,
            conditions=conditions,
        )

        setattr(data, 'conditions', json.dumps(data.conditions, indent=2))

        return row_headers, utils.get_item_properties(data, rows)


class DeleteRule(command.Command):
    _description = _("Delete rule of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(DeleteRule, self). \
            get_parser(prog_name)
        parser.add_argument(
            "rule",
            nargs="+",
            help="IDs of rule to be deleted",
            metavar='<rule-id>'
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna
        for rule_id in parsed_args.rule:
            client.delete_rule(rule_id)


class UpdateRule(command.ShowOne):
    _description = _("Update rule of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(UpdateRule, self). \
            get_parser(prog_name)
        parser.add_argument(
            "rule",
            help="ID of rule to be updated",
            metavar='<rule-id>'
        )

        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Name of rule'),
        )

        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description of rule'),
        )

        parser.add_argument(
            "--tags",
            help="Tags of rule"
                 " (e.g. '{\"tag1\": 1,\"tag2\": \"a\"...}' )",
            metavar='<string>'
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        rows = ROWS_FOR_SHOW
        row_headers = rows

        target = client.get_rule(parsed_args.rule)

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

        data = client.update_rule(
            parsed_args.rule, **patch)

        setattr(data, 'conditions', json.dumps(data.conditions, indent=2))

        return row_headers, utils.get_item_properties(data, rows)


class CreateStagedRuleConfiguration(command.ShowOne):
    _description = _("Create new staged rule of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(CreateStagedRuleConfiguration, self). \
            get_parser(prog_name)
        parser.add_argument(
            "rule",
            help="ID of rule to be create staged",
            metavar='<rule-id>'
        )

        parser.add_argument(
            '--priority',
            metavar='<priority>',
            type=int,
            help=_('Priority of the rule'),
        )

        parser.add_argument(
            '--target-group-id',
            metavar='<target-group-id>',
            help=_('ID of the target group that assigned to the rule'),
        )

        parser.add_argument(
            '--backup-target-group-id',
            metavar='<backup-target-group-id>',
            help=_('ID of the backup target group that assigned to the rule'),
        )

        parser.add_argument(
            '--conditions',
            metavar='<conditions>',
            help=_("Conditions of the rules to distribute accesses to the target groups "
                   "path_patterns: URL path patterns (regular expressions) of the condition"
                   " (e.g. '{\"path_patterns\":[\"pattern1\", \"pattern2\"...]}' )"),
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        rows = ROWS_FOR_SHOW_STAGED
        row_headers = rows

        try:
            conditions = json.loads(parsed_args.conditions) if parsed_args.conditions else None
        except Exception:
            msg = _("You must specify JSON object format to conditions")
            raise exceptions.CommandError(msg)

        data = client.create_staged_rule_configuration(
            parsed_args.rule,
            priority=parsed_args.priority,
            target_group_id=parsed_args.target_group_id,
            backup_target_group_id=parsed_args.backup_target_group_id,
            conditions=conditions,
        )

        setattr(data, 'conditions', json.dumps(data.conditions, indent=2))

        return row_headers, utils.get_item_properties(data, rows)


class CancelStagedRuleConfiguration(command.Command):
    _description = _("Cancel staged rule of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(CancelStagedRuleConfiguration, self). \
            get_parser(prog_name)
        parser.add_argument(
            "rule",
            help="IDs of rule to be cancel configuration",
            metavar='<rule-id>'
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna
        rule_id = parsed_args.rule
        client.cancel_staged_rule_configuration(rule_id)


class ShowStagedRuleConfiguration(command.ShowOne):
    _description = _("Show staged rule of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(ShowStagedRuleConfiguration, self).\
            get_parser(prog_name)
        parser.add_argument(
            'rule',
            metavar='<rule-id>',
            help='ID of rule id to look up.')
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        rows = ROWS_FOR_SHOW_STAGED
        row_headers = rows

        data = client.get_staged_rule_configuration(parsed_args.rule)

        setattr(data, 'conditions', json.dumps(data.conditions, indent=2))

        return row_headers, (utils.get_item_properties(data, rows))


class UpdateStagedRuleConfiguration(command.ShowOne):
    _description = _("Update staged rule of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(UpdateStagedRuleConfiguration, self). \
            get_parser(prog_name)
        parser.add_argument(
            "rule",
            help="ID of rule to be update staged",
            metavar='<rule-id>'
        )

        parser.add_argument(
            '--priority',
            metavar='<priority>',
            type=int,
            help=_('Priority of the rule'),
        )

        parser.add_argument(
            '--target-group-id',
            metavar='<target-group-id>',
            help=_('ID of the target group that assigned to the rule'),
        )

        parser.add_argument(
            '--backup-target-group-id',
            metavar='<backup-target-group-id>',
            help=_('ID of the backup target group that assigned to the rule'),
        )

        parser.add_argument(
            '--conditions',
            metavar='<conditions>',
            help=_("Conditions of the rules to distribute accesses to the target groups "
                   "path_patterns: URL path patterns (regular expressions) of the condition"
                   " (e.g. '{\"path_patterns\":[\"pattern1\", \"pattern2\"...]}' )"),
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        rows = ROWS_FOR_SHOW_STAGED
        row_headers = rows

        try:
            conditions = json.loads(parsed_args.conditions) if parsed_args.conditions else None
        except Exception:
            msg = _("You must specify JSON object format to conditions")
            raise exceptions.CommandError(msg)

        data = client.update_staged_rule_configuration(
            parsed_args.rule,
            priority=parsed_args.priority,
            target_group_id=parsed_args.target_group_id,
            backup_target_group_id=parsed_args.backup_target_group_id,
            conditions=conditions,
        )

        setattr(data, 'conditions', json.dumps(data.conditions, indent=2))

        return row_headers, utils.get_item_properties(data, rows)
