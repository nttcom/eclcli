# -*- coding: utf-8 -*-

import six

from eclcli.common import command
from eclcli.common import utils
from eclcli.i18n import _  # noqa


class ListVersion(command.Lister):
    _description = _("List versions of remote console access")
    def get_parser(self, prog_name):
        parser = super(ListVersion, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.rca

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

        data = client.versions()
        return (column_headers,
                (utils.get_item_properties(
                    s, columns, formatters={'links': utils.format_list_of_dicts}
                ) for s in data))


class ShowVersion(command.ShowOne):
    _description = _("Show version of remote console access")
    def get_parser(self, prog_name):
        parser = super(ShowVersion, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.rca
        data = client.get_version()._body
        return zip(*sorted(six.iteritems(data)))
