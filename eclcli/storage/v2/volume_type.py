import copy

import six

from eclcli.common import command
from eclcli.common import utils
from eclcli.storage.storageclient import exceptions


class ListVolumeType(command.Lister):

    def get_parser(self, prog_name):
        parser = super(ListVolumeType, self).get_parser(prog_name)
        parser.add_argument(
            "--name",
            metavar="<string>",
            help="Filter results by virtual storage name")
        return parser

    def take_action(self, parsed_args):
        storage_client = self.app.client_manager.storage

        search_opts = {
            'display_name': parsed_args.name,
        }

        columns = ['ID', 'Name', 'available_volume_size',
                   'available_volume_throughput',
                   'available_iops_per_gb']
        column_headers = copy.deepcopy(columns)

        data = storage_client.volume_types.list(search_opts=search_opts)

        if parsed_args.name is not None:
            data = utils.filter_list_with_property(data, "name", parsed_args.name)

        for vtype in data:
            for key, value in vtype.extra_specs.items():
                setattr(vtype, key, value)

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowVolumeType(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(ShowVolumeType, self).get_parser(prog_name)
        parser.add_argument(
            "volume_type",
            metavar="VOLUME_TYPE_ID",
            help="volume type to display (ID)")
        return parser

    def take_action(self, parsed_args):
        storage_client = self.app.client_manager.storage
        try:
            volume_type = storage_client.volume_types.get(parsed_args.volume_type)
            printout = volume_type._info
            for key, value in printout.get("extra_specs").items():
                printout[key] = copy.copy(value)
            del printout["extra_specs"]
        except exceptions.ClientException as clientexp:
            printout = {"message": clientexp.message,
                        "details": clientexp.details,
                        "code": clientexp.code}
        return zip(*sorted(six.iteritems(printout)))
