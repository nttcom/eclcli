# -*- coding: utf-8 -*-

import copy
import six
from eclcli.common import command
from eclcli.common import utils


class ListSnapshot(command.Lister):

    def get_parser(self, prog_name):
        parser = super(ListSnapshot, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.storage

        columns = [
            'ID',
            'Name',
            'Description',
            'Usage',
            'Volume ID',
            'Status',
          ]
        column_headers = copy.deepcopy(columns)

        data = client.snapshots()

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={'Metadata': utils.format_dict},
                ) for s in data))


class ShowSnapshot(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(ShowSnapshot, self).get_parser(prog_name)
        parser.add_argument(
            'snapshot_id',
            metavar='<string>',
            help='ID of snapshot to look up.')
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.storage

        rows = [
            'ID',
            'Name',
            'Status',
            'Description',
            'Usage',
            'Volume ID',
            'Snapshot Type ID',
            'Created At',
            'Updated At',
            'Deleted At',
            'Error Message',
            'Delete Reason',
        ]
        row_headers = rows

        data = client.get_snapshot(parsed_args.snapshot_id)

        return (row_headers, (utils.get_item_properties(data, rows)))


class CreateSnapshot(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(CreateSnapshot, self).get_parser(prog_name)
        parser.add_argument(
            'volume_id',
            metavar='<string>',
            help='ID of volume')
        parser.add_argument(
            "name",
            help="Name of snapshot",
            metavar='<string>'
        )
        parser.add_argument(
            "--description",
            help="Description of snapshot",
            metavar='<string>'
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.storage

        rows = [
            'ID',
            'Name',
            'Status',
            'Description',
            'Usage',
            'Volume ID',
            'Snapshot Type ID',
            'Created At',
            'Error Message',
        ]
        row_headers = rows

        data = client.create_snapshot(parsed_args.volume_id,
                                      parsed_args.name,
                                      description=parsed_args.description)

        return (row_headers, utils.get_item_properties(data, rows))


class UpdateSnapshot(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(UpdateSnapshot, self).get_parser(prog_name)
        parser.add_argument(
            'snapshot_id',
            metavar='<string>',
            help='ID of snapshot')
        parser.add_argument(
            "--name",
            help="Name of snapshot",
            metavar='<string>'
        )
        parser.add_argument(
            "--description",
            help="Description of snapshot",
            metavar='<string>'
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.storage

        rows = [
            'ID',
            'Name',
            'Status',
            'Description',
            'Usage',
            'Volume ID',
            'Snapshot Type ID',
            'Created At',
            'Updated At',
            'Deleted At',
            'Error Message',
            'Delete Reason',
        ]
        row_headers = rows

        body = {}
        if parsed_args.name:
            body["name"] = parsed_args.name
        if parsed_args.description:
            body["description"] = parsed_args.description
        data = client.update_snapshot(parsed_args.snapshot_id, **body)

        return (row_headers, utils.get_item_properties(data, rows))


class DeleteSnapshot(command.Command):

    def get_parser(self, prog_name):
        parser = super(DeleteSnapshot, self).get_parser(prog_name)
        parser.add_argument(
            "snapshot_ids",
            nargs="+",
            help="IDs of snapshot to be deleted",
            metavar='<string>'
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.storage
        for snapshot_id in parsed_args.snapshot_ids:
            client.delete_snapshot(snapshot_id)


class RestoreSnapshot(command.Command):

    def get_parser(self, prog_name):
        parser = super(RestoreSnapshot, self).get_parser(prog_name)
        parser.add_argument(
            'snapshot_id',
            metavar='<string>',
            help='ID of snapshot')
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.storage
        client.restore_snapshot(parsed_args.snapshot_id)
