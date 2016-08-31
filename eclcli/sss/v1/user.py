# -*- coding: utf-8 -*-

from eclcli.common import command
from eclcli.common import exceptions
from eclcli.common import utils
from eclcli.identity import common as identity_common
from ..sssclient.common.utils import objectify


class ListUser(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListUser, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        sss_client = self.app.client_manager.sss

        columns = (
            'login_id',
            'mail_address',
            'user_id',
            'contract_owner',
            'contract_id'
        )
        column_headers = (
            'Login ID',
            'Address',
            'User ID',
            'Contract Owner',
            'Contract ID',
        )

        users_dict = sss_client.list_users()
        contract_id = users_dict.get('contract_id')
        users = users_dict.get('users')
        map(lambda user:user.update({'contract_id': contract_id}), users)

        data = [objectify(user) for user in users]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowUser(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(ShowUser, self).get_parser(prog_name)
        parser.add_argument(
            'user_id',
            metavar="<uuid>",
            help=("user's id which you need to get information. (ecidXXXXXXXXX)")
        )
        return parser

    def take_action(self, parsed_args):
        sss_client = self.app.client_manager.sss
        user_id = parsed_args.user_id
        user = sss_client.show_user(user_id)
        columns = utils.get_columns(user)
        obj = objectify(user)
        data = utils.get_item_properties(obj, columns)
        return columns, data


class CreateUser(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(CreateUser, self).get_parser(prog_name)
        parser.add_argument(
            'login_id',
            metavar='<login_id>',
            help='Login id of new user.'
        )
        parser.add_argument(
            'mail_address',
            metavar='<mail_address>',
            help='Mail address of new user.'
        )
        parser.add_argument(
            'notify_password',
            metavar='<boolean>',
            type=utils.parse_bool,
            choices=[True, False],
            help='If this flag is set true, notification eamil will be sent to new users email.'
        )
        parser.add_argument(
            '--password',
            metavar='<password>',
            help='Initial password of new user. If this parameter is not designated, '
                 'random initial password is generated and applied to new user.'
        )
        return parser

    def take_action(self, parsed_args):
        sss_client = self.app.client_manager.sss

        body = {}
        if parsed_args.login_id is not None:
            body['login_id'] = str(parsed_args.login_id)
        if parsed_args.mail_address is not None:
            body['mail_address'] = str(parsed_args.mail_address)
        if parsed_args.notify_password is not None:
            body['notify_password'] = parsed_args.notify_password
        if parsed_args.password is not None:
            body['password'] = str(parsed_args.password)

        user = sss_client.create_user(body)
        columns = utils.get_columns(user)
        obj = objectify(user)
        data = utils.get_item_properties(obj, columns)
        return columns, data


class DeleteUser(command.Command):
    def get_parser(self, prog_name):
        parser = super(DeleteUser, self).get_parser(prog_name)
        parser.add_argument(
            'user_id',
            metavar="<uuid>",
            nargs="+",
            help=("Delete target users user id.")
        )
        return parser

    def take_action(self, parsed_args):
        sss_client = self.app.client_manager.sss

        for user_id in parsed_args.user_id:
            sss_client.delete_user(user_id)
