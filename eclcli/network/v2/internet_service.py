from eclcli.common import command
from eclcli.common import utils
from ..networkclient.common import utils as to_obj


class ListInternetService(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListInternetService, self).get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar="name",
            help="filter by name")
        parser.add_argument(
            '--id',
            metavar="id",
            help="filter by id")
        parser.add_argument(
            '--minimal-submask-length',
            metavar="minimal_submask_length",
            help="filter by minimal submask length")
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
            'minimal_submask_length',
            'Zone',
        )
        column_headers = (
            'ID',
            'Name',
            'Subnet mask',
            'Zone',
        )

        search_opts = dict()
        if parsed_args.name:
            search_opts.update({"name": parsed_args.name})
        if parsed_args.id:
            search_opts.update({"id": parsed_args.id})
        if parsed_args.minimal_submask_length:
            search_opts.update({"minimal_submask_length": parsed_args.minimal_submask_length})
        if parsed_args.zone:
            search_opts.update({"zone": parsed_args.zone})

        data = [
            to_obj.InternetService(inetsv)
            for inetsv in network_client.list_internet_services(
                **search_opts).get('internet_services')
        ]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowInternetService(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(ShowInternetService, self).get_parser(prog_name)
        parser.add_argument(
            'internet_service_id',
            metavar="INTERNET_SERVICE_ID",
            help="ID of Internet Service to show."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        inetsv_id = parsed_args.internet_service_id

        dic = network_client.show_internet_service(inetsv_id).get('internet_service')
        columns = utils.get_columns(dic)
        obj = to_obj.InternetService(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data
