# -*- coding: utf-8 -*-

import copy
import six
from eclcli.common import command
from eclcli.common import utils
from eclcli.i18n import _  # noqa


class ListTenantConnecion(command.Lister):
    _description = _("List tenant-connections")

    def get_parser(self, prog_name):
        parser = super(ListTenantConnecion,
                       self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.provider_connectivity

        columns = [
            'ID',
            'Tenant Connection Request ID',
            'Name',
            'Name Other',
            'Tenant ID',
            'Tenant ID Other',
            'Network ID',
            'Status',
          ]
        column_headers = copy.deepcopy(columns)

        data = client.tenant_connections()

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowTenantConnection(command.ShowOne):
    _description = _("Show tenant-connection")
    """Display details"""

    def get_parser(self, prog_name):
        parser = super(ShowTenantConnection,
                       self).get_parser(prog_name)
        parser.add_argument(
            'tenant_connection_id',
            metavar='<TENANT CONNECTION ID>',
            help='ID of tenant connection to display',
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.provider_connectivity

        data = client.get_tenant_connection(
                    parsed_args.tenant_connection_id)._body

        if 'tags' in data:
            data['tags'] = utils.format_dict(data.pop('tags'))
        if 'tags_other' in data:
            data['tags_other'] = utils.format_dict(data.pop('tags_other'))

        return zip(*sorted(six.iteritems(data)))


class CreateTenantConnection(command.ShowOne):
    _description = _("Create new tenant-connection")

    def get_parser(self, prog_name):
        parser = super(CreateTenantConnection,
                       self).get_parser(prog_name)

        parser.add_argument(
            '--tenant-connection-request-id',
            metavar='<TENANT CONNECTION REQUEST ID>',
            help='Tenant connection request ID of tenant connection to create',
            required=True,
        )

        parser.add_argument(
            '--device-type',
            metavar='<DEVICE TYPE>',
            help='Device type of tenant connection to create',
            required=True,
        )

        parser.add_argument(
            '--device-id',
            metavar='<Device ID>',
            help='Device ID of tenant connection to create',
            required=True,
        )

        parser.add_argument(
            '--device-interface-id',
            metavar='<Device Interface ID>',
            help='Device interface ID of tenant connection to create',
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
            '--segmentation-type',
            metavar='<Segmentation type>',
            help='Segmentation type of tenant connection to create',
        )

        parser.add_argument(
            '--segmentation-id',
            metavar='<Segmentation ID>',
            help='Segmentation ID of tenant connection to create',
        )

        parser.add_argument(
            '--fixed-ip',
            action='append',
            type=utils.parse_fixed_ips,
            metavar='<subnet_id,ipv4>|<ipv4>',
            help="Fixed ip address of tenant connection to create. "
                 "subnet_id,ipv4 or ipv4 format. "
                 "You can repeat this option."
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.provider_connectivity

        body = {
            'tenant_connection_request_id':
                parsed_args.tenant_connection_request_id,
            'device_type': parsed_args.device_type,
            'device_id': parsed_args.device_id,
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
        if parsed_args.device_interface_id:
            body['device_interface_id'] = parsed_args.device_interface_id

        attachment_opts = dict()
        if parsed_args.segmentation_type:
            attachment_opts['segmentation_type'] = \
                parsed_args.segmentation_type
        if parsed_args.segmentation_id:
            attachment_opts['segmentation_id'] = parsed_args.segmentation_id
        if parsed_args.fixed_ip:
            attachment_opts['fixed_ips'] = parsed_args.fixed_ip

        if len(attachment_opts.keys()) > 0:
            body['attachment_opts'] = attachment_opts

        data = client.create_tenant_connection(**body)._body

        if 'tags' in data:
            data['tags'] = utils.format_dict(data.pop('tags'))
        if 'tags_other' in data:
            data['tags_other'] = utils.format_dict(data.pop('tags_other'))

        return zip(*sorted(six.iteritems(data)))


class UpdateTenantConnection(command.ShowOne):
    _description = _("Update tenant-connection")

    def get_parser(self, prog_name):
        parser = super(UpdateTenantConnection,
                       self).get_parser(prog_name)

        parser.add_argument(
            'tenant_connection_id',
            metavar='<TENANT CONNECTION ID>',
            help='ID of tenant connection to update',
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
            'tenant_connection':
                parsed_args.tenant_connection_id,
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

        data = client.update_tenant_connection(**body)._body

        if 'tags' in data:
            data['tags'] = utils.format_dict(data.pop('tags'))
        if 'tags_other' in data:
            data['tags_other'] = utils.format_dict(data.pop('tags_other'))

        return zip(*sorted(six.iteritems(data)))


class DeleteTenantConnection(command.Command):
    _description = _("Delete tenant-connection")
    """Delete"""

    def get_parser(self, prog_name):
        parser = super(DeleteTenantConnection,
                       self).get_parser(prog_name)
        parser.add_argument(
            'tenant_connection_id',
            metavar='<TENANT CONNECTION REQUEST ID>',
            help='ID of tenant connection request to display',
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.provider_connectivity

        client.delete_tenant_connection(
                parsed_args.tenant_connection_id)
