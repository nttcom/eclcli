from eclcli.common import command
from eclcli.common import utils
from eclcli.i18n import _  # noqa
from ..networkclient.common import utils as to_obj


class ListLoadBalancerInterface(command.Lister):
    _description = _("List load-balancer-interfaces")
    def get_parser(self, prog_name):
        parser = super(ListLoadBalancerInterface, self).get_parser(prog_name)
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
            '--name',
            metavar="name",
            help="filter by name")
        parser.add_argument(
            '--network_id',
            metavar="network_id",
            help="filter by network id")
        parser.add_argument(
            '--slot_number',
            metavar="slot_number",
            help="filter by slot number")
        parser.add_argument(
            '--status',
            metavar="status",
            help="filter by status")
        parser.add_argument(
            '--virtual_ip_address',
            metavar="virtual_ip_address",
            help="filter by virtual ip address")
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        columns = (
            'id',
            'name',
            'load_balancer_id',
            'ip_address',
            'status',
        )
        column_headers = (
            'ID',
            'Name',
            'Load Balancer',
            'Address',
            'Status',
        )

        search_opts = {}
        if parsed_args.id:
            search_opts.update({"id": parsed_args.id})
        if parsed_args.ip_address:
            search_opts.update({"ip_address": parsed_args.ip_address})
        if parsed_args.load_balancer_id:
            search_opts.update({"load_balancer_id": parsed_args.load_balancer_id})
        if parsed_args.name:
            search_opts.update({"name": parsed_args.name})
        if parsed_args.network_id:
            search_opts.update({"network_id": parsed_args.network_id})
        if parsed_args.slot_number:
            search_opts.update({"slot_number": parsed_args.slot_number})
        if parsed_args.status:
            search_opts.update({"status": parsed_args.status})
        if parsed_args.virtual_ip_address:
            search_opts.update({"virtual_ip_address": parsed_args.virtual_ip_address})

        data = [to_obj.LoadBalancerInterface(loadbalancer_interface)
                for loadbalancer_interface in
                network_client.list_loadbalancer_interfaces(
                   **search_opts
                ).get('load_balancer_interfaces')]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowLoadBalancerInterface(command.ShowOne):
    _description = _("Show load-balancer-interface")
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
    _description = _("Update load-balancer-interface")
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
            help='Network ID for load balancer interface to attach.'
                 'If you want to set this param to null, please specified 0.')
        parser.add_argument(
            '--ip_address',
            metavar='<ipv4>',
            help='Logical IP Address of load balancer interface to be set.'
                 'If you want to set this param to null, please specified 0.')
        parser.add_argument(
            '--virtual_ip_address',
            metavar='<ipv4>',
            help='Virtual IP Address of load balancer interface to be set.'
                 'If you want to set this param to null, please specified 0.')
        parser.add_argument(
            '--vrid',
            metavar='<integer>',
            type=int,
            help='VRID of load balancer interface to be set.'
                 'If you want to set this param to null, please specified 0.')
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

        if parsed_args.network_id == '0':
            body["load_balancer_interface"]["network_id"] = None

        if parsed_args.ip_address == '0':
            body["load_balancer_interface"]["ip_address"] = None

        if parsed_args.virtual_ip_address == '0':
            body["load_balancer_interface"]["virtual_ip_address"] = None

        if parsed_args.vrid == 0:
            body["load_balancer_interface"]["virtual_ip_properties"] = None
        elif parsed_args.vrid:
            body["load_balancer_interface"]["virtual_ip_properties"] = {
                "protocol": "vrrp",
                "vrid": parsed_args.vrid,
            }

        dic = network_client.update_loadbalancer_interface(
            loadbalancer_interface_id, body).get('load_balancer_interface')
        columns = utils.get_columns(dic)
        obj = to_obj.LoadBalancerInterface(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return (columns, data)
