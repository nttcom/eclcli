from eclcli.common import command
from eclcli.common import utils
from ..networkclient.common import utils as to_obj


class ListLoadBalancer(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListLoadBalancer, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        columns = (
            'id',
            'name',
            'status',
        )
        column_headers = (
            'ID',
            'Name',
            'Status',
        )

        data = [to_obj.LoadBalancer(loadbalancer)
            for loadbalancer in network_client.list_loadbalancers().get('load_balancers')]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowLoadBalancer(command.ShowOne):
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
    def get_parser(self, prog_name):
        parser = super(ResetPasswordLoadBalancer, self).get_parser(prog_name)
        parser.add_argument(
            'loadbalancer_id',
            metavar="LOAD_BALANCER_PLAN_ID",
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
