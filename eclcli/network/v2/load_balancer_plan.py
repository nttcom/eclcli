from eclcli.common import command
from eclcli.common import utils
from ..networkclient.common import utils as to_obj


class ListLoadBalancerPlan(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListLoadBalancerPlan, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        columns = (
            'id',
            'name',
            'vendor',
        )
        column_headers = (
            'ID',
            'Name',
            'Vendor',
        )

        data = [to_obj.LoadBalancerPlan(lbplan)
            for lbplan in network_client.list_loadbalancer_plans().get('load_balancer_plans')]

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
