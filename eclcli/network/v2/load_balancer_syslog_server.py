from eclcli.common import command
from eclcli.common import utils
from eclcli.i18n import _  # noqa
from ..networkclient.common import utils as to_obj


class ListLoadBalancerSyslogServer(command.Lister):
    _description = _("List load-balancer-syslog-servers")
    def get_parser(self, prog_name):
        parser = super(ListLoadBalancerSyslogServer, self).get_parser(prog_name)
        parser.add_argument(
            '--id',
            metavar="id",
            help="filter by id")
        parser.add_argument(
            '--ip_address',
            metavar="ip_address",
            help="filter by ip address")
        parser.add_argument(
            '--load_balancer_id',
            metavar="load_balancer_id",
            help="filter by load balancer id")
        parser.add_argument(
            '--log_facility',
            metavar="log_facility",
            help="filter by log facility")
        parser.add_argument(
            '--log_level',
            metavar="log_level",
            help="filter by log level")
        parser.add_argument(
            '--name',
            metavar="name",
            help="filter by name")
        parser.add_argument(
            '--port_number',
            metavar="port_number",
            help="filter by port number")
        parser.add_argument(
            '--status',
            metavar="status",
            help="filter by status")
        parser.add_argument(
            '--transport_type',
            metavar="transport_type",
            help="filter by transport type")
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        columns = (
            'id',
            'name',
            'load_balancer_id',
            'status',
        )
        column_headers = (
            'ID',
            'Name',
            'Load Balancer',
            'Status',
        )
        search_opts = {}
        if parsed_args.id:
            search_opts.update({"id": parsed_args.id})
        if parsed_args.ip_address:
            search_opts.update({"ip_address": parsed_args.ip_address})
        if parsed_args.load_balancer_id:
            search_opts.update({"load_balancer_id": parsed_args.load_balancer_id})
        if parsed_args.log_facility:
            search_opts.update({"log_facility": parsed_args.log_facility})
        if parsed_args.log_level:
            search_opts.update({"log_level": parsed_args.log_level})
        if parsed_args.name:
            search_opts.update({"name": parsed_args.name})
        if parsed_args.port_number:
            search_opts.update({"port_number": parsed_args.port_number})
        if parsed_args.status:
            search_opts.update({"status": parsed_args.status})
        if parsed_args.transport_type:
            search_opts.update({"transport_type": parsed_args.transport_type})

        data = [to_obj.LoadBalancerSyslogServer(loadbalancer_syslog_server)
                for loadbalancer_syslog_server in
                network_client.list_loadbalancer_syslog_servers(
                   **search_opts
                ).get('load_balancer_syslog_servers')]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowLoadBalancerSyslogServer(command.ShowOne):
    _description = _("Show load-balancer-syslog-server")
    def get_parser(self, prog_name):
        parser = super(ShowLoadBalancerSyslogServer, self).get_parser(prog_name)
        parser.add_argument(
            'loadbalancer_syslog_server_id',
            metavar="LOAD_BALANCER_SYSLOG_SERVER_ID",
            help="ID of Load Balancer Syslog Server ID."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        loadbalancer_syslog_server_id = parsed_args.loadbalancer_syslog_server_id

        dic = network_client.show_loadbalancer_syslog_server(
                loadbalancer_syslog_server_id).get('load_balancer_syslog_server')
        columns = utils.get_columns(dic)
        obj = to_obj.LoadBalancerSyslogServer(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data


class CreateLoadBalancerSyslogServer(command.ShowOne):
    _description = _("Create new load-balancer-syslog-server")
    def get_parser(self, prog_name):
        parser = super(CreateLoadBalancerSyslogServer, self).get_parser(prog_name)
        parser.add_argument(
            '--acl_logging',
            metavar='<string>',
            help='Acl logging ENABLED or DISABLED.')
        parser.add_argument(
            '--appflow_logging',
            metavar='<string>',
            help='appflow logging ENABLED or DISABLED.')
        parser.add_argument(
            '--date_format',
            metavar='<string>',
            help='date format utilized, one of DDMMYYYY, MMDDYYYY or YYYYMMDD')
        parser.add_argument(
            '--description',
            metavar='<string>',
            help='Description of load balancer syslog server to create.')
        parser.add_argument(
            '--ip_address',
            metavar='<ipv4>',
            required=True,
            help='IP address of load balancer syslog server to create.')
        parser.add_argument(
            'load_balancer_id',
            metavar='LOAD_BALANCER_ID',
            help='Load Balancer ID of load balancer syslog server to create')
        parser.add_argument(
            '--log_facility',
            metavar='<string>',
            help='Log facility, from LOCAL0 to LOCAL7')
        parser.add_argument(
            '--log_level',
            metavar='<string>',
            help='Log levels, one of "ALERT", "CRITICAL","EMERGENCY", "INFORMATIONAL", '
                    '"NOTICE", "ALL", "DEBUG", "ERROR", "NONE", "WARNING", '
                    'Cannot combine "ALL" or "None" with the others.')
        parser.add_argument(
            '--name',
            metavar='<string>',
            required=True,
            help='Name of load balancer syslog server to create.')
        parser.add_argument(
            '--port_number',
            metavar='<integer>',
            type=int,
            help='Port number of load balancer syslog server to create.')
        parser.add_argument(
            '--priority',
            metavar='<integer>',
            required=True,
            type=int,
            help='Priority of load balancer syslog server to create, 0-255.')
        parser.add_argument(
            '--tcp_logging',
            metavar='<string>',
            help='TCP logging. NONE or ALL')
        parser.add_argument(
            '--time_zone',
            metavar='<string>',
            help='Time zone, GMT_TIME or LOCAL_TIME')
        parser.add_argument(
            '--transport_type',
            metavar='<string>',
            help='Transport type, UDP')
        parser.add_argument(
            '--user_configurable_log_messages',
            metavar='<string>',
            help='Can user configure log messages, YES or NO')
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        body = {'load_balancer_syslog_server': {}}
        utils.update_dict(
            parsed_args,
            body['load_balancer_syslog_server'],
            ['acl_logging', 'appflow_logging', 'date_format',
             'description', 'ip_address', 'load_balancer_id',
             'log_facility', 'log_level', 'name', 'port_number',
             'priority', 'tcp_logging', 'time_zone', 'transport_type',
             'user_configurable_log_messages'])

        dic = network_client.create_loadbalancer_syslog_server(body).get('load_balancer_syslog_server')
        columns = utils.get_columns(dic)
        obj = to_obj.LoadBalancerSyslogServer(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data


class DeleteLoadBalancerSyslogServer(command.Command):
    _description = _("Delete load-balancer-syslog-server")
    def get_parser(self, prog_name):
        parser = super(DeleteLoadBalancerSyslogServer, self).get_parser(prog_name)
        parser.add_argument(
            'load_balancer_syslog_server_id',
            metavar="LOAD_BALANCER_SYSLOG_SERVER_ID",
            nargs="+",
            help="ID(s) of Load Balancer Syslog Servers to delete."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        for lb_sid in parsed_args.load_balancer_syslog_server_id:
            network_client.delete_loadbalancer_syslog_server(lb_sid)


class SetLoadBalancerSyslogServer(command.ShowOne):
    _description = _("Update load-balancer-syslog-server")
    def get_parser(self, prog_name):
        parser = super(SetLoadBalancerSyslogServer, self).get_parser(prog_name)
        parser.add_argument(
            'load_balancer_syslog_server_id',
            metavar='LOAD_BALANCER_SYSLOG_SERVER_ID',
            help='ID of Load Balancer Syslog Server to update.')
        parser.add_argument(
            '--acl_logging',
            metavar='<string>',
            help='Acl logging ENABLED or DISABLED.')
        parser.add_argument(
            '--appflow_logging',
            metavar='<string>',
            help='appflow logging ENABLED or DISABLED.')
        parser.add_argument(
            '--date_format',
            metavar='<string>',
            help='date format utilized, one of DDMMYYYY, MMDDYYYY or YYYYMMDD')
        parser.add_argument(
            '--description',
            metavar='<string>',
            help='Description of load balancer syslog server to create.')
        parser.add_argument(
            '--log_facility',
            metavar='<string>',
            help='Log facility, from LOCAL0 to LOCAL7')
        parser.add_argument(
            '--log_level',
            metavar='<string>',
            help='Log levels, one of "ALERT", "CRITICAL","EMERGENCY", "INFORMATIONAL", '
                    '"NOTICE", "ALL", "DEBUG", "ERROR", "NONE", "WARNING", '
                    'Cannot combine "ALL" or "None" with the others.')
        parser.add_argument(
            '--priority',
            metavar='<integer>',
            type=int,
            help='Priority of load balancer syslog server to create, 0-255.')
        parser.add_argument(
            '--tcp_logging',
            metavar='<string>',
            help='TCP logging. NONE or ALL')
        parser.add_argument(
            '--time_zone',
            metavar='<string>',
            help='Time zone, GMT_TIME or LOCAL_TIME')
        parser.add_argument(
            '--user_configurable_log_messages',
            metavar='<string>',
            help='Can user configure log messages, YES or NO')
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        body = {'load_balancer_syslog_server': {}}
        load_balancer_syslog_server_id = parsed_args.load_balancer_syslog_server_id
        utils.update_dict(
            parsed_args,
            body['load_balancer_syslog_server'],
            ['acl_logging', 'appflow_logging', 'date_format',
             'description', 'log_facility', 'log_level',
             'priority', 'tcp_logging', 'time_zone',
             'user_configurable_log_messages'])

        dic = network_client.update_loadbalancer_syslog_server(
            load_balancer_syslog_server_id, body).get('load_balancer_syslog_server')

        columns = utils.get_columns(dic)
        obj = to_obj.LoadBalancerSyslogServer(dic)
        data = utils.get_item_properties(
                    obj, columns,)
        return columns, data
