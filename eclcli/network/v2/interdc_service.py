from eclcli.common import command
from eclcli.common import utils
from eclcli.i18n import _  # noqa
from ..networkclient.common import utils as to_obj


class ListInterDCService(command.Lister):
    _description = _("List interdc-services")
    def get_parser(self, prog_name):
        parser = super(ListInterDCService, self).get_parser(prog_name)
        parser.add_argument(
            '--description',
            metavar="description",
            help="filter by description")
        parser.add_argument(
            '--id',
            metavar="id",
            help="filter by id")
        parser.add_argument(
            '--name',
            metavar="name",
            help="filter by name")
        parser.add_argument(
            '--zone',
            metavar="zone",
            help="filter by zone")
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        columns = (
            'id',
            'name',
            'zone',
        )
        column_headers = (
            'ID',
            'Name',
            'zone',
        )

        search_opts = {}
        if parsed_args.description:
            search_opts.update({"description": parsed_args.description})
        if parsed_args.id:
            search_opts.update({"id": parsed_args.id})
        if parsed_args.name:
            search_opts.update({"name": parsed_args.name})
        if parsed_args.zone:
            search_opts.update({"zone": parsed_args.zone})

        data = [to_obj.InterDCService(idcsv)
                for idcsv in network_client.list_interdc_services(
                    **search_opts).get('interdc_services')]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowInterDCService(command.ShowOne):
    _description = _("Show interdc-service")
    def get_parser(self, prog_name):
        parser = super(ShowInterDCService, self).get_parser(prog_name)
        parser.add_argument(
            'interdc_service_id',
            metavar="INTERDC_SERVICE_ID",
            help="ID of InterDC Service to show."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        interdc_service_id = parsed_args.interdc_service_id

        dic = network_client.show_interdc_service(interdc_service_id).get('interdc_service')
        columns = utils.get_columns(dic)
        obj = to_obj.InterDCService(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data
