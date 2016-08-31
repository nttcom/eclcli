
import six

from eclcli.common import command
from eclcli.common import exceptions
from eclcli.common import utils
from ..interconnectivityclient.common.utils import objectify, get_request_body


class ListCIC(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListCIC, self).get_parser(prog_name)
        parser.add_argument(
            "--mcic_id",
            metavar="<mcic_id>",
            required=True,
            help="id of mcic to list CIC (ID)")
        return parser

    def take_action(self, parsed_args):
        connectivity_client = self.app.client_manager.interconnectivity

        columns = (
            'cic_id',
            'cic_name',
            'cic_status',
        )
        column_headers = (
            'ID',
            'Name',
            'Status',
        )

        data = [objectify(cic)
                for cic in connectivity_client.list_cics(parsed_args.mcic_id)]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowCIC(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(ShowCIC, self).get_parser(prog_name)
        parser.add_argument(
            "--mcic_id",
            metavar="<mcic_id>",
            required=True,
            help="mcic to display (ID)")
        parser.add_argument(
            "--cic_id",
            metavar="<cic_id>",
            required=True,
            help="cic to display (ID)")
        return parser

    def take_action(self, parsed_args):
        ecc_client = self.app.client_manager.interconnectivity
        try:
            cic = ecc_client.show_cic(parsed_args.mcic_id, parsed_args.cic_id)
            printout = cic
        except exceptions.ClientException as clientexp:
            printout = {"message": clientexp.message,
                        "details": clientexp.details,
                        "code": clientexp.code}
        return zip(*sorted(six.iteritems(printout)))


class CreateCIC(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(CreateCIC, self).get_parser(prog_name)
        parser.add_argument(
            '--mcic_id',
            metavar='<mcic_id>',
            required=True,
            help='mCIC ID [Type: String]')
        parser.add_argument(
            '--cic_name',
            metavar='<cic_name>',
            required=True,
            help='CIC friendly name [Type: String]')
        parser.add_argument(
            '--logical_nw_id',
            metavar='<logical_nw_id>',
            required=True,
            help='NGC logical NW ID [Type: String]')
        parser.add_argument(
            '--colo_vlan_id',
            metavar='<colo_vlan_id>',
            help='Co-location VLAN ID  [Type: Int]')
        parser.add_argument(
            '--server_segment_nbr',
            metavar='<server_segment_nbr>',
            help='Server Segment Number [Type: Int]')
        return parser

    def take_action(self, parsed_args):
        ecc_client = self.app.client_manager.interconnectivity
        required = ('cic_name', 'logical_nw_id')
        optional = ('colo_vlan_id', 'server_segment_nbr')
        body = get_request_body(parsed_args, required, optional)
        try:
            cic = ecc_client.create_cic(body, parsed_args.mcic_id)
            printout = cic
        except exceptions.ClientException as clientexp:
            printout = {"message": clientexp.message,
                        "details": clientexp.details,
                        "code": clientexp.code}
        return zip(*sorted(six.iteritems(printout)))


class UpdateCIC(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(UpdateCIC, self).get_parser(prog_name)
        parser.add_argument(
            '--mcic_id',
            metavar='<mcic_id>',
            required=True,
            help='mCIC ID [Type: String]')
        parser.add_argument(
            '--cic_id',
            metavar='<cic_id>',
            required=True,
            help='CIC ID [Type: String]')
        parser.add_argument(
            '--cic_name',
            metavar='<cic_name>',
            help='CIC friendly name [Type: String]')
        return parser

    def take_action(self, parsed_args):
        ecc_client = self.app.client_manager.interconnectivity
        required = ()
        optional = ('cic_name',)
        body = get_request_body(parsed_args, required, optional)
        try:
            cic = ecc_client.update_cic(body=body, mcic_id=parsed_args.mcic_id,cic_id=parsed_args.cic_id, )
            printout = cic
        except exceptions.ClientException as clientexp:
            printout = {"message": clientexp.message,
                        "details": clientexp.details,
                        "code": clientexp.code}
        return zip(*sorted(six.iteritems(printout)))


class DeleteCIC(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(DeleteCIC, self).get_parser(prog_name)
        parser.add_argument(
            "--mcic_id",
            metavar="<mcic_id>",
            required=True,
            help="mcic to display (ID)")
        parser.add_argument(
            "--cic_id",
            metavar="<cic_id>",
            required=True,
            help="cic to display (ID)")
        return parser

    def take_action(self, parsed_args):
        ecc_client = self.app.client_manager.interconnectivity
        try:
            cic = ecc_client.delete_cic(parsed_args.mcic_id, parsed_args.cic_id)
            printout = cic
        except exceptions.ClientException as clientexp:
            printout = {"message": clientexp.message,
                        "details": clientexp.details,
                        "code": clientexp.code}
        return zip(*sorted(six.iteritems(printout)))
