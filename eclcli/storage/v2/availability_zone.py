# -*- coding: utf-8 -*-


import copy


from eclcli.common import command
from eclcli.common import utils
from eclcli.i18n import _  # noqa


class ListAvailabilityZone(command.Lister):
    _description = _("List availability-zones of storage")

    def get_parser(self, prog_name):
        parser = super(ListAvailabilityZone, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        storage_client = self.app.client_manager.storage

        columns = ['zoneName', 'zoneState', ]
        column_headers = copy.deepcopy(columns)

        data = storage_client.availability_zones.list(detailed=True)

        return (column_headers,
                (utils.get_item_properties(
                    s, columns, columns
                ) for s in data))
