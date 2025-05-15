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
    'Monitoring Status',
    'Operation Status',
    'Primary Availability Zone',
    'Secondary Availability Zone',
    'Active Availability Zone',
    'Revision',
    'Plan ID',
    'Plan Name',
    'Tenant ID',
    'Syslog Servers',
    'Interfaces',
]

ROWS_FOR_CHANGES = [
    'Current',
    'Staged',
]

ROWS_FOR_SHOW_STAGED = [
    'Syslog Servers',
    'Interfaces',
]


class ListLoadBalancer(command.Lister):
    _description = _("List load-balancers")

    def get_parser(self, prog_name):
        parser = super(ListLoadBalancer, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        columns = [
            'ID',
            'Name',
            'Description',
            'Tags',
            'Configuration Status',
            'Monitoring Status',
            'Operation Status',
            'Primary Availability Zone',
            'Secondary Availability Zone',
            'Active Availability Zone',
            'Revision',
            'Plan ID',
            'Plan Name',
        ]
        column_headers = copy.deepcopy(columns)

        data = client.load_balancers()

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={'Metadata': utils.format_dict},
                ) for s in data))


class ShowLoadBalancer(command.ShowOne):
    _description = _("Show load-balancer")

    def get_parser(self, prog_name):
        parser = super(ShowLoadBalancer, self).\
            get_parser(prog_name)
        parser.add_argument(
            'load_balancer',
            metavar='<load-balancer-id>',
            help='ID of load balancer id to look up.')

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

        data = client.get_load_balancer(parsed_args.load_balancer, changes)
        setattr(data, 'interfaces', json.dumps(data.interfaces, indent=2))
        setattr(data, 'syslog_servers', json.dumps(data.syslog_servers, indent=2))

        if changes:
            setattr(data, 'current', json.dumps(data.current, indent=2))
            setattr(data, 'staged', json.dumps(data.staged, indent=2))

        return row_headers, (utils.get_item_properties(data, rows))


class CreateLoadBalancer(command.ShowOne):
    _description = _("Create new load-balancer")

    def get_parser(self, prog_name):
        parser = super(CreateLoadBalancer, self). \
            get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Name of load balancer'),
        )

        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description of load balancer'),
        )

        parser.add_argument(
            "--tags",
            help="Tags of load balancer"
                 " (e.g. '{\"tag1\": 1,\"tag2\": \"a\"...}' )",
            metavar='<string>'
        )

        parser.add_argument(
            '--plan-id',
            metavar='<plan-id>',
            required=True,
            help=_('ID of the plan'),
        )

        parser.add_argument(
            '--syslog-servers',
            metavar="<ip-address=ip-addr,"
                    "port=port-number,"
                    "protocol=protocol>",
            action='store',
            nargs='+',
            help=_("Syslog servers to which access logs are transferred."
                   "ip-address: attach interface to network with this UUID, "
                   "port: Virtual IP address of the interface within subnet, "
                   "protocol: Protocol of the syslog server "
                   )
        )

        parser.add_argument(
            '--interface',
            metavar="<net-id=net-uuid,"
                    "virtual-ip=ip-addr,"
                    "reserved-fixed-ips=ip-addr1:ip-addr2:ip-addr3:ip-addr4>",
            required=True,
            action='store',
            nargs='+',
            help=_("Interfaces that attached to the load balancer."
                   "net-id: attach interface to network with this UUID, "
                   "virtual-ip: Virtual IP address of the interface within subnet, "
                   "reserved-fixed-ips: IPv4 fixed address for interface. "
                   "You can specify multiple ip address by using ':' "
                   "(e.g: 1.1.1.1:2.2.2.2:...), "
                   "If reserved-fixed-ips keywords are unspecified or less than 4 IP addresses are provided, they will be automatically assigned."
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

        if len(parsed_args.interface) > 7:
            msg = _("You can specify 1 to 7 interface")
            raise exceptions.CommandError(msg)

        interfaces = []
        valid_keys = ['net-id', 'virtual-ip', 'reserved-fixed-ips']
        key_map = {'net-id': 'network_id',
                   'virtual-ip': 'virtual_ip_address',
                   'reserved-fixed-ips': 'reserved_fixed_ips'}
        for if_str in parsed_args.interface:
            if_info = {}
            if_info.update(utils.parse_mlb_params(if_str, valid_keys, key_map))
            # reserved_fixed_ips は任意項目のため if_str に含まれない場合がある
            if if_info.get('reserved_fixed_ips'):
                fixed_ips = [{'ip_address': ip} for ip in if_info.get('reserved_fixed_ips').split(':')]
                if_info['reserved_fixed_ips'] = fixed_ips
            interfaces.append(if_info)

        syslog_servers = []
        if parsed_args.syslog_servers:
            if len(parsed_args.syslog_servers) > 2:
                msg = _("You can specify 0 to 2 syslog servers")
                raise exceptions.CommandError(msg)

            valid_keys = ['ip-address', 'port', 'protocol']
            key_map = {'ip-address': 'ip_address',
                       'port': 'port',
                       'protocol': 'protocol'}
            for sys_str in parsed_args.syslog_servers:
                sys_info = {}
                sys_info.update(utils.parse_mlb_params(sys_str, valid_keys, key_map))
                if sys_info.get('port'):
                    try:
                        sys_info['port'] = int(sys_info['port'])
                    except ValueError:
                        msg = _("You must specify integer to port")
                        raise exceptions.CommandError(msg)
                syslog_servers.append(sys_info)

        data = client.create_load_balancer(
            plan_id=parsed_args.plan_id,
            interfaces=interfaces,
            name=parsed_args.name,
            description=parsed_args.description,
            tags=tags,
            syslog_servers=syslog_servers if not syslog_servers == [] else None,
        )

        setattr(data, 'interfaces', json.dumps(data.interfaces, indent=2))
        setattr(data, 'syslog_servers', json.dumps(data.syslog_servers, indent=2))

        return row_headers, utils.get_item_properties(data, rows)


class DeleteLoadBalancer(command.Command):
    _description = _("Delete load-balancer")

    def get_parser(self, prog_name):
        parser = super(DeleteLoadBalancer, self). \
            get_parser(prog_name)
        parser.add_argument(
            "load_balancer",
            nargs="+",
            help="IDs of load balancer to be deleted",
            metavar='<load-balancer-id>'
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna
        for load_balancer_id in parsed_args.load_balancer:
            client.delete_load_balancer(load_balancer_id)


class UpdateLoadBalancer(command.ShowOne):
    _description = _("Update load-balancer")

    def get_parser(self, prog_name):
        parser = super(UpdateLoadBalancer, self). \
            get_parser(prog_name)
        parser.add_argument(
            "load_balancer",
            help="ID of load balancer to be updated",
            metavar='<load-balancer-id>'
        )

        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Name of load balancer'),
        )

        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description of load balancer'),
        )

        parser.add_argument(
            "--tags",
            help="Tags of load balancer"
                 " (e.g. '{\"tag1\": 1,\"tag2\": \"a\"...}' )",
            metavar='<string>'
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        rows = ROWS_FOR_SHOW
        row_headers = rows

        target = client.get_load_balancer(parsed_args.load_balancer)

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

        data = client.update_load_balancer(
            parsed_args.load_balancer, **patch)

        setattr(data, 'interfaces', json.dumps(data.interfaces, indent=2))
        setattr(data, 'syslog_servers', json.dumps(data.syslog_servers, indent=2))

        return row_headers, utils.get_item_properties(data, rows)


class CreateStagedLoadBalancerConfiguration(command.ShowOne):
    _description = _("Create new staged load-balancer")

    def get_parser(self, prog_name):
        parser = super(CreateStagedLoadBalancerConfiguration, self). \
            get_parser(prog_name)
        parser.add_argument(
            'load_balancer',
            metavar='<load-balancer-id>',
            help='ID of load balancer to create staged')

        parser.add_argument(
            '--syslog-servers',
            metavar="<ip-address=ip-addr,"
                    "port=port-number,"
                    "protocol=protocol>",
            action='store',
            nargs='+',
            help=_("Syslog servers to which access logs are transferred."
                   "ip-address: attach interface to network with this UUID, "
                   "port: Virtual IP address of the interface within subnet, "
                   "protocol: Protocol of the syslog server "
                   )
        )

        parser.add_argument(
            '--interface',
            metavar="<net-id=net-uuid,"
                    "virtual-ip=ip-addr,"
                    "reserved-fixed-ips=ip-addr1:ip-addr2:ip-addr3:ip-addr4>",
            required=True,
            action='store',
            nargs='+',
            help=_("Interfaces that attached to the load balancer."
                   "net-id: attach interface to network with this UUID, "
                   "virtual-ip: Virtual IP address of the interface within subnet, "
                   "reserved-fixed-ips: IPv4 fixed address for interface. "
                   "You can specify multiple ip address by using ':' "
                   "(e.g: 1.1.1.1:2.2.2.2:...), "
                   "If reserved-fixed-ips keywords are unspecified or less than 4 IP addresses are provided, they will be automatically assigned."
                   )
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        rows = ROWS_FOR_SHOW_STAGED
        row_headers = rows

        interfaces = []
        if parsed_args.interface:
            if len(parsed_args.interface) > 7:
                msg = _("You can specify 1 to 7 interface")
                raise exceptions.CommandError(msg)

            valid_keys = ['net-id', 'virtual-ip', 'reserved-fixed-ips']
            key_map = {'net-id': 'network_id',
                       'virtual-ip': 'virtual_ip_address',
                       'reserved-fixed-ips': 'reserved_fixed_ips'}
            for if_str in parsed_args.interface:
                if_info = {}
                if_info.update(utils.parse_mlb_params(if_str, valid_keys, key_map))
                # reserved_fixed_ips は任意項目のため if_str に含まれない場合がある
                if if_info.get('reserved_fixed_ips'):
                    fixed_ips = [{'ip_address': ip} for ip in if_info.get('reserved_fixed_ips').split(':')]
                    if_info['reserved_fixed_ips'] = fixed_ips
                interfaces.append(if_info)

        syslog_servers = []
        if parsed_args.syslog_servers:
            if len(parsed_args.syslog_servers) > 2:
                msg = _("You can specify 0 to 2 syslog servers")
                raise exceptions.CommandError(msg)

            valid_keys = ['ip-address', 'port', 'protocol']
            key_map = {'ip-address': 'ip_address',
                       'port': 'port',
                       'protocol': 'protocol'}
            for sys_str in parsed_args.syslog_servers:
                sys_info = {}
                sys_info.update(utils.parse_mlb_params(sys_str, valid_keys, key_map))
                if sys_info.get('port'):
                    try:
                        sys_info['port'] = int(sys_info['port'])
                    except ValueError:
                        msg = _("You must specify integer to port")
                        raise exceptions.CommandError(msg)
                syslog_servers.append(sys_info)

        data = client.create_staged_load_balancer_configuration(
            parsed_args.load_balancer,
            interfaces=interfaces if not interfaces == [] else None,
            syslog_servers=syslog_servers if not syslog_servers == [] else None,
        )

        setattr(data, 'interfaces', json.dumps(data.interfaces, indent=2))
        setattr(data, 'syslog_servers', json.dumps(data.syslog_servers, indent=2))

        return row_headers, utils.get_item_properties(data, rows)


class CancelStagedLoadBalancerConfiguration(command.Command):
    _description = _("Cancel staged load-balancer")

    def get_parser(self, prog_name):
        parser = super(CancelStagedLoadBalancerConfiguration, self). \
            get_parser(prog_name)
        parser.add_argument(
            "load_balancer",
            help="IDs of load balancer to be cancel configuration",
            metavar='<load-balancer-id>'
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna
        load_balancer_id = parsed_args.load_balancer
        client.cancel_staged_load_balancer_configuration(load_balancer_id)


class ShowStagedLoadBalancerConfiguration(command.ShowOne):
    _description = _("Show staged load-balancer")

    def get_parser(self, prog_name):
        parser = super(ShowStagedLoadBalancerConfiguration, self).\
            get_parser(prog_name)
        parser.add_argument(
            'load_balancer',
            metavar='<load-balancer-id>',
            help='ID of load balancer id to look up.')
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        rows = ROWS_FOR_SHOW_STAGED
        row_headers = rows

        data = client.get_staged_load_balancer_configuration(parsed_args.load_balancer)
        setattr(data, 'interfaces', json.dumps(data.interfaces, indent=2))
        setattr(data, 'syslog_servers', json.dumps(data.syslog_servers, indent=2))

        return row_headers, (utils.get_item_properties(data, rows))


class UpdateStagedLoadBalancerConfiguration(command.ShowOne):
    _description = _("Update staged load-balancer")

    def get_parser(self, prog_name):
        parser = super(UpdateStagedLoadBalancerConfiguration, self). \
            get_parser(prog_name)
        parser.add_argument(
            'load_balancer',
            metavar='<load-balancer-id>',
            help='ID of load balancer to update staged')

        parser.add_argument(
            '--syslog-servers',
            metavar="<ip-address=ip-addr,"
                    "port=port-number,"
                    "protocol=protocol>",
            action='store',
            nargs='+',
            help=_("Syslog servers to which access logs are transferred."
                   "ip-address: attach interface to network with this UUID, "
                   "port: Virtual IP address of the interface within subnet, "
                   "protocol: Protocol of the syslog server "
                   )
        )

        parser.add_argument(
            '--interface',
            metavar="<net-id=net-uuid,"
                    "virtual-ip=ip-addr,"
                    "reserved-fixed-ips=ip-addr1:ip-addr2:ip-addr3:ip-addr4>",
            required=True,
            action='store',
            nargs='+',
            help=_("Interfaces that attached to the load balancer."
                   "net-id: attach interface to network with this UUID, "
                   "virtual-ip: Virtual IP address of the interface within subnet, "
                   "reserved-fixed-ips: IPv4 fixed address for interface. "
                   "You can specify multiple ip address by using ':' "
                   "(e.g: 1.1.1.1:2.2.2.2:...), "
                   "If reserved-fixed-ips keywords are unspecified or less than 4 IP addresses are provided, they will be automatically assigned."
                   )
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        rows = ROWS_FOR_SHOW_STAGED
        row_headers = rows

        interfaces = []
        if parsed_args.interface:
            if len(parsed_args.interface) > 7:
                msg = _("You can specify 1 to 7 interface")
                raise exceptions.CommandError(msg)

            valid_keys = ['net-id', 'virtual-ip', 'reserved-fixed-ips']
            key_map = {'net-id': 'network_id',
                       'virtual-ip': 'virtual_ip_address',
                       'reserved-fixed-ips': 'reserved_fixed_ips'}
            for if_str in parsed_args.interface:
                if_info = {}
                if_info.update(utils.parse_mlb_params(if_str, valid_keys, key_map))
                # reserved_fixed_ips は任意項目のため if_str に含まれない場合がある
                if if_info.get('reserved_fixed_ips'):
                    fixed_ips = [{'ip_address': ip} for ip in if_info.get('reserved_fixed_ips').split(':')]
                    if_info['reserved_fixed_ips'] = fixed_ips
                interfaces.append(if_info)

        syslog_servers = []
        if parsed_args.syslog_servers:
            if len(parsed_args.syslog_servers) > 2:
                msg = _("You can specify 0 to 2 syslog servers")
                raise exceptions.CommandError(msg)

            valid_keys = ['ip-address', 'port', 'protocol']
            key_map = {'ip-address': 'ip_address',
                       'port': 'port',
                       'protocol': 'protocol'}
            for sys_str in parsed_args.syslog_servers:
                sys_info = {}
                sys_info.update(utils.parse_mlb_params(sys_str, valid_keys, key_map))
                if sys_info.get('port'):
                    try:
                        sys_info['port'] = int(sys_info['port'])
                    except ValueError:
                        msg = _("You must specify integer to port")
                        raise exceptions.CommandError(msg)
                syslog_servers.append(sys_info)

        data = client.update_staged_load_balancer_configuration(
            parsed_args.load_balancer,
            interfaces=interfaces if not interfaces == [] else None,
            syslog_servers=syslog_servers if not syslog_servers == [] else None,
        )

        setattr(data, 'interfaces', json.dumps(data.interfaces, indent=2))
        setattr(data, 'syslog_servers', json.dumps(data.syslog_servers, indent=2))

        return row_headers, utils.get_item_properties(data, rows)


class ActionLoadBalancer(command.Command):
    _description = _("Action for load-balancer")

    def get_parser(self, prog_name):
        parser = super(ActionLoadBalancer, self). \
            get_parser(prog_name)
        parser.add_argument(
            "load_balancer",
            help="IDs of load balancer to action",
            metavar='<load-balancer-id>'
        )

        parser.add_argument(
            '--apply-configurations',
            action='store_true',
            help=_('action of load balancer'),
        )

        parser.add_argument(
            '--system-update',
            metavar='<system-update>',
            help=_('system update of load balancer'),
        )

        parser.add_argument(
            '--cancel-configurations',
            action='store_true',
            help=_('cancel configuration of load balancer'),
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        request_body = {}

        if parsed_args.apply_configurations:
            request_body["apply-configurations"] = None

        if parsed_args.system_update:
            request_body["system-update"] = {"system_update_id": parsed_args.system_update}

        if parsed_args.cancel_configurations:
            if not request_body:
                request_body["cancel-configurations"] = None
            else:
                msg = _("You can not specify cancel-configurations and other options in the same time.")
                raise exceptions.CommandError(msg)

        client.action_load_balancer(parsed_args.load_balancer,
                                    None,
                                    **request_body)
