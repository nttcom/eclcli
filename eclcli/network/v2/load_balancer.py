from eclcli.common import command
from eclcli.common import utils
from eclcli.i18n import _  # noqa
from ..networkclient.common import utils as to_obj


class ListLoadBalancer(command.Lister):
    _description = _("List load-balancers")
    def get_parser(self, prog_name):
        parser = super(ListLoadBalancer, self).get_parser(prog_name)
        parser.add_argument(
            '--admin_username',
            metavar="admin_username",
            help="filter by admin username")
        parser.add_argument(
            '--availability_zone',
            metavar="availability_zone",
            help="filter by availability zone")
        parser.add_argument(
            '--default_gateway',
            metavar="default_gateway",
            help="filter by default gateway")
        parser.add_argument(
            '--user_username',
            metavar="user_username",
            help="filter by user username")
        parser.add_argument(
            '--load_balancer_plan_id',
            metavar="load_balancer_plan_id",
            help="filter by load balancer plan id")
        parser.add_argument(
            '--id',
            metavar="id",
            help="filter by id")
        parser.add_argument(
            '--name',
            metavar="name",
            help="filter by name")
        parser.add_argument(
            '--status',
            metavar="status",
            help="filter by status")
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        columns = (
            'id',
            'name',
            'load_balancer_plan_id',
            'default_gateway',
            'status',
        )
        column_headers = (
            'ID',
            'Name',
            'Load Balancer Plan',
            'Default Gateway',
            'Status',
        )

        search_opts = dict()
        if parsed_args.admin_username:
            search_opts.update({"admin_username": parsed_args.admin_username})
        if parsed_args.availability_zone:
            search_opts.update({"availability_zone": parsed_args.availability_zones})
        if parsed_args.user_username:
            search_opts.update({"user_username": parsed_args.user_username})
        if parsed_args.default_gateway:
            search_opts.update({"default_gateway": parsed_args.default_gateway})
        if parsed_args.load_balancer_plan_id:
            search_opts.update({"load_balancer_plan_id": parsed_args.load_balancer_plan_id})
        if parsed_args.id:
            search_opts.update({"id": parsed_args.id})
        if parsed_args.name:
            search_opts.update({"name": parsed_args.name})
        if parsed_args.status:
            search_opts.update({"status": parsed_args.status})

        data = [
            to_obj.LoadBalancer(loadbalancer)
            for loadbalancer in network_client.list_loadbalancers().get(
                'load_balancers')
        ]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowLoadBalancer(command.ShowOne):
    _description = _("Show load-balancer")
    def get_parser(self, prog_name):
        parser = super(ShowLoadBalancer, self).get_parser(prog_name)
        parser.add_argument(
            'loadbalancer_id',
            metavar="LOAD_BALANCER_ID",
            help="ID of Load Balancer to show."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        loadbalancer_id = parsed_args.loadbalancer_id

        dic = network_client.show_loadbalancer(loadbalancer_id).get('load_balancer')
        columns = utils.get_columns(dic)
        obj = to_obj.LoadBalancer(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data


class CreateLoadBalancer(command.ShowOne):
    _description = _("Create new load-balancer")
    def get_parser(self, prog_name):
        parser = super(CreateLoadBalancer, self).get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar='<string>',
            help='Name of load balancer to create.')
        parser.add_argument(
            '--description',
            metavar='<string>',
            help='Description of load balancer to create.')
        parser.add_argument(
            'load_balancer_plan_id',
            metavar='LOAD_BALANCER_PLAN_ID',
            help='Load Balancer Plan ID of load balancer to create')
        parser.add_argument(
            '--availability_zone',
            metavar='<string>',
            help='Availability Zone of load balancer to create.')
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        body = {'load_balancer': {}}
        utils.update_dict(
            parsed_args,
            body['load_balancer'],
            ['name', 'description', 'load_balancer_plan_id',
             'availability_zone'])

        dic = network_client.create_loadbalancer(body).get('load_balancer')
        columns = utils.get_columns(dic)
        obj = to_obj.LoadBalancer(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data


class SetLoadBalancer(command.ShowOne):
    _description = _("Update load-balancer")
    def get_parser(self, prog_name):
        parser = super(SetLoadBalancer, self).get_parser(prog_name)
        parser.add_argument(
            'loadbalancer_id',
            metavar='LOAD_BALANCER_ID',
            help='ID of Public IP to update.')
        parser.add_argument(
            '--name',
            metavar='<string>',
            help='Name of load balancer to update.')
        parser.add_argument(
            '--description',
            metavar='<string>',
            help='Description of load balancer to update.')
        parser.add_argument(
            '--load_balancer_plan_id',
            metavar='LOAD_BALANCER_PLAN_ID',
            help='LoadBalancer Plan ID of load balancer to update')
        parser.add_argument(
            '--default_gateway',
            metavar='<ipv4>',
            help='Default Gateway of load balancer to update.')
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        body = {'load_balancer': {}}
        loadbalancer_id = parsed_args.loadbalancer_id
        utils.update_dict(
            parsed_args,
            body['load_balancer'],
            ['name', 'description',
             'load_balancer_plan_id', 'default_gateway'])

        dic = network_client.update_loadbalancer(
            loadbalancer_id, body).get('load_balancer')
        columns = utils.get_columns(dic)
        obj = to_obj.LoadBalancer(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data


class DeleteLoadBalancer(command.Command):
    _description = _("Delete load-balancer")
    def get_parser(self, prog_name):
        parser = super(DeleteLoadBalancer, self).get_parser(prog_name)
        parser.add_argument(
            'loadbalancer_id',
            metavar="LOAD_BALANCER_ID",
            nargs="+",
            help="ID(s) of Load Balancers to delete."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        for fid in parsed_args.loadbalancer_id:
            network_client.delete_loadbalancer(fid)


class RebootLoadBalancer(command.ShowOne):
    _description = _("Reboot load-balancer")
    def get_parser(self, prog_name):
        parser = super(RebootLoadBalancer, self).get_parser(prog_name)
        parser.add_argument(
            'loadbalancer_id',
            metavar="LOAD_BALANCER_ID",
            help="ID of Load Balancer to show."
        )
        parser.add_argument(
            '--type',
            metavar='{SOFT|HARD}',
            default="HARD",
            choices=["SOFT", "HARD"],
            help='Reboot Type: SOFT/HARD.')
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        loadbalancer_id = parsed_args.loadbalancer_id

        body = {}
        body.update({"type": parsed_args.type})

        network_client.reboot_loadbalancer(loadbalancer_id, body=body)
        dic = network_client.show_loadbalancer(loadbalancer_id).get('load_balancer')
        columns = utils.get_columns(dic)
        obj = to_obj.LoadBalancer(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data


class ResetPasswordLoadBalancer(command.ShowOne):
    _description = _("Reset password load-balancer")
    def get_parser(self, prog_name):
        parser = super(ResetPasswordLoadBalancer, self).get_parser(prog_name)
        parser.add_argument(
            'loadbalancer_id',
            metavar="LOAD_BALANCER_ID",
            help="ID of Load Balancer to show."
        )
        parser.add_argument(
            '--username',
            metavar='USERNAME',
            required=True,
            help='username to reset password of Load Balancer.')
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        loadbalancer_id = parsed_args.loadbalancer_id
        body = {}
        body.update({"username": parsed_args.username})

        dic = network_client.reset_password_loadbalancer(loadbalancer_id, body=body)
        columns = utils.get_columns(dic)
        obj = to_obj.LoadBalancer(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data
