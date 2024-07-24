import copy

import six

from eclcli.common import command
from eclcli.common import utils
from eclcli.i18n import _  # noqa
from eclcli.storage.storageclient import exceptions
from eclcli.storage.storageclient.utils import _set_request_body, \
    format_ip_addr_pool, format_host_routes


class ListStorage(command.Lister):
    _description = _("List storages")
    def get_parser(self, prog_name):
        parser = super(ListStorage, self).get_parser(prog_name)
        parser.add_argument(
            "--name",
            metavar="<string>",
            help="Filter results by virtual storage name")
        parser.add_argument(
            "--status",
            metavar="<string>",
            help="Filter results by status")
        return parser

    def take_action(self, parsed_args):
        storage_client = self.app.client_manager.storage

        search_opts = {
            'display_name': parsed_args.name,
            'status': parsed_args.status,
        }

        columns = ['ID', 'Name', 'Description', 'Network ID', 'Volume Type ID', 'Status']
        column_headers = copy.deepcopy(columns)

        data = storage_client.virtual_storages.list(search_opts=search_opts)

        if parsed_args.name is not None:
            data = utils.filter_list_with_property(data, "name", parsed_args.name)
        if parsed_args.status is not None:
            data = utils.filter_list_with_property(data, "status", parsed_args.status)

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={'Metadata': utils.format_dict},
                ) for s in data))


class ShowStorage(command.ShowOne):
    _description = _("Show storage")
    def get_parser(self, prog_name):
        parser = super(ShowStorage, self).get_parser(prog_name)
        parser.add_argument(
            "virtualstorage",
            metavar="VIRTUAL_STORAGE",
            help="virtual storage to display (ID)")
        return parser

    def take_action(self, parsed_args):
        storage_client = self.app.client_manager.storage
        try:
            virtual_storage = storage_client.virtual_storages.get(parsed_args.virtualstorage)
            printout = virtual_storage._info
        except exceptions.ClientException as clientexp:
            printout = {"message": clientexp.message,
                        "details": clientexp.details,
                        "code": clientexp.code}
        return zip(*sorted(six.iteritems(printout)))


class CreateStorage(command.ShowOne):
    _description = _("Create new storage")
    def get_parser(self, prog_name):
        parser = super(CreateStorage, self).get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar='<name>',
            required=True,
            help='Volume name.')
        parser.add_argument(
            '--description',
            metavar='<description>',
            default=None,
            help='Volume description.')
        parser.add_argument(
            '--volume_type_id',
            metavar='VOLUME_TYPE_ID',
            required=True,
            help='Volume type.')
        parser.add_argument(
            '--network_id',
            metavar='NETWORK_ID',
            required=True,
            help='ID of network.')
        parser.add_argument(
            '--subnet_id',
            metavar='SUBNET_ID',
            required=True,
            help='ID of subnet.')
        parser.add_argument(
            '--ip_addr_pool',
            metavar='<address_from,address_to>',
            required=True,
            help='Range of ip address specified as from, to. Default=None.')
        parser.add_argument(
            '--host_route',
            metavar='<dest_cidr,nexthop>',
            action='append',
            default=[],
            help='Host route. '
                 'In case destination is 192.168.1.0/24 and '
                 'next hop is 10.0.0.254, '
                 'please write like "192.168.1.0/24,10.0.0.254"')
        return parser

    def take_action(self, parsed_args):
        storage_client = self.app.client_manager.storage
        param_list = ['name', 'description',
                      'volume_type_id', 'network_id', 'subnet_id']
        body = _set_request_body(parsed_args, param_list)

        ip_addr_pool = format_ip_addr_pool(parsed_args.ip_addr_pool)
        body.update({'ip_addr_pool': ip_addr_pool})

        hr_array = format_host_routes(parsed_args.host_route)
        body.update({'host_routes': hr_array})

        try:
            virtual_storage = storage_client.virtual_storages.create(**body)
            printout = virtual_storage._info
        except exceptions.ClientException as clientexp:
            printout = {"message": clientexp.message,
                        "details": clientexp.details,
                        "code": clientexp.code}
        return zip(*sorted(six.iteritems(printout)))


class UpdateStorage(command.ShowOne):
    _description = _("Update storage")
    def get_parser(self, prog_name):
        parser = super(UpdateStorage, self).get_parser(prog_name)

        parser.add_argument(
            'virtualstorage',
            metavar='VIRTUAL_STORAGE_ID',
            help='Name or ID of virtual storage to update.')

        parser.add_argument(
            '--name',
            metavar='<name>',
            default=None,
            help='Volume name. Default=None.')

        parser.add_argument(
            '--description',
            metavar='<description>',
            default=None,
            help='Volume description. Default=None.')

        parser.add_argument(
            '--ip_addr_pool',
            metavar='<address_from,address_to>',
            help='Range of ip address specified as from, to. Default=None.')

        parser.add_argument(
            '--host_route',
            metavar='<dest_cidr,nexthop>',
            action='append',
            help='Host route. '
                 'In case destination is 192.168.1.0/24 and '
                 'next hop is 10.0.0.254, '
                 'please write like "192.168.1.0/24,10.0.0.254"')
        return parser

    def take_action(self, parsed_args):
        storage_client = self.app.client_manager.storage
        param_list = ['name', 'description']
        body = _set_request_body(parsed_args, param_list)

        if hasattr(parsed_args, "ip_addr_pool") and parsed_args.ip_addr_pool is not None:
            ip_addr_pool = format_ip_addr_pool(parsed_args.ip_addr_pool)
            body.update({'ip_addr_pool': ip_addr_pool})

        if hasattr(parsed_args, "host_route") and parsed_args.host_route is not None:
            if len(parsed_args.host_route) > 0:
                hr_array = format_host_routes(parsed_args.host_route)
                body.update({'host_routes': hr_array})
        try:
            virtual_storage = storage_client.virtual_storages.update(
                parsed_args.virtualstorage, **body)
            printout = virtual_storage._info
        except exceptions.ClientException as clientexp:
            printout = {"message": clientexp.message,
                        "details": clientexp.details,
                        "code": clientexp.code}
        return zip(*sorted(six.iteritems(printout)))


class DeleteStorage(command.ShowOne):
    _description = _("Delete storage")
    def get_parser(self, prog_name):
        parser = super(DeleteStorage, self).get_parser(prog_name)

        parser.add_argument(
            'virtualstorage',
            metavar='VIRTUAL_STORAGE_ID',
            nargs='+',
            default=[],
            help='Name or ID of virtual storage to delete.')
        return parser

    def take_action(self, parsed_args):
        storage_client = self.app.client_manager.storage
        printout = {}
        for vs in parsed_args.virtualstorage:
            try:
                resp, body = storage_client.virtual_storages.delete(vs)
                message = ""
                if body is not None:
                    message = body.get("api_error_message")
                printout[vs] = {
                    "status_code": resp.status_code,
                    "api_error_message": message}
            except exceptions.ClientException as clientexp:
                printout[vs] = {"message": clientexp.message,
                                "details": clientexp.details,
                                "code": clientexp.code}

        return zip(*sorted(six.iteritems(printout)))
