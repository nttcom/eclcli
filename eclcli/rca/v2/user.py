# -*- coding: utf-8 -*-


from eclcli.common import command

from eclcli.common import exceptions
from eclcli.common import utils
from ..rcaclient.common.utils import objectify


class ListUser(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListUser, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        rca_client = self.app.client_manager.rca

        columns = (
            'name',
            'vpn_endpoints'
        )
        column_headers = (
            'Name',
            'VPN Endpoints'
        )

        data = rca_client.users.list()
        return (column_headers,
                (utils.get_item_properties(
                    s, columns, formatters={'vpn_endpoints': utils.format_list_of_dicts}
                ) for s in data))


class ShowUser(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(ShowUser, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help="User Name for Inter Connect Gateway Service"
        )
        return parser

    def take_action(self, parsed_args):
        rca_client = self.app.client_manager.rca
        name = parsed_args.name
        try:
            user = rca_client.users.get(name)
            printout = user._info
        except exceptions.ClientException as clientexp:
            printout = {"code": clientexp.code,
                        "message": clientexp.message}
        columns = utils.get_columns(printout)
        data = utils.get_item_properties(
          objectify(printout),
          columns,
          formatters={'vpn_endpoints': utils.format_list_of_dicts})
        return columns, data


class CreateUser(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(CreateUser, self).get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar='<name>',
            help="User Name for Inter Connect Gateway Service")
        parser.add_argument(
            '--password',
            metavar='<password>',
            default=None,
            help="User Password for Inter Connect Gateway Service")
        return parser

    def take_action(self, parsed_args):
        rca_client = self.app.client_manager.rca
        name = parsed_args.name
        password = parsed_args.password
        try:
            user = rca_client.users.create(name, password)
            printout = user._info
        except exceptions.ClientException as clientexp:
            printout = {"code": clientexp.code,
                        "message": clientexp.message}
        columns = utils.get_columns(printout)
        data = utils.get_item_properties(
          objectify(printout),
          columns,
          formatters={'vpn_endpoints': utils.format_list_of_dicts})
        return columns, data

  
class SetUser(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(SetUser, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help="User Name for Inter Connect Gateway Service")
        parser.add_argument(
            '--password',
            metavar='<password>',
            default=None,
            help="User Password for Inter Connect Gateway Service")
        return parser

    def take_action(self, parsed_args):
        rca_client = self.app.client_manager.rca
        name = parsed_args.name
        password = parsed_args.password
        try:
            user = rca_client.users.update(name, password)
            printout = user._info
        except exceptions.ClientException as clientexp:
            printout = {"code": clientexp.code,
                        "message": clientexp.message}
        columns = utils.get_columns(printout)
        data = utils.get_item_properties(
          objectify(printout),
          columns,
          formatters={'vpn_endpoints': utils.format_list_of_dicts})
        return columns, data


class DeleteUser(command.Command):
    def get_parser(self, prog_name):
        parser = super(DeleteUser, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help="User Name for Inter Connect Gateway Service")
        return parser

    def take_action(self, parsed_args):
        rca_client = self.app.client_manager.rca
        name = parsed_args.name
        rca_client.users.delete(name)
