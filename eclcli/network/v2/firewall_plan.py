from eclcli.common import command
from eclcli.common import utils
from eclcli.i18n import _  # noqa
from ..networkclient.common import utils as to_obj


class ListFirewallPlan(command.Lister):
    _description = _("List firewall-plans")
    def get_parser(self, prog_name):
        parser = super(ListFirewallPlan, self).get_parser(prog_name)
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
            'enabled',
        )
        column_headers = (
            'ID',
            'Name',
            'Vendor',
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
        #     search_opts.update({"version": parsed_args.version})

        data = [
            to_obj.FirewallPlan(fwplan) for fwplan
            in network_client.list_firewall_plans(**search_opts).get('firewall_plans')
        ]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowFirewallPlan(command.ShowOne):
    _description = _("Show firewall-plan")
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
