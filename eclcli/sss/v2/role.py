# -*- coding: utf-8 -*-

from eclcli.common import command
from eclcli.common import exceptions
from eclcli.common import utils
from eclcli.identity import common as identity_common
from ..sssclient.common.utils import objectify


class CreateRole(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(CreateRole, self).get_parser(prog_name)
        parser.add_argument(
          'tenant_id',
          metavar='<tenant_id>',
          help='Tenant which the user have role.',
        )
        parser.add_argument(
          'user_id',
          metavar='<user_id>',
          help='User which have new role.',
        )
        return parser

    def take_action(self, parsed_args):
        sss_client = self.app.client_manager.sss
        body = {}
        if parsed_args.user_id is not None:
            body['user_id'] = str(parsed_args.user_id)
        if parsed_args.tenant_id is not None:
            body['tenant_id'] = str(parsed_args.tenant_id)

        role = sss_client.create_role(body)
        columns = utils.get_columns(role)
        obj = objectify(role)
        data = utils.get_item_properties(obj, columns)
        return columns, data


class DeleteRole(command.Command):
    def get_parser(self, prog_name):
        parser = super(DeleteRole, self).get_parser(prog_name)
        parser.add_argument(
          'tenant_id',
          metavar='<tenant_id>',
          help='Delete target tenant\'s tenant id.',
        )
        parser.add_argument(
          'user_id',
          metavar='<user_id>',
          help='User\'s id of the role.',
        )
        return parser

    def take_action(self, parsed_args):
        sss_client = self.app.client_manager.sss
        tenant_id  = parsed_args.tenant_id
        user_id    = parsed_args.user_id
        sss_client.delete_role(tenant_id, user_id)

