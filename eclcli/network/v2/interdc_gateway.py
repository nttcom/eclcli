from eclcli.common import command
from eclcli.common import utils
from eclcli.i18n import _  # noqa
from ..networkclient.common import utils as to_obj


class ListInterDCGateway(command.Lister):
    _description = _("List interdc-gws")
    def get_parser(self, prog_name):
        parser = super(ListInterDCGateway, self).get_parser(prog_name)
        parser.add_argument(
            '--description',
            metavar="description",
            help="filter by description")
        parser.add_argument(
            '--id',
            metavar="id",
            help="filter by id")
        parser.add_argument(
            '--interdc_service_id',
            metavar="interdc_service_id",
            help="filter by interdc service id")
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
            'status',
        )
        column_headers = (
            'ID',
            'Name',
            'Status',
        )
        search_opts = {}
        if parsed_args.description:
            search_opts.update({"description": parsed_args.description})
        if parsed_args.id:
            search_opts.update({"id": parsed_args.id})
        if parsed_args.interdc_service_id:
            search_opts.update({"interdc_service_id": parsed_args.interdc_service_id})
        if parsed_args.interdc_service_id:
            search_opts.update({"interdc_service_id": parsed_args.interdc_service_id})
        if parsed_args.name:
            search_opts.update({"name": parsed_args.name})
        if parsed_args.status:
            search_opts.update({"status": parsed_args.status})

        data = [to_obj.InterDCGateway(idcgw)
                for idcgw in network_client.list_interdc_gateways(
                    **search_opts).get('interdc_gateways')]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowInterDCGateway(command.ShowOne):
    _description = _("Show interdc-gw")
    def get_parser(self, prog_name):
        parser = super(ShowInterDCGateway, self).get_parser(prog_name)
        parser.add_argument(
            'interdc_gateway_id',
            metavar="INTERDC_GATEWAY_ID",
            help="ID of Inter Data Center Gateway to show."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        interdc_gateway_id = parsed_args.interdc_gateway_id

        dic = network_client.show_interdc_gateway(interdc_gateway_id).get('interdc_gateway')
        columns = utils.get_columns(dic)
        obj = to_obj.InterDCGateway(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data
