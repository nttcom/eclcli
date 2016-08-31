from eclcli.common import command
from eclcli.common import utils
from ..networkclient.common import utils as to_obj


class ListInterDCService(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListInterDCService, self).get_parser(prog_name)
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

        data = [to_obj.InterDCService(idcsv)
            for idcsv in network_client.list_interdc_services().get('interdc_services')]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowInterDCService(command.ShowOne):
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
