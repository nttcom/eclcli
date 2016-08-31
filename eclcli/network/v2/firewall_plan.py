from eclcli.common import command
from eclcli.common import utils
from ..networkclient.common import utils as to_obj


class ListFirewallPlan(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListFirewallPlan, self).get_parser(prog_name)
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

        data = [to_obj.FirewallPlan(fwplan)
            for fwplan in network_client.list_firewall_plans().get('firewall_plans')]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowFirewallPlan(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(ShowFirewallPlan, self).get_parser(prog_name)
        parser.add_argument(
            'firewall_plan_id',
            metavar="FIREWALL_PLAN_ID",
            help="ID of Firewall Plan to show."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        firewall_plan_id = parsed_args.firewall_plan_id

        dic = network_client.show_firewall_plan(firewall_plan_id).get('firewall_plan')
        columns = utils.get_columns(dic)
        obj = to_obj.FirewallPlan(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data
