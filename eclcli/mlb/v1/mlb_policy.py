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
    'Algorithm',
    'Persistence',
    'Sorry page url',
    'Source NAT',
    'Certificate ID',
    'Health Monitor ID',
    'Listener ID',
    'Default Target Group ID',
    'TLS Policy ID',
]

ROWS_FOR_CHANGES = [
    'Current',
    'Staged',
]

ROWS_FOR_SHOW_STAGED = [
    'Algorithm',
    'Persistence',
    'Sorry page url',
    'Source NAT',
    'Certificate ID',
    'Health Monitor ID',
    'Listener ID',
    'Default Target Group ID',
    'TLS Policy ID',
]


class ListPolicy(command.Lister):

    def get_parser(self, prog_name):
        parser = super(ListPolicy, self).get_parser(prog_name)
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
            'Algorithm',
            'Persistence',
            'Sorry page url',
            'Source NAT',
            'Certificate ID',
            'Health Monitor ID',
            'Listener ID',
            'Default Target Group ID',
            'TLS Policy ID',
        ]
        column_headers = copy.deepcopy(columns)

        data = client.policies()

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={'Metadata': utils.format_dict},
                ) for s in data))


class ShowPolicy(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(ShowPolicy, self).\
            get_parser(prog_name)
        parser.add_argument(
            'policy',
            metavar='<policy-id>',
            help='ID of policy id to look up.')

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

        data = client.get_policy(parsed_args.policy, changes)

        if changes:
            setattr(data, 'current', json.dumps(data.current, indent=2))
            setattr(data, 'staged', json.dumps(data.staged, indent=2))

        return row_headers, (utils.get_item_properties(data, rows))


class CreatePolicy(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(CreatePolicy, self). \
            get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Name of policy'),
        )

        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description of policy'),
        )

        parser.add_argument(
            "--tags",
            help="Tags of policy"
                 " (e.g. '{\"tag1\": 1,\"tag2\": \"a\"...}' )",
            metavar='<string>'
        )

        parser.add_argument(
            '--algorithm',
            metavar='<algorithm>',
            choices=['round-robin',
                     'weighted-round-robin',
                     'least-connection',
                     'weighted-least-connection',
                     'source-ip-port-hash'],
            help=_('Load balancing algorithm (method) of the policy'),
        )

        parser.add_argument(
            '--persistence',
            metavar='<persistence>',
            choices=['none',
                     'source-ip',
                     'cookie'],
            help=_('Persistence setting of the policy'),
        )

        parser.add_argument(
            '--sorry-page-url',
            metavar='<sorry-page-url>',
            help=_('URL of the sorry page to which accesses are redirected '
                   'when all members in the target group are down'),
        )

        parser.add_argument(
            '--source-nat',
            metavar='<source-nat>',
            choices=['disable',
                     'enable'],
            help=_('Source NAT setting of the policy'),
        )

        parser.add_argument(
            '--certificate-id',
            metavar='<certificate-id>',
            help=_('ID of the certificate that assigned to the policy'),
        )

        parser.add_argument(
            '--health-monitor-id',
            metavar='<health-monitor-id>',
            required=True,
            help=_('ID of the health monitor that assigned to the policy'),
        )

        parser.add_argument(
            '--listener-id',
            metavar='<listener-id>',
            required=True,
            help=_('ID of the listener that assigned to the policy'),
        )

        parser.add_argument(
            '--default-target-group-id',
            metavar='<default-target-group-id>',
            required=True,
            help=_('ID of the default target group that assigned to the policy'),
        )

        parser.add_argument(
            '--tls-policy-id',
            metavar='<tls-policy-id>',
            help=_('ID of the TLS policy that assigned to the policy'),
        )

        parser.add_argument(
            '--load-balancer-id',
            metavar='<load-balancer-id>',
            required=True,
            help=_('ID of the load balancer which the policy belongs to'),
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

        data = client.create_policy(
            name=parsed_args.name,
            description=parsed_args.description,
            tags=tags,
            algorithm=parsed_args.algorithm,
            persistence=parsed_args.persistence,
            sorry_page_url=parsed_args.sorry_page_url,
            certificate_id=parsed_args.certificate_id,
            source_nat=parsed_args.source_nat,
            health_monitor_id=parsed_args.health_monitor_id,
            listener_id=parsed_args.listener_id,
            default_target_group_id=parsed_args.default_target_group_id,
            tls_policy_id=parsed_args.tls_policy_id,
            load_balancer_id=parsed_args.load_balancer_id,
        )

        return row_headers, utils.get_item_properties(data, rows)


class DeletePolicy(command.Command):

    def get_parser(self, prog_name):
        parser = super(DeletePolicy, self). \
            get_parser(prog_name)
        parser.add_argument(
            "policy",
            nargs="+",
            help="IDs of policy to be deleted",
            metavar='<policy-id>'
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna
        for policy_id in parsed_args.policy:
            client.delete_policy(policy_id)


class UpdatePolicy(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(UpdatePolicy, self). \
            get_parser(prog_name)
        parser.add_argument(
            "policy",
            help="ID of policy to be updated",
            metavar='<policy-id>'
        )

        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Name of policy'),
        )

        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description of policy'),
        )

        parser.add_argument(
            "--tags",
            help="Tags of policy"
                 " (e.g. '{\"tag1\": 1,\"tag2\": \"a\"...}' )",
            metavar='<string>'
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        rows = ROWS_FOR_SHOW
        row_headers = rows

        target = client.get_policy(parsed_args.policy)

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

        data = client.update_policy(
            parsed_args.policy, **patch)

        return row_headers, utils.get_item_properties(data, rows)


class CreateStagedPolicyConfiguration(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(CreateStagedPolicyConfiguration, self). \
            get_parser(prog_name)
        parser.add_argument(
            "policy",
            help="ID of policy to be create staged",
            metavar='<policy-id>'
        )

        parser.add_argument(
            '--algorithm',
            metavar='<algorithm>',
            choices=['round-robin',
                     'weighted-round-robin',
                     'least-connection',
                     'weighted-least-connection',
                     'source-ip-port-hash'],
            help=_('Load balancing algorithm (method) of the policy'),
        )

        parser.add_argument(
            '--persistence',
            metavar='<persistence>',
            choices=['none',
                     'source-ip',
                     'cookie'],
            help=_('Persistence setting of the policy'),
        )

        parser.add_argument(
            '--sorry-page-url',
            metavar='<sorry-page-url>',
            help=_('URL of the sorry page to which accesses are redirected '
                   'when all members in the target group are down'),
        )

        parser.add_argument(
            '--source-nat',
            metavar='<source-nat>',
            choices=['disable',
                     'enable'],
            help=_('Source NAT setting of the policy'),
        )

        parser.add_argument(
            '--certificate-id',
            metavar='<certificate-id>',
            help=_('ID of the certificate that assigned to the policy'),
        )

        parser.add_argument(
            '--health-monitor-id',
            metavar='<health-monitor-id>',
            help=_('ID of the health monitor that assigned to the policy'),
        )

        parser.add_argument(
            '--listener-id',
            metavar='<listener-id>',
            help=_('ID of the listener that assigned to the policy'),
        )

        parser.add_argument(
            '--default-target-group-id',
            metavar='<default-target-group-id>',
            help=_('ID of the default target group that assigned to the policy'),
        )

        parser.add_argument(
            '--tls-policy-id',
            metavar='<tls-policy-id>',
            help=_('ID of the TLS policy that assigned to the policy'),
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        rows = ROWS_FOR_SHOW_STAGED
        row_headers = rows

        data = client.create_staged_policy_configuration(
            parsed_args.policy,
            algorithm=parsed_args.algorithm,
            persistence=parsed_args.persistence,
            sorry_page_url=parsed_args.sorry_page_url,
            certificate_id=parsed_args.certificate_id,
            source_nat=parsed_args.source_nat,
            health_monitor_id=parsed_args.health_monitor_id,
            listener_id=parsed_args.listener_id,
            default_target_group_id=parsed_args.default_target_group_id,
            tls_policy_id=parsed_args.tls_policy_id,
        )

        return row_headers, utils.get_item_properties(data, rows)


class CancelStagedPolicyConfiguration(command.Command):

    def get_parser(self, prog_name):
        parser = super(CancelStagedPolicyConfiguration, self). \
            get_parser(prog_name)
        parser.add_argument(
            "policy",
            help="IDs of policy to be cancel configuration",
            metavar='<policy-id>'
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna
        policy_id = parsed_args.policy
        client.cancel_staged_policy_configuration(policy_id)


class ShowStagedPolicyConfiguration(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(ShowStagedPolicyConfiguration, self).\
            get_parser(prog_name)
        parser.add_argument(
            'policy',
            metavar='<policy-id>',
            help='ID of policy id to look up.')
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        rows = ROWS_FOR_SHOW_STAGED
        row_headers = rows

        data = client.get_staged_policy_configuration(parsed_args.policy)

        return row_headers, (utils.get_item_properties(data, rows))


class UpdateStagedPolicyConfiguration(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(UpdateStagedPolicyConfiguration, self). \
            get_parser(prog_name)
        parser.add_argument(
            "policy",
            help="ID of policy to be update staged",
            metavar='<policy-id>'
        )

        parser.add_argument(
            '--algorithm',
            metavar='<algorithm>',
            choices=['round-robin',
                     'weighted-round-robin',
                     'least-connection',
                     'weighted-least-connection',
                     'source-ip-port-hash'],
            help=_('Load balancing algorithm (method) of the policy'),
        )

        parser.add_argument(
            '--persistence',
            metavar='<persistence>',
            choices=['none',
                     'source-ip',
                     'cookie'],
            help=_('Persistence setting of the policy'),
        )

        parser.add_argument(
            '--sorry-page-url',
            metavar='<sorry-page-url>',
            help=_('URL of the sorry page to which accesses are redirected '
                   'when all members in the target group are down'),
        )

        parser.add_argument(
            '--source-nat',
            metavar='<source-nat>',
            choices=['disable',
                     'enable'],
            help=_('Source NAT setting of the policy'),
        )

        parser.add_argument(
            '--certificate-id',
            metavar='<certificate-id>',
            help=_('ID of the certificate that assigned to the policy'),
        )

        parser.add_argument(
            '--health-monitor-id',
            metavar='<health-monitor-id>',
            help=_('ID of the health monitor that assigned to the policy'),
        )

        parser.add_argument(
            '--listener-id',
            metavar='<listener-id>',
            help=_('ID of the listener that assigned to the policy'),
        )

        parser.add_argument(
            '--default-target-group-id',
            metavar='<default-target-group-id>',
            help=_('ID of the default target group that assigned to the policy'),
        )

        parser.add_argument(
            '--tls-policy-id',
            metavar='<tls-policy-id>',
            help=_('ID of the TLS policy that assigned to the policy'),
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        rows = ROWS_FOR_SHOW_STAGED
        row_headers = rows

        data = client.update_staged_policy_configuration(
            parsed_args.policy,
            algorithm=parsed_args.algorithm,
            persistence=parsed_args.persistence,
            sorry_page_url=parsed_args.sorry_page_url,
            certificate_id=parsed_args.certificate_id,
            source_nat=parsed_args.source_nat,
            health_monitor_id=parsed_args.health_monitor_id,
            listener_id=parsed_args.listener_id,
            default_target_group_id=parsed_args.default_target_group_id,
            tls_policy_id=parsed_args.tls_policy_id,
        )

        return row_headers, utils.get_item_properties(data, rows)
