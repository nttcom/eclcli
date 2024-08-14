# -*- coding: utf-8 -*-

from eclcli.common import command
from eclcli.common import utils
from eclcli.i18n import _  # noqa
from ..sssclient.common.utils import objectify


class ListTenant(command.Lister):
    _description = _("List tenants")
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
            'workspace_id',
        )
        column_headers = (
            'ID',
            'Tenant Name',
            'Description',
            'Region',
            'Start Time',
            'Workspace ID',
        )

        data = [objectify(tenant)
                for tenant in sss_client.list_tenants().get('tenants')]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowTenant(command.ShowOne):
    _description = _("Show tenant")
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
    _description = _("Create new tenant")
    def get_parser(self, prog_name):
        parser = super(CreateTenant, self).get_parser(prog_name)
        parser.add_argument(
            'workspace_id',
            metavar='<workspace_id>',
            help='The workspace ID where the tenant will be created.'
        )
        parser.add_argument(
            'region',
            metavar='<region>',
            help='Region this tenant belongs to. \'jp1\' is available as of now.',
        )
        return parser

    def take_action(self, parsed_args):
        sss_client = self.app.client_manager.sss

        body = {}
        if parsed_args.region is not None:
            body['workspace_id'] = str(parsed_args.workspace_id)
        if parsed_args.region is not None:
            body['region'] = str(parsed_args.region)

        tenant = sss_client.create_tenant(body)
        columns = utils.get_columns(tenant)
        obj = objectify(tenant)
        data = utils.get_item_properties(obj, columns)
        return columns, data
