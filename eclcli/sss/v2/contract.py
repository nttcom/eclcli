# -*- coding: utf-8 -*-

try:
    import json
except ImportError:
    import simplejson as json
from eclcli.common import command, utils
from eclcli.i18n import _  # noqa
from ..sssclient.common.utils import objectify


class ListContract(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListContract, self).get_parser(prog_name)
        parser.add_argument(
            'channel_id',
            metavar="<uuid>",
            help="Target channel_id under own contract."
        )
        parser.add_argument(
            '--include_deleted',
            metavar="<boolean>",
            type=utils.parse_bool,
            choices=[True, False],
            help="default is false. (true : Include deleted contract "
                 "/ false: exclude deleted contract."
        )
        return parser

    def take_action(self, parsed_args):
        sss_client = self.app.client_manager.sss

        columns = (
        )
        column_headers = (
        )

        channel_id = parsed_args.channel_id
        data = [
            objectify(contract) for contract
            in sss_client.list_contracts(channel_id).get('contracts')
        ]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowContract(command.ShowOne):
    _description = _("Show contract")
    def get_parser(self, prog_name):
        parser = super(ShowContract, self).get_parser(prog_name)
        parser.add_argument(
            'contract_id',
            metavar="<uuid>",
            help="The contract ID getting more information"
        )
        return parser

    def take_action(self, parsed_args):
        sss_client = self.app.client_manager.sss
        contract_id = parsed_args.contract_id
        contract = sss_client.show_contract(contract_id)
        columns = utils.get_columns(contract)
        obj = objectify(contract)
        data = utils.get_item_properties(obj, columns)
        return columns, data


class CreateContract(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(CreateContract, self).get_parser(prog_name)
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
            'channel_id',
            metavar='<uuid>',
            help=('The channel means the group to manage contracts.',
                  'The partner user will be given 2 channels.',
                  'One is the channel that contains own contract.',
                  'The other is the channel that contains all end user'
                  ' contracts which the partner user has.',
                  'By executing the List Channel API(For partner user only), '
                  'the user can get your (and enduser\'s) channel ID.')
        )
        parser.add_argument(
            '--notify_password',
            metavar='<boolean>',
            type=utils.parse_bool,
            choices=[True, False],
            help='If this flag is set \'true\', notification email will be '
                 'sent to new user\'s email.'
        )
        parser.add_argument(
            '--external_reference_id',
            metavar='<uuid>',
            help=('By using this item, the partner API user can associate '
                  'optional string to the constract(e.g. The end user management '
                  'ID in the partner user\'s system).',
                  'Note that this ID will be NOT used to control the contract '
                  'in ECL2.0 internal system.',
                  'If the item is set as blank, ECL 2.0 system set the end user\'s'
                  ' contract ID automatically(e.g. econXXXXXXXX).')
        )
        parser.add_argument(
            '--password',
            metavar='<password>',
            help=('Initial password of new user.',
                  'If this parameter is not designated, random initial password is '
                  'generated and applied to new user.')
        )
        return parser

    def take_action(self, parsed_args):
        sss_client = self.app.client_manager.sss

        body = {}
        if parsed_args.login_id is not None:
            body['login_id'] = str(parsed_args.login_id)
        if parsed_args.mail_address is not None:
            body['mail_address'] = str(parsed_args.mail_address)
        if parsed_args.channel_id is not None:
            body['channel_id'] = str(parsed_args.channel_id)
        if parsed_args.notify_password is not None:
            body['notify_password'] = parsed_args.notify_password
        if parsed_args.password is not None:
            body['password'] = str(parsed_args.password)
        if parsed_args.external_reference_id is not None:
            body['external_reference_id'] = str(parsed_args.external_reference_id)

        contract = sss_client.create_contract(body)
        columns = utils.get_columns(contract)
        obj = objectify(contract)
        data = utils.get_item_properties(obj, columns)
        return columns, data


class DeleteContract(command.Command):
    def get_parser(self, prog_name):
        parser = super(DeleteContract, self).get_parser(prog_name)
        parser.add_argument(
            'contract_id',
            metavar="<uuid>",
            nargs="+",
            help="Contract ID of Delete target"
        )
        return parser

    def take_action(self, parsed_args):
        sss_client = self.app.client_manager.sss

        for contract_id in parsed_args.contract_id:
            sss_client.delete_contract(contract_id)
