import argparse
import getpass
import io
import os
import six
import sys

from eclcli.common import command
from eclcli.bare import bare_utils
from eclcli.common import utils


class ListVersion(command.Lister):
    """List baremetal API versions"""

    def get_parser(self, prog_name):
        parser = super(ListVersion, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        bare_client = self.app.client_manager.bare
        identity_client = self.app.client_manager.identity

        search_opts = {}
        self.log.debug('search options: %s', search_opts)

        columns = (
            'ID',
            'Status',
        )

        data = bare_client.versions.list()
        return (columns,
                (utils.get_item_properties(s, columns) 
                for s in data))



class ShowVersion(command.ShowOne):
    """Show baremetal API version details"""

    def get_parser(self, prog_name):
        parser = super(ShowVersion, self).get_parser(prog_name)
        parser.add_argument(
            "version",
            metavar="<version>",
            help="Version ID",
        )
        return parser

    def take_action(self, parsed_args):
        bare_client = self.app.client_manager.bare
        identity_client = self.app.client_manager.identity

        columns = (
            'ID',
            'Status',
            'Links',
        )

        data = bare_client.versions.get(parsed_args.version)
        return (columns,utils.get_item_properties(
            data,
            columns,
            mixed_case_fields = [],
            formatters = {
                'Links': bare_utils._format_links
            }
        ))


