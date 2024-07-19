from eclcli.common import command
from eclcli.common import utils
from eclcli.i18n import _  # noqa
from ..networkclient.common import utils as to_obj


class ListFICService(command.Lister):
    _description = _("List fic-services")
    def get_parser(self, prog_name):
        parser = super(ListFICService, self).get_parser(prog_name)
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
            'Zone',
        )

        data = [to_obj.FICService(ficsv) for ficsv in
                network_client.list_fic_services().get('fic_services')]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowFICService(command.ShowOne):
    _description = _("Show fic-service")
    def get_parser(self, prog_name):
        parser = super(ShowFICService, self).get_parser(prog_name)
        parser.add_argument(
            'fic_service_id',
            metavar="FIC_SERVICE_ID",
            help="ID of FIC Service to show."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        ficsv_id = parsed_args.fic_service_id

        dic = network_client.show_fic_service(ficsv_id).get('fic_service')
        columns = utils.get_columns(dic)
        obj = to_obj.FICService(dic)
        data = utils.get_item_properties(
            obj, columns, )
        return columns, data
