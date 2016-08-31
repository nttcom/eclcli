from eclcli.common import command
from eclcli.common import utils
from ..networkclient.common import utils as to_obj


class ListLoadBalancerInterface(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListLoadBalancerInterface, self).get_parser(prog_name)
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

        data = [to_obj.LoadBalancerInterface(loadbalancer_interface)
            for loadbalancer_interface in network_client.list_loadbalancer_interfaces().get('load_balancer_interfaces')]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowLoadBalancerInterface(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(ShowLoadBalancerInterface, self).get_parser(prog_name)
        parser.add_argument(
            'loadbalancer_interface_id',
            metavar="LOAD_BALANCER_INTERFACE_ID",
            help="ID of Load Balancer Interface ID."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        loadbalancer_interface_id = parsed_args.loadbalancer_interface_id

        dic = network_client.show_loadbalancer_interface(loadbalancer_interface_id).get('load_balancer_interface')
        columns = utils.get_columns(dic)
        obj = to_obj.LoadBalancerInterface(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data


class SetLoadBalancerInterface(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(SetLoadBalancerInterface, self).get_parser(prog_name)
        parser.add_argument(
            'loadbalancer_interface_id',
            metavar='LOAD_BALANCER_INTERFACE_ID',
            help='ID of load balancer interface to update.')
        parser.add_argument(
            '--description',
            metavar='<string>',
            help='Description of load balancer interface.')
        parser.add_argument(
            '--network_id',
            metavar='NETWORK_ID',
            help='Network ID for load balancer interface to attach.')
        parser.add_argument(
            '--ip_address',
            metavar='<ipv4>',
            help='Logical IP Address of load balancer interface to be set.')
        parser.add_argument(
            '--virtual_ip_address',
            metavar='<ipv4>',
            help='Virtual IP Address of load balancer interface to be set.')
        parser.add_argument(
            '--vrid',
            metavar='<integer>',
            type=int,
            help='VRID of load balancer interface to be set.')
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        body = {'load_balancer_interface': {}}
        loadbalancer_interface_id = parsed_args.loadbalancer_interface_id
        utils.update_dict(
            parsed_args,
            body['load_balancer_interface'],
            ['description', 'network_id', 'ip_address',
             'virtual_ip_address'])

        dic = network_client.update_loadbalancer_interface(
            loadbalancer_interface_id, body).get('load_balancer_interface')
        columns = utils.get_columns(dic)
        obj = to_obj.LoadBalancerInterface(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return (columns, data)
