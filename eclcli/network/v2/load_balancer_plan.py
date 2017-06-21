from eclcli.common import command
from eclcli.common import utils
from ..networkclient.common import utils as to_obj


class ListLoadBalancerPlan(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListLoadBalancerPlan, self).get_parser(prog_name)
        parser.add_argument(
            '--enabled',
            metavar="enabled",
            help="filter by enabled: true or false")
        parser.add_argument(
            '--id',
            metavar="id",
            help="filter by id")
        parser.add_argument(
            '--name',
            metavar="name",
            help="filter by name")
        parser.add_argument(
            '--maximum_syslog_servers',
            metavar="maximum_syslog_servers",
            help="filter by maximum syslog servers")
        parser.add_argument(
            '--vendor',
            metavar="vendor",
            help="filter by vendor")
        # parser.add_argument(
        #     '--version',
        #     metavar="version",
        #     help="filter by version")
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        columns = (
            'id',
            'name',
            'vendor',
            'maximum_syslog_servers',
            'enabled',
        )
        column_headers = (
            'ID',
            'Name',
            'Vendor',
            'Maximum_Syslog_Servers',
            'Enabled',
        )

        search_opts = dict()
        if parsed_args.enabled:
            search_opts.update({"enabled": parsed_args.enabled})
        if parsed_args.id:
            search_opts.update({"id": parsed_args.id})
        if parsed_args.name:
            search_opts.update({"name": parsed_args.name})
        if parsed_args.vendor:
            search_opts.update({"vendor": parsed_args.vendor})
        # if parsed_args.version:
            # search_opts.update({"version": parsed_args.version})

        data = [to_obj.LoadBalancerPlan(lbplan)
                for lbplan in network_client.list_loadbalancer_plans(
                    **search_opts).get('load_balancer_plans')]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowLoadBalancerPlan(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(ShowLoadBalancerPlan, self).get_parser(prog_name)
        parser.add_argument(
            'loadbalancer_plan_id',
            metavar="LOAD_BALANCER_PLAN_ID",
            help="ID of Load Balancer Plan to show."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        loadbalancer_plan_id = parsed_args.loadbalancer_plan_id

        dic = network_client.show_loadbalancer_plan(loadbalancer_plan_id).get('load_balancer_plan')
        columns = utils.get_columns(dic)
        obj = to_obj.LoadBalancerPlan(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data
