
import six

from eclcli.common import command
from eclcli.common import exceptions
from eclcli.common import utils
from eclcli.identity import common as identity_common
from ..interconnectivityclient.common.utils import objectify


class ListMCIC(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListMCIC, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        connectivity_client = self.app.client_manager.interconnectivity

        columns = (
            'mcic_id',
            'mcic_name',
            'mcic_status',
        )
        column_headers = (
            'ID',
            'Name',
            'Status',
        )

        tenant_id = self.app.client_manager.session.get_project_id()
        data = [objectify(mcic)
            for mcic in connectivity_client.list_mcics(tenant_id)]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowMCIC(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(ShowMCIC, self).get_parser(prog_name)
        parser.add_argument(
            "mcic",
            metavar="MCIC",
            help="mcic to display (ID)")
        return parser

    def take_action(self, parsed_args):
        ecc_client = self.app.client_manager.interconnectivity
        try:
            mcic = ecc_client.show_mcic(parsed_args.mcic)
            printout = mcic
        except exceptions.ClientException as clientexp:
            printout = {"message": clientexp.message,
                        "details": clientexp.details,
                        "code": clientexp.code}
        return zip(*sorted(six.iteritems(printout)))
