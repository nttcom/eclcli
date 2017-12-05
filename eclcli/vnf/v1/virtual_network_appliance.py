# -*- coding: utf-8 -*-

import copy
import six
from eclcli.common import command
from eclcli.common import utils
from eclcli.i18n import _  # noqa


class ListVirtualNetworkAppliance(command.Lister):

    def get_parser(self, prog_name):
        parser = super(ListVirtualNetworkAppliance, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.virtual_network_appliance

        columns = [
            'ID',
            'Name',
            'Appliance Type',
            'OS Monitoring Status',
            'OS Login Status',
            'VM Status',
        ]
        column_headers = copy.deepcopy(columns)

        data = client.virtual_network_appliances()

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={'Metadata': utils.format_dict},
                ) for s in data))


class ShowVirtualNetworkAppliance(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(ShowVirtualNetworkAppliance, self).get_parser(prog_name)
        parser.add_argument(
            'virtual_network_appliance_id',
            metavar='<string>',
            help='ID of virtual network appliance id to look up.')
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.virtual_network_appliance

        rows = [
            'ID',
            'Name',
            'Appliance Type',
            'OS Monitoring Status',
            'OS Login Status',
            'VM Status',
            'Interfaces'
        ]
        row_headers = rows

        # TODO format interface dictionary by using kind of formetter function
        data = client.get_virtual_network_appliance(
            parsed_args.virtual_network_appliance_id)
        return (row_headers, (utils.get_item_properties(data, rows)))


class CreateVirtualNetworkAppliance(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(CreateVirtualNetworkAppliance, self).\
            get_parser(prog_name)
        parser.add_argument(
            'virtual_network_appliance_plan_id',
            metavar='<virtual-network-appliance-id>',
            help='ID of virtual network appliance plan')

        parser.add_argument(
            '--interface',
            metavar="<net-id=net-uuid,fixed-ip=ip-addr,name=interface-name>,",
            action='append',
            default=[],
            help=_("Specify interface parameter for VNF. "
                   "You can specify only one interface in creation of "
                   "virtual network appliance. "
                   "net-id: attach interface to network with this UUID, "
                   "fixed-ip: IPv4 fixed address for NIC, "
                   "name: Name of Interface (optional)."),
        )

        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Name of virtual network appliance'),
        )

        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description of virtual network appliance'),
        )

        parser.add_argument(
            '--default-gateway',
            metavar='<default-gateway>',
            help=_('Default gateway of virtual network appliance'),
        )

        parser.add_argument(
            '--availability-zone',
            metavar='<availability-zone>',
            help=_('Availability zone that virtual network appliance '
                   'will be created'),
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.virtual_network_appliance

        rows = [
            'ID',
            'Name',
            'Appliance Type',
            'OS Monitoring Status',
            'OS Login Status',
            'VM Status',
        ]
        row_headers = rows

        if len(parsed_args.interface) == 0:
            msg = _("You can specify at least one interface.")
            raise exceptions.CommandError(msg)

        if len(parsed_args.interface) > 1:
            msg = _("You can specify only one interface in virtual network "
                    "appliance creation.")
            raise exceptions.CommandError(msg)

        interfaces = []
        for if_str in parsed_args.interface:
            if_info = {"net-id": "", "fixed-ip": "",
                       "name": ""}
            if_info.update(dict(kv_str.split("=", 1)
                           for kv_str in if_str.split(",")))
            if not bool(if_info["net-id"]) or not bool(if_info["fixed-ip"]):
                msg = _("You must specify network uuid and ip address both")
                raise exceptions.CommandError(msg)

            interfaces.append(if_info)

        interfaces_arg = _define_interface(parsed_args.interface)

        plan_id = \
            parsed_args.virtual_network_appliance_plan_id

        name = parsed_args.name
        description = parsed_args.description
        default_gateway = parsed_args.default_gateway
        zone = parsed_args.availability_zone

        data = client.create_virtual_network_appliance(
            virtual_network_appliance_plan_id=plan_id,
            interfaces=interfaces_arg,
            name=name,
            description=description,
            default_gateway=default_gateway,
            availability_zone=zone,
        )

        return (row_headers, utils.get_item_properties(data, rows))


def _define_interface(arg_interface):
    interfaces = []
    for if_str in arg_interface:
        if_info = {"net-id": "", "fixed-ip": "",
                   "name": ""}
        if_info.update(dict(kv_str.split("=", 1)
                            for kv_str in if_str.split(",")))
        if not bool(if_info["net-id"]) or not bool(if_info["fixed-ip"]):
            msg = _("You must specify network uuid and ip address both")
            raise exceptions.CommandError(msg)

        interfaces.append(if_info)

    interface_object = {}
    if_num = 1
    for interface in interfaces:

        if_key = 'interface_' + str(if_num)
        tmp = {
            if_key: {
                'network_id': interface['net-id'],
                'fixed_ips': [
                    {'ip_address': interface['fixed-ip']}
                ]
            }
        }
        if interface['name']:
            tmp[if_key].update({'name': interface['name']})

        interface_object.update(tmp)
        if_num += 1

    return interface_object


class DeleteVirtualNetworkAppliance(command.Command):

    def get_parser(self, prog_name):
        parser = super(DeleteVirtualNetworkAppliance, self).\
            get_parser(prog_name)
        parser.add_argument(
            "virtual_network_appliance_id",
            nargs="+",
            help="IDs of virtual network appliance to be deleted",
            metavar='<virtual-network-appliance-id>'
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.virtual_network_appliance
        for virtual_network_appliance_id in \
                parsed_args.virtual_network_appliance_id:
            client.delete_virtual_network_appliance(
                virtual_network_appliance_id)


# class UpdateSnapshot(command.ShowOne):
#
#     def get_parser(self, prog_name):
#         parser = super(UpdateSnapshot, self).get_parser(prog_name)
#         parser.add_argument(
#             'snapshot_id',
#             metavar='<string>',
#             help='ID of snapshot')
#         parser.add_argument(
#             "--name",
#             help="Name of snapshot",
#             metavar='<string>'
#         )
#         parser.add_argument(
#             "--description",
#             help="Description of snapshot",
#             metavar='<string>'
#         )
#         return parser
#
#     def take_action(self, parsed_args):
#         client = self.app.eclsdk.conn.storage
#
#         rows = [
#             'ID',
#             'Name',
#             'Status',
#             'Description',
#             'Usage',
#             'Volume ID',
#             'Snapshot Type ID',
#             'Created At',
#             'Updated At',
#             'Deleted At',
#             'Error Message',
#             'Delete Reason',
#         ]
#         row_headers = rows
#
#         body = {}
#         if parsed_args.name:
#             body["name"] = parsed_args.name
#         if parsed_args.description:
#             body["description"] = parsed_args.description
#         data = client.update_snapshot(parsed_args.snapshot_id, **body)
#
#         return (row_headers, utils.get_item_properties(data, rows))
#
#
#
#
# class RestoreSnapshot(command.Command):
#
#     def get_parser(self, prog_name):
#         parser = super(RestoreSnapshot, self).get_parser(prog_name)
#         parser.add_argument(
#             'snapshot_id',
#             metavar='<string>',
#             help='ID of snapshot')
#         return parser
#
#     def take_action(self, parsed_args):
#         client = self.app.eclsdk.conn.storage
#         client.restore_snapshot(parsed_args.snapshot_id)
