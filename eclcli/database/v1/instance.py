# -*- coding: utf-8 -*-

import copy
import six
from eclcli.common import command
from eclcli.common import utils


class ListInstance(command.Lister):

    def get_parser(self, prog_name):
        parser = super(ListInstance, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.database
        columns = [
            'ID',
            'Name',
            'Datastore',
            'Volume',
            'Backup Retention Period',
            'Restorable Time',
            'Backup Window',
            'Status',
        ]
        column_headers = copy.deepcopy(columns)
        data = client.instances()
        return (column_headers,
            (utils.get_item_properties(d, columns, formatters={
                'Datastore': utils.format_dict,
                'Volume': utils.format_dict}) for d in data))


class ShowInstance(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(ShowInstance, self).get_parser(prog_name)
        parser.add_argument(
            'instance_id',
            metavar='INSTANCE_ID',
            help='Target database instance ID.',
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.database

        data = client.get_instance(parsed_args.instance_id)._body

        if data.get('datastore'):
            data["datastore"] = utils.format_dict(data.pop('datastore'))
        if data.get('volume'):
            data["volume"] = utils.format_dict(data.pop('volume'))
        if data.get('flavor'):
            data["flavor"] = utils.format_dict(data.pop('flavor'))
        if data.get('links'):
            data["links"] = utils.format_list_of_dicts(data.pop('links'))
        return zip(*sorted(six.iteritems(data)))


class CreateInstance(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(CreateInstance, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='NAME',
            help='Database instance name.',
        )
        parser.add_argument(
            'flavor',
            metavar='FLAVOR',
            help='Actual name to a flavor as it appears in the list flavors '
                 'response. (You can get it by <ecl rdb flavor list>)',
        )
        parser.add_argument(
            'size',
            metavar='SIZE',
            type=utils.parse_volume,
            help='Disk volume size(GB) for your instance. '
                 'You can specify 40, 80, 100 or 300.',
        )
        parser.add_argument(
            'type',
            metavar='TYPE',
            help='Database(Datastore) type which you would like to create into '
                 'database instance. e.g. postgresql '
                 '(You can get it by <ecl rdb datastore list>)',
        )
        parser.add_argument(
            'version',
            metavar='VERSION',
            help='Database version of the target Database type. e.g. 9.5.4'
                 '(You can get it by <ecl rdb datastore list>)',
        )
        parser.add_argument(
            '--network_id',
            metavar='<string>',
            required=True,
            action='append',
            type=utils.parse_net_id,
            help='Logical network ID to which the database instance connects. '
                 'This parameter is required. '
                 'You can repeat this option.',
        )

        parser.add_argument(
            '--database_name',
            metavar='<string>',
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
        parser.add_argument(
            '--user_name',
            metavar='<string>',
            help='Database user name. (1~63 characters). Allowed characters '
                 'depend on database type.',
        )
        parser.add_argument(
            '--password',
            metavar='<string>',
            help='Database user password. (8~128 characters). Allowed '
                 'characters depend on database type.',
        )
        parser.add_argument(
            '--revoke_user',
            action='store_true',
            default=False,
            help='Please specify it '
                 'if you do not want to associate this user to the database '
                 'you specified at --database_name option.',
        )
        parser.add_argument(
            '--availability_zone',
            metavar='<string>',
            help='Availability zone where database instance install.',
        )
        parser.add_argument(
            '--backup_window',
            metavar='<string>',
            help='The range of backing up time (UTC). '
                 'Please specify it like HH:mm-HH:mm. '
                 'Default value is 23:00-06:00.',
        )
        parser.add_argument(
            '--backup_retention_period',
            metavar='<integer>',
            help='The days how long back-up data should be kept. '
                 'Please specify it between 0 to 35.'
                 'Default value is 7.',
        )
        parser.add_argument(
            '--maintenance_window',
            metavar='<string>',
            help='ECL2.0 periodical maintenance. '
                 'Please specify it like EEE:HH:mm-EEE:HH:mm. '
                 'Default value is Sun:23:00-Mon:05:00.',
        )
        parser.add_argument(
            '--restore_time',
            metavar='<string>',
            help='The time you want to restore. (e.g. 2018-06-11T11:25:35Z)',
        )
        parser.add_argument(
            '--restore_instance_id',
            metavar='<string>',
            help='Instance ID from which you want to restore and create '
                 'new database instance.',
        )
        return parser


    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.database
        kwargs = {}

        if parsed_args.database_name:
            databases = {"name": parsed_args.database_name}
            if parsed_args.character_set:
                databases.update({"character_set": parsed_args.character_set})
            if parsed_args.collate:
                databases.update({"collate": parsed_args.collate})
            kwargs["databases"] = [databases]

        if parsed_args.user_name and parsed_args.password:
            users = {
                "name": parsed_args.user_name,
                "password": parsed_args.password,
            }
            if not parsed_args.revoke_user and parsed_args.database_name:
                users.update(
                    {"databases": [{"name": parsed_args.database_name}]})
            kwargs["users"] = [users]

        if parsed_args.availability_zone:
            kwargs["availability_zone"] = parsed_args.availability_zone
        if parsed_args.backup_window:
            kwargs["backup_window"] = parsed_args.backup_window
        if parsed_args.backup_retention_period:
            kwargs["backup_retention_period"] = \
                parsed_args.backup_retention_period
        if parsed_args.maintenance_window:
            kwargs["maintenance_window"] = parsed_args.maintenance_window
        if parsed_args.restore_time and parsed_args.restore_instance_id:
            kwargs["restore_point"] = {
                "restore_time": parsed_args.restore_time,
                "instance_id": parsed_args.restore_instance_id,
            }

        data = client.create_instance(
            parsed_args.name,
            parsed_args.flavor,
            parsed_args.size,
            {"type": parsed_args.type, "version": parsed_args.version},
            parsed_args.network_id,
            **kwargs)._body

        data["datastore"] = utils.format_dict(data.pop('datastore'))
        data["volume"] = utils.format_dict(data.pop('volume'))
        data["flavor"] = utils.format_dict(data.pop('flavor'))
        data["links"] = utils.format_list_of_dicts(data.pop('links'))
        data["nics"] = utils.format_list_of_dicts(data.pop('nics'))
        if data.get("users"):
            data["users"] = utils.format_list_of_dicts(data.pop('users'))
        if data.get("databases"):
            data["databases"] = utils.format_list_of_dicts(
                data.pop('databases'))
        return zip(*sorted(six.iteritems(data)))


class DeleteInstance(command.Command):

    def get_parser(self, prog_name):
        parser = super(DeleteInstance, self).get_parser(prog_name)
        parser.add_argument(
            'instance_id',
            metavar='INSTANCE_ID',
            help='Specify the instance to be deleted. UUID Format(8-4-4-4-12).',
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.database
        client.delete_instance(parsed_args.instance_id)
