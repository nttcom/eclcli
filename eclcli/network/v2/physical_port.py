from eclcli.common import command
from eclcli.common import utils
from eclcli.i18n import _  # noqa
from ..networkclient.common import utils as to_obj


class ListPhysicalPort(command.Lister):
    _description = _("List physical-ports")
    def get_parser(self, prog_name):
        parser = super(ListPhysicalPort, self).get_parser(prog_name)
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

        data = [to_obj.PhysicalPort(pport) for pport
                in network_client.list_physical_ports().get('physical_ports')]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowPhysicalPort(command.ShowOne):
    _description = _("Show physical-port")
    def get_parser(self, prog_name):
        parser = super(ShowPhysicalPort, self).get_parser(prog_name)
        parser.add_argument(
            'physical_port_id',
            metavar="<uuid>",
            help="Physical Port ID to show."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        pport_id = parsed_args.physical_port_id

        dic = network_client.show_physical_port(pport_id).get('physical_port')
        columns = utils.get_columns(dic)
        obj = to_obj.PhysicalPort(dic)
        data = utils.get_item_properties(
            obj, columns, )
        return columns, data
