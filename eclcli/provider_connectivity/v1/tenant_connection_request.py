# -*- coding: utf-8 -*-

import copy
import six
from eclcli.common import command
from eclcli.common import utils


class ListTenantConnecionRequest(command.Lister):

    def get_parser(self, prog_name):
        parser = super(ListTenantConnecionRequest,
                       self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.provider_connectivity

        columns = [
            'ID',
            'Name',
            'Name Other',
            'Tenant ID',
            'Network ID',
            'Status',
          ]
        column_headers = copy.deepcopy(columns)

        data = client.tenant_connection_requests()

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowTenantConnectionRequest(command.ShowOne):
    """Display details"""

    def get_parser(self, prog_name):
        parser = super(ShowTenantConnectionRequest,
                       self).get_parser(prog_name)
        parser.add_argument(
            'tenant_connection_request_id',
            metavar='<TENANT CONNECTION REQUEST ID>',
            help='ID of tenant connection request to display',
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.provider_connectivity

        data = client.get_tenant_connection_request(
                    parsed_args.tenant_connection_request_id)._body

        if 'tags' in data:
            data['tags'] = utils.format_dict(data.pop('tags'))
        if 'tags_other' in data:
            data['tags_other'] = utils.format_dict(data.pop('tags_other'))

        return zip(*sorted(six.iteritems(data)))


class CreateTenantConnectionRequest(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(CreateTenantConnectionRequest,
                       self).get_parser(prog_name)

        parser.add_argument(
            '--keystone-user-id',
            metavar='<KEYSTONE USER ID>',
            help='Keystone user ID of tenant connection request',
            required=False,
        )

        parser.add_argument(
            '--network-id',
            metavar='<NETWORK ID>',
            help='Network ID of tenant connection request',
            required=True,
        )

        parser.add_argument(
            '--tenant-id',
            metavar='<TENANT ID>',
            help='Tenant ID of owner of tenant connection request',
            required=False,
        )

        parser.add_argument(
            '--tenant-id-other',
            metavar='<TENANT ID>',
            help='Tenant ID of owner of network to connect',
            required=True,
        )

        parser.add_argument(
            '--name',
            metavar='<string>',
            help='Name of tenant connection request')

        parser.add_argument(
            "--description",
            help="Description of tenant connection request",
            metavar='<string>'
        )

        parser.add_argument(
            '--tags',
            action='append',
            type=utils.parse_tags,
            metavar='<key=value>',
            help="Tags of tenant connection request to create. "
                 "You can repeat this option."
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.provider_connectivity

        body = {
            'keystone_user_id': parsed_args.keystone_user_id,
            'network_id': parsed_args.network_id,
            'tenant_id_other': parsed_args.tenant_id_other,
            'tenant_id': parsed_args.tenant_id,
        }
        if parsed_args.name:
            body['name'] = parsed_args.name
        if parsed_args.description:
            body['description'] = parsed_args.description
        if parsed_args.tags:
            tags = {}
            for tag in parsed_args.tags:
                tags.update(tag)
            body['tags'] = tags

        data = client.create_tenant_connection_request(**body)._body

        if 'tags' in data:
            data['tags'] = utils.format_dict(data.pop('tags'))
        if 'tags_other' in data:
            data['tags_other'] = utils.format_dict(data.pop('tags_other'))

        return zip(*sorted(six.iteritems(data)))


class UpdateTenantConnectionRequest(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(UpdateTenantConnectionRequest,
                       self).get_parser(prog_name)

        parser.add_argument(
            'tenant_connection_request_id',
            metavar='<TENANT CONNECTION REQUEST ID>',
            help='ID of tenant connection request to update',
        )

        parser.add_argument(
            '--name',
            metavar='<string>',
            help='Name of tenant connection request')

        parser.add_argument(
            "--description",
            help="Description of tenant connection request",
            metavar='<string>'
        )

        parser.add_argument(
            '--tags',
            action='append',
            type=utils.parse_tags,
            metavar='<key=value>',
            help="Tags of tenant connection request to create. "
                 "You can repeat this option."
        )
        parser.add_argument(
            '--name-other',
            metavar='<string>',
            help='Name given by owner of network.')

        parser.add_argument(
            "--description-other",
            help="Description given by owner of network",
            metavar='<string>'
        )

        parser.add_argument(
            '--tags-other',
            action='append',
            type=utils.parse_tags,
            metavar='<key=value>',
            help="Tags given by owner of network. "
                 "You can repeat this option."
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.provider_connectivity

        body = {
            'tenant_connection_request':
                parsed_args.tenant_connection_request_id,
        }
        if parsed_args.name:
            body['name'] = parsed_args.name
        if parsed_args.description:
            body['description'] = parsed_args.description
        if parsed_args.name_other:
            body['name_other'] = parsed_args.name_other
        if parsed_args.description_other:
            body['description_other'] = parsed_args.description_other
        if parsed_args.tags:
            tags = {}
            for tag in parsed_args.tags:
                tags.update(tag)
            body['tags'] = tags
        if parsed_args.tags_other:
            tags = {}
            for tag in parsed_args.tags_other:
                tags.update(tag)
            body['tags_other'] = tags

        data = client.update_tenant_connection_request(**body)._body

        if 'tags' in data:
            data['tags'] = utils.format_dict(data.pop('tags'))
        if 'tags_other' in data:
            data['tags_other'] = utils.format_dict(data.pop('tags_other'))

        return zip(*sorted(six.iteritems(data)))


class DeleteTenantConnectionRequest(command.Command):
    """Delete"""

    def get_parser(self, prog_name):
        parser = super(DeleteTenantConnectionRequest,
                       self).get_parser(prog_name)
        parser.add_argument(
            'tenant_connection_request_id',
            metavar='<TENANT CONNECTION REQUEST ID>',
            help='ID of tenant connection request to display',
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.provider_connectivity

        data = client.delete_tenant_connection_request(
                    parsed_args.tenant_connection_request_id)
