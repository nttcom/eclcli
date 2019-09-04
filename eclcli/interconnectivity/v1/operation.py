import six

from eclcli.common import command
from eclcli.common import exceptions
from eclcli.common import utils
from ..interconnectivityclient.common.utils import objectify, get_request_body


class ListOperation(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListOperation, self).get_parser(prog_name)

        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            '--mcic_id',
            metavar='<mcic_id>',
            help='mCIC id to query operations [Type: String]')
        group.add_argument(
            '--cic_id',
            metavar='<cic_id>',
            help='CIC id to query operations [Type: String]')
        return parser

    def take_action(self, parsed_args):
        connectivity_client = self.app.client_manager.interconnectivity

        columns = (
            'operation_id',
            'operation_type',
            'operation_status',
        )
        column_headers = (
            'ID',
            'Type',
            'Status',
        )

        required = ()
        optional = ('mcic_id', 'cic_id')
        body = get_request_body(parsed_args, required, optional)

        data = [objectify(mcic)
                for mcic in connectivity_client.list_operations(**body)]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowOperation(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(ShowOperation, self).get_parser(prog_name)
        parser.add_argument(
            "operation_id",
            metavar="OPERATION_ID",
            help="Operation to display (ID)")
        return parser

    def take_action(self, parsed_args):
        ecc_client = self.app.client_manager.interconnectivity
        try:
            ops = ecc_client.show_operation(parsed_args.operation_id)
            printout = ops
        except exceptions.ClientException as clientexp:
            printout = {"message": clientexp.message,
                        "details": clientexp.details,
                        "code": clientexp.code}
        return zip(*sorted(six.iteritems(printout)))
