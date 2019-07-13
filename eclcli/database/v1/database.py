# -*- coding: utf-8 -*-

import copy
import six
from eclcli.common import command
from eclcli.common import utils


class ListDatabase(command.Lister):

    def get_parser(self, prog_name):
        parser = super(ListDatabase, self).get_parser(prog_name)
        parser.add_argument(
            'instance_id',
            metavar='INSTANCE_ID',
            help='Database instance ID. UUID Format (8-4-4-4-12 style).',
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.database
        columns = [
            'Name',
            # 'Character Set',
            # 'Collate',
        ]
        column_headers = copy.deepcopy(columns)
        data = client.databases(parsed_args.instance_id)
        return (column_headers,
                (utils.get_item_properties(d, columns) for d in data))


class CreateDatabase(command.Command):

    def get_parser(self, prog_name):
        parser = super(CreateDatabase, self).get_parser(prog_name)
        parser.add_argument(
            'instance_id',
            metavar='INSTANCE_ID',
            help='Target database instance in which you would like to create '
                 'databases. UUID format (8-4-4-4-12 style).',
        )
        parser.add_argument(
            'name',
            metavar='NAME',
            help='Database name.',
        )
        parser.add_argument(
            '--character_set',
            metavar='<string>',
            help='Database character code. '
                 'Default value is UTF8.',
        )
        parser.add_argument(
            '--collate',
            metavar='<string>',
            help='Database collation. '
                 'Default value is C.',
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.database

        kwargs = {}
        if parsed_args.character_set:
            kwargs["charset"] = parsed_args.character_set
        if parsed_args.collate:
            kwargs["collate"] = parsed_args.collate

        data = client.create_database(
            parsed_args.instance_id,
            parsed_args.name,
            **kwargs)._body

        # data["databases"] = utils.format_list_of_dicts(data.pop('databases'))
        # return zip(*sorted(six.iteritems(data)))


class DeleteDatabase(command.Command):

    def get_parser(self, prog_name):
        parser = super(DeleteDatabase, self).get_parser(prog_name)
        parser.add_argument(
            'instance_id',
            metavar='INSTANCE_ID',
            help='The database instance ID in which you would like to delete '
                 'the target databases. UUID format (8-4-4-4-12 style).',
        )
        parser.add_argument(
            'name',
            metavar='NAME',
            help='The target database you want to delete.',
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.database
        client.delete_database(
            parsed_args.instance_id,
            parsed_args.name)
