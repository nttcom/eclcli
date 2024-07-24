from eclcli.common import command
from eclcli.common import utils
from eclcli.i18n import _  # noqa
from ..networkclient.common import utils as to_obj


class ListInternetGateway(command.Lister):
    _description = _("List inet-gws")
    def get_parser(self, prog_name):
        parser = super(ListInternetGateway, self).get_parser(prog_name)

        parser.add_argument(
            '--name',
            metavar="name",
            help="filter by name")
        parser.add_argument(
            '--id',
            metavar="id",
            help="filter by id")
        parser.add_argument(
            '--internet-service-id',
            metavar="internet_service_id",
            help="filter by internet service id")
        parser.add_argument(
            '--qos-option-id',
            metavar="qos_option_id",
            help="filter by qos option id")
        # parser.add_argument(
        #     '--tenant-id',
        #     metavar="tenant_id",
        #     help="filter by tenant_id")
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
            'status',
        )
        column_headers = (
            'ID',
            'Name',
            'Status',
        )

        search_opts = dict()
        if parsed_args.name:
            search_opts.update({"name": parsed_args.name})
        if parsed_args.id:
            search_opts.update({"id": parsed_args.id})
        if parsed_args.internet_service_id:
            search_opts.update({"internet_service_id": parsed_args.internet_service_id})
        if parsed_args.qos_option_id:
            search_opts.update({"qos_option_id": parsed_args.qos_option_id})
        # if parsed_args.tenant_id:
        #     search_opts.update({"tenant_id": parsed_args.tenant_id})
        if parsed_args.status:
            search_opts.update({"status": parsed_args.status})

        data = [
            to_obj.InternetGateway(inetgw)
            for inetgw in network_client.list_internet_gateways(
                **search_opts).get('internet_gateways')
        ]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowInternetGateway(command.ShowOne):
    _description = _("Show inet-gw")
    def get_parser(self, prog_name):
        parser = super(ShowInternetGateway, self).get_parser(prog_name)
        parser.add_argument(
            'internet_gateway_id',
            metavar="INTERNET_GATEWAY_ID",
            help="ID of Internet Gateway to show."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        internet_gateway_id = parsed_args.internet_gateway_id

        dic = network_client.show_internet_gateway(internet_gateway_id).get('internet_gateway')
        columns = dic  # utils.get_columns(dic)
        obj = to_obj.InternetGateway(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data


class CreateInternetGateway(command.ShowOne):
    _description = _("Create new inet-gw")
    def get_parser(self, prog_name):
        parser = super(CreateInternetGateway, self).get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar='<string>',
            help='Name of internet gateway to create.')
        parser.add_argument(
            '--description',
            metavar='<string>',
            help='Description of internet gateway to create.')
        parser.add_argument(
            'internet_service_id',
            metavar='INTERNET_SERVICE_ID',
            help='Internet Service ID of internet gateway to create.')
        parser.add_argument(
            '--qos_option_id',
            metavar='QOS_OPTION_ID',
            help='QoS Option ID of internet gateway to create.')
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        body = {}
        if parsed_args.name is not None:
            body['name'] = str(parsed_args.name)
        if parsed_args.description is not None:
            body['description'] = str(parsed_args.description)
        body['internet_service_id'] = parsed_args.internet_service_id
        body['qos_option_id'] = parsed_args.qos_option_id

        dic = network_client.create_internet_gateway({'internet_gateway': body}).get('internet_gateway')
        columns = utils.get_columns(dic)
        obj = to_obj.InternetGateway(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data


class SetInternetGateway(command.ShowOne):
    _description = _("Update inet-gw")
    def get_parser(self, prog_name):
        parser = super(SetInternetGateway, self).get_parser(prog_name)
        parser.add_argument(
            'internet_gateway_id',
            metavar='INTERNET_GATEWAY_ID',
            help='ID of internet gateway to update.')
        parser.add_argument(
            '--name',
            metavar='<string>',
            help='Name of internet gateway to update.')
        parser.add_argument(
            '--description',
            metavar='<string>',
            help='Description of internet gateway to update.')
        parser.add_argument(
            '--qos_option_id',
            metavar='QOS_OPTION_ID',
            help='QoS Option ID of internet gateway to update.')
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        body = {}
        internet_gateway_id = parsed_args.internet_gateway_id
        if parsed_args.name is not None:
            body['name'] = str(parsed_args.name)
        if parsed_args.description is not None:
            body['description'] = str(parsed_args.description)
        if parsed_args.qos_option_id is not None:
            body['qos_option_id'] = parsed_args.qos_option_id

        dic = network_client.update_internet_gateway(
            internet_gateway_id, body={'internet_gateway': body}).get('internet_gateway')
        columns = utils.get_columns(dic)
        obj = to_obj.InternetGateway(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data


class DeleteInternetGateway(command.Command):
    _description = _("Delete inet-gw")
    def get_parser(self, prog_name):
        parser = super(DeleteInternetGateway, self).get_parser(prog_name)
        parser.add_argument(
            'internet_gateway_id',
            metavar="INTERNET_GATEWAY_ID",
            nargs="+",
            help="ID(s) of Internet Gateway to delete."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        for inetgw_id in parsed_args.internet_gateway_id:
            network_client.delete_internet_gateway(inetgw_id)
