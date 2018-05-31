# -*- coding: utf-8 -*-

import copy
import six
from eclcli.common import command
from eclcli.common import utils


class ListUser(command.Lister):

    def get_parser(self, prog_name):
        parser = super(ListUser, self).get_parser(prog_name)
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
            # 'Host',
            'Databases',
        ]
        column_headers = copy.deepcopy(columns)
        data = client.users(parsed_args.instance_id)
        # data["databases"] = utils.format_list_of_dicts(data.pop('databases'))
        return (column_headers,
                (utils.get_item_properties(d, columns, formatters={
                    'Databases': utils.format_list_of_dicts}) for d in data))


class ShowUser(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(ShowUser, self).get_parser(prog_name)
        parser.add_argument(
            'instance_id',
            metavar='INSTANCE_ID',
            help='Database instance ID. UUID Format (8-4-4-4-12 style).',
        )
        parser.add_argument(
            'name',
            metavar='NAME',
            help='The user name you want to show in detail.',
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.database

        data = client.get_user(
            parsed_args.instance_id, parsed_args.name)._body

        data["databases"] = utils.format_list_of_dicts(data.pop('databases'))
        return zip(*sorted(six.iteritems(data)))


class CreateUser(command.Command):

    def get_parser(self, prog_name):
        parser = super(CreateUser, self).get_parser(prog_name)
        parser.add_argument(
            'instance_id',
            metavar='INSTANCE_ID',
            help='Target database instance in which you would like to create '
                 'databases. UUID format (8-4-4-4-12 style).',
        )
        parser.add_argument(
            'name',
            metavar='NAME',
            help='Database user name. (1~63 characters). Allowed characters '
                 'depend on database type.',
        )
        parser.add_argument(
            'password',
            metavar='PASSWORD',
            help='Database user password. (8~128 characters). Allowed '
                 'characters depend on database type.',
        )
        parser.add_argument(
            '--databases',
            metavar='<string>',
            action='append',
            type=utils.parse_databases,
            help='Databases that user can access.'
                 'You can repeat this option.',
        )
        return parser


    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.database

        kwargs = {}
        if parsed_args.databases:
            kwargs["databases"] = parsed_args.databases

        data = client.create_user(
            parsed_args.instance_id,
            parsed_args.name,
            parsed_args.password,
            **kwargs)._body

        # data["databases"] = utils.format_list_of_dicts(data.pop('databases'))
        # return zip(*sorted(six.iteritems(data)))


class DeleteUser(command.Command):

    def get_parser(self, prog_name):
        parser = super(DeleteUser, self).get_parser(prog_name)
        parser.add_argument(
            'instance_id',
            metavar='INSTANCE_ID',
            help='The instance ID from which you would like to delete an user.',
        )
        parser.add_argument(
            'name',
            metavar='NAME',
            help='The user name you want to delete from the instance.',
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.database
        client.delete_user(
            parsed_args.instance_id,
            parsed_args.name,
        )


class GrantUser(command.Command):

    def get_parser(self, prog_name):
        parser = super(GrantUser, self).get_parser(prog_name)
        parser.add_argument(
            'instance_id',
            metavar='INSTANCE_ID',
            help='Target database instance ID. UUID format (8-4-4-4-12 style).',
        )
        parser.add_argument(
            'name',
            metavar='NAME',
            help='Users to whom some privileges are granted.',
        )
        parser.add_argument(
            '--databases',
            metavar='<string>',
            action='append',
            type=utils.parse_databases,
            required=True,
            help='Database list on which you grant privileges to user.'
                 'You can repeat this option.',
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.database
        client.grant_user(
            parsed_args.instance_id,
            parsed_args.name,
            parsed_args.databases,
        )



class RevokeUser(command.Command):

    def get_parser(self, prog_name):
        parser = super(RevokeUser, self).get_parser(prog_name)
        parser.add_argument(
            'instance_id',
            metavar='INSTANCE_ID',
            help='Target database instance ID. UUID format (8-4-4-4-12 style).',
        )
        parser.add_argument(
            'user_name',
            metavar='USER_NAME',
            help='User from whom some privileges are revoked.',
        )
        parser.add_argument(
            'database_name',
            metavar='DATABASE_NAME',
            help='Database name on which privileges are revoked from user.',
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.database
        client.revoke_user(
            parsed_args.instance_id,
            parsed_args.user_name,
            parsed_args.database_name,
        )
