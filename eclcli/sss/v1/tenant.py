# -*- coding: utf-8 -*-

from eclcli.common import command
from eclcli.common import exceptions
from eclcli.common import utils
from eclcli.identity import common as identity_common
from ..sssclient.common.utils import objectify


class ListTenant(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListTenant, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        sss_client = self.app.client_manager.sss

        columns = (
            'tenant_id',
            'tenant_name',
            'description',
            'region',
            'start_time',
        )
        column_headers = (
            'ID',
            'Tenant Name',
            'Description',
            'Region',
            'Start Time',
        )

        data = [objectify(tenant)
                for tenant in sss_client.list_tenants().get('tenants')]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowTenant(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(ShowTenant, self).get_parser(prog_name)
        parser.add_argument(
            'tenant_id',
            metavar="<uuid>",
            help="ID of tenant to show."
        )
        return parser

    def take_action(self, parsed_args):
        sss_client = self.app.client_manager.sss
        tenant_id = parsed_args.tenant_id
        tenant = sss_client.show_tenant(tenant_id)
        columns = utils.get_columns(tenant)
        obj = objectify(tenant)
        data = utils.get_item_properties(obj, columns)
        return columns, data


class CreateTenant(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(CreateTenant, self).get_parser(prog_name)
        parser.add_argument(
            'tenant_name',
            metavar='<tenant_name>',
            help="New tenant\'s tenant name. This name need to be unique globally."
        )
        parser.add_argument(
            'description',
            metavar='<description>',
            help='Description for this tenant.'
        )
        parser.add_argument(
            'region',
            metavar='<region>',
            help='Region this tenant belongs to. \'jp1\' is available as of now.',
        )
        parser.add_argument(
            '--contract_id',
            metavar='<contract_id>',
            help='Contract which new tenant belongs to. If this parameter is not'
                 ' designated, API user\'s contract implicitly designated.'
        )
        return parser

    def take_action(self, parsed_args):
        sss_client = self.app.client_manager.sss

        body = {}
        if parsed_args.tenant_name is not None:
            body['tenant_name'] = str(parsed_args.tenant_name)
        if parsed_args.description is not None:
            body['description'] = str(parsed_args.description)
        if parsed_args.region is not None:
            body['region'] = str(parsed_args.region)
        if parsed_args.contract_id is not None:
            body['contract_id'] = str(parsed_args.contract_id)

        tenant = sss_client.create_tenant(body)
        columns = utils.get_columns(tenant)
        obj = objectify(tenant)
        data = utils.get_item_properties(obj, columns)
        return columns, data


class DeleteTenant(command.Command):
    def get_parser(self, prog_name):
        parser = super(DeleteTenant, self).get_parser(prog_name)
        parser.add_argument(
            'tenant_id',
            metavar="<uuid>",
            nargs="+",
            help="Delete target tenant\'s tenant id."
        )
        return parser

    def take_action(self, parsed_args):
        sss_client = self.app.client_manager.sss

        for tenant_id in parsed_args.tenant_id:
            sss_client.delete_tenant(tenant_id)
