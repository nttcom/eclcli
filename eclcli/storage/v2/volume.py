import copy

import six

from eclcli.common import command
from eclcli.common import utils
from eclcli.i18n import _  # noqa
from eclcli.storage.storageclient import exceptions
from eclcli.storage.storageclient.utils import _set_request_body


class ListVolume(command.Lister):
    _description = _("List volumes of storage")
    def get_parser(self, prog_name):
        parser = super(ListVolume, self).get_parser(prog_name)
        parser.add_argument(
            "--name",
            metavar="<string>",
            help="Filter results by virtual storage name")
        parser.add_argument(
            "--status",
            metavar="<string>",
            help="Filter results by status")
        parser.add_argument(
            "--virtual_storage_id",
            metavar="<virtual_storage_id>",
            help="Filter results by virtual_storage_id")

        return parser

    def take_action(self, parsed_args):
        storage_client = self.app.client_manager.storage
        search_opts = {
            'display_name': parsed_args.name,
            'status': parsed_args.status,
        }

        columns = ['id', 'name', 'size', 'throughput',
                   'iops_per_gb', 'initiator_iqns', 'virtual_storage_id',
                   'status']
        column_headers = copy.deepcopy(columns)
        data = storage_client.volumes.list(search_opts=search_opts)

        if parsed_args.virtual_storage_id is not None:
            data = utils.filter_list_with_property(data, "virtual_storage_id", parsed_args.virtual_storage_id)
        if parsed_args.name is not None:
            data = utils.filter_list_with_property(data, "name", parsed_args.name)
        if parsed_args.status is not None:
            data = utils.filter_list_with_property(data, "status", parsed_args.status)

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={'Metadata': utils.format_dict},
                ) for s in data))


class ShowVolume(command.ShowOne):
    _description = _("Show volume of storage")
    def get_parser(self, prog_name):
        parser = super(ShowVolume, self).get_parser(prog_name)
        parser.add_argument(
            'volume',
            metavar='VOLUME_ID',
            help='ID of volume to look up.')
        return parser

    def take_action(self, parsed_args):
        storage_client = self.app.client_manager.storage
        try:
            volume = storage_client.volumes.get(parsed_args.volume)
            printout = volume._info
        except exceptions.ClientException as clientexp:
            printout = {"message": clientexp.message,
                        "details": clientexp.details,
                        "code": clientexp.code}
        return zip(*sorted(six.iteritems(printout)))


class CreateVolume(command.ShowOne):
    _description = _("Create new volume of storage")
    def get_parser(self, prog_name):
        parser = super(CreateVolume, self).get_parser(prog_name)

        parser.add_argument(
            '--name',
            metavar='<string>',
            required=True,
            help='Name. Default=None.')

        parser.add_argument(
            '--size',
            metavar='<number>',
            required=True,
            type=int,
            help='Size. Default=None.')

        parser.add_argument(
            '--virtual_storage_id',
            metavar='<VIRTUAL_STORAGE_ID>',
            required=True,
            help='Virtual Storage ID. Default=None.')

        parser.add_argument(
            '--description',
            metavar='<string>',
            default=None,
            help='Volume description. Default=None.')

        parser.add_argument(
            '--availability_zone',
            metavar='<string>',
            help='Volume name. ')

        parser.add_argument(
            '--throughput',
            metavar='<number>',
            type=int,
            default=None,
            help='Throughput of NFS type. Default=None.')

        parser.add_argument(
            '--iops_per_gb',
            metavar='<number>',
            default=None,
            help='IOPS/GB of iscsi type. Default=2.')

        parser.add_argument(
            '--initiator_iqns',
            metavar='<array>',
            action='append',
            default=None,
            help='Initial iqns of iscsi type. Default=None.'
                 'You can repeat this option.')

        return parser

    def take_action(self, parsed_args):
        param_list = ['size', 'name', 'description', 'iops_per_gb',
                      'initiator_iqns', 'throughput',
                      'virtual_storage_id', 'availability_zone']

        body = _set_request_body(parsed_args, param_list)
        body.update({"metadata": None})
        storage_client = self.app.client_manager.storage
        try:
            volume = storage_client.volumes.create(**body)
            printout = volume._info
        except exceptions.ClientException as clientexp:
            printout = {"message": clientexp.message,
                        "details": clientexp.details,
                        "code": clientexp.code}
        return zip(*sorted(six.iteritems(printout)))


class UpdateVolume(command.ShowOne):
    _description = _("Update volume of storage")
    def get_parser(self, prog_name):
        parser = super(UpdateVolume, self).get_parser(prog_name)

        parser.add_argument(
            'volume',
            metavar='VOLUME_ID',
            help='ID of volume to update.')

        parser.add_argument(
            '--name',
            metavar='<string>',
            help='Name of volume to update. Default=None.')

        parser.add_argument(
            '--description',
            metavar='<string>',
            default=None,
            help='Description of volume to update. Default=None.')

        parser.add_argument(
            '--initiator_iqns',
            metavar='<array>',
            action='append',
            default=None,
            help='Initial iqns of volume to update. Default=None.'
                 'You can repeat this option.')
        return parser

    def take_action(self, parsed_args):
        param_list = ['name', 'description',
                      'initiator_iqns']

        body = _set_request_body(parsed_args, param_list)
        storage_client = self.app.client_manager.storage
        try:
            volume = storage_client.volumes.update(parsed_args.volume, **body)
            printout = volume._info
        except exceptions.ClientException as clientexp:
            printout = {"message": clientexp.message,
                        "details": clientexp.details,
                        "code": clientexp.code}
        return zip(*sorted(six.iteritems(printout)))


class DeleteVolume(command.ShowOne):
    _description = _("Delete volume of storage")
    def get_parser(self, prog_name):
        parser = super(DeleteVolume, self).get_parser(prog_name)

        parser.add_argument(
            'volume',
            metavar='VOLUME_ID',
            nargs='+',
            help='Name or ID of volume to delete.')
        return parser

    def take_action(self, parsed_args):
        storage_client = self.app.client_manager.storage
        printout = {}
        for vol in parsed_args.volume:
            try:
                resp, body = storage_client.volumes.delete(vol)
                message = ""
                if body is not None:
                    message = body.get("api_error_message")
                printout[vol] = {"status code": resp.status_code,
                                 "api_error_message": message}
            except exceptions.ClientException as clientexp:
                printout[vol] = {"status code": clientexp.code,
                                 "api_error_message": clientexp.message,
                                 "details": clientexp.details}
        return zip(*sorted(six.iteritems(printout)))

