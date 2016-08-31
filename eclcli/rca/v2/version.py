# -*- coding: utf-8 -*-

from eclcli.common import command

from eclcli.common import exceptions
from eclcli.common import utils
from ..rcaclient.common.utils import objectify


class ListVersion(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListVersion, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        rca_client = self.app.client_manager.rca

        columns = (
            'status',
            'id',
            'links'
        )
        column_headers = (
            'Status',
            'ID',
            'Links'
        )

        data = rca_client.versions.list()
        return (column_headers,
                (utils.get_item_properties(
                    s, columns, formatters={'links': utils.format_list_of_dicts}
                ) for s in data))


class ShowVersion(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(ShowVersion, self).get_parser(prog_name)
        parser.add_argument(
            'version',
            metavar='<version>',
            help="API version for Inter Connect Gateway Service"
        )
        return parser

    def take_action(self, parsed_args):
        rca_client = self.app.client_manager.rca
        version = parsed_args.version
        try:
            version_info = rca_client.versions.get(version)
            printout = version_info._info
        except exceptions.ClientException as clientexp:
            printout = {"code": clientexp.code,
                        "message": clientexp.message,}
        columns = utils.get_columns(printout)
        data = utils.get_item_properties(
          objectify(printout),
          columns,
          formatters={'links': utils.format_list_of_dicts})
        return columns, data
