# -*- coding: utf-8 -*-

import json
import json_merge_patch as jmp
import copy
import six
from eclcli.common import command
from eclcli.common import exceptions
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
            'Description',
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
            'Description',
            'Appliance Type',
            'OS Monitoring Status',
            'OS Login Status',
            'VM Status',
            'Interfaces'
        ]
        row_headers = rows

        data = client.get_virtual_network_appliance(
            parsed_args.virtual_network_appliance_id)

        _set_interfaces_for_display(data)

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
            metavar="<net-id=net-uuid,ip-address=ip-addr,name=interface-name>",
            action='append',
            default=[],
            help=_("Specify interface parameter for "
                   "virtual network appliance. "
                   "You can specify only one interface in creation of "
                   "virtual network appliance. "
                   "net-id: attach interface to network with this UUID, "
                   "ip-address: IPv4 fixed address for interface. "
                   "(You can specify only one address in creation), "
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
            'Description',
            'Appliance Type',
            'OS Monitoring Status',
            'OS Login Status',
            'VM Status',
        ]
        row_headers = rows

        if len(parsed_args.interface) == 0:
            msg = _("You must specify at least one interface.")
            raise exceptions.CommandError(msg)

        if len(parsed_args.interface) > 1:
            msg = _("You can specify only one interface in virtual network "
                    "appliance creation.")
            raise exceptions.CommandError(msg)

        interfaces = []
        for if_str in parsed_args.interface:
            if_info = {"net-id": "", "ip-address": "",
                       "name": ""}
            if_info.update(dict(kv_str.split("=", 1)
                           for kv_str in if_str.split(",")))
            if not bool(if_info["net-id"]) or not bool(if_info["ip-address"]):
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
                        {'ip_address': interface['ip-address']}
                    ]
                }
            }
            if interface['name']:
                tmp[if_key].update({'name': interface['name']})

            interface_object.update(tmp)
            if_num += 1

        plan_id = \
            parsed_args.virtual_network_appliance_plan_id

        name = parsed_args.name
        description = parsed_args.description
        default_gateway = parsed_args.default_gateway
        zone = parsed_args.availability_zone

        data = client.create_virtual_network_appliance(
            virtual_network_appliance_plan_id=plan_id,
            interfaces=interface_object,
            name=name,
            description=description,
            default_gateway=default_gateway,
            availability_zone=zone,
        )

        return (row_headers, utils.get_item_properties(data, rows))


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


class UpdateVirtualNetworkApplianceMetaData(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(UpdateVirtualNetworkApplianceMetaData, self).\
            get_parser(prog_name)
        parser.add_argument(
            'virtual_network_appliance',
            metavar='<virtual-network-appliance name or id>',
            help='Name or ID of virtual network appliance')
        parser.add_argument(
            "--name",
            help="Name of virtual network appliance",
            metavar='<string>'
        )
        parser.add_argument(
            "--description",
            help="Description of virtual network appliance",
            metavar='<string>'
        )

        return parser

    def take_action(self, parsed_args):
        vnf_client = self.app.eclsdk.conn.virtual_network_appliance

        target = vnf_client.\
            get_virtual_network_appliance(
            parsed_args.virtual_network_appliance)

        rows = [
            'ID',
            'Name',
            'Description',
            'Appliance Type',
            'OS Monitoring Status',
            'OS Login Status',
            'VM Status',
            'Interfaces'
        ]
        row_headers = rows

        # serialize request parmeter as JSON
        requested_param = {}
        if parsed_args.name:
            requested_param["name"] = parsed_args.name
        if parsed_args.description:
            requested_param["description"] = parsed_args.description

        # serialize current parmeter as JSON
        current_param = {
            'name': target.name,
            'description': target.description,
        }

        patch = jmp.create_patch(current_param, requested_param)

        if not patch:
            msg = _('No change will be expected')
            raise exceptions.CommandError(msg)

        data = vnf_client.update_virtual_network_appliance(
            parsed_args.virtual_network_appliance, **patch)

        _set_interfaces_for_display(data)

        return (row_headers, utils.get_item_properties(data, rows))


class UpdateVirtualNetworkApplianceInterfaces(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(UpdateVirtualNetworkApplianceInterfaces, self).\
            get_parser(prog_name)
        parser.add_argument(
            'virtual_network_appliance',
            metavar='<virtual-network-appliance name or id>',
            help='Name or ID of virtual network appliance')

        parser.add_argument(
            '--interface',
            metavar="<slot-no=number,net-id=net-uuid,"
                    "fixed-ips=ip-addr1:ip-addr2...,name=interface-name>",
            action='append',
            default=[],
            help=_("Specify interface parameter "
                   "for virtual network appliance. "
                   "slot-no: sequential number of interface,"
                   "net-id: attach interface to network with this UUID, "
                   "fixed-ips: IPv4 fixed address for NIC. "
                   "You can specif multiple ip address by using ':' "
                   "(e.g: 1.1.1.1:2.2.2.2:...) , "
                   "name: Name of Interface."),
        )

        return parser

    def take_action(self, parsed_args):
        vnf_client = self.app.eclsdk.conn.virtual_network_appliance

        target = vnf_client.\
            get_virtual_network_appliance(
            parsed_args.virtual_network_appliance)

        rows = [
            'ID',
            'Name',
            'Description',
            'Appliance Type',
            'OS Monitoring Status',
            'OS Login Status',
            'VM Status',
            'Interfaces'
        ]
        row_headers = rows

        interfaces = []
        VALID_KEYS = ['slot-no', 'net-id', 'fixed-ips', 'name']
        for if_str in parsed_args.interface:
            # if_info = {"net-id": "", "fixed-ips": "",
            #            "name": "", "slot-no": ""}
            if_info = {}
            if_info.update(dict(kv_str.split("=", 1)
                           for kv_str in if_str.split(",")))

            for k in if_info.keys():
                if k not in VALID_KEYS:
                    msg = 'Invalid key %s is specified.' % k
                    raise exceptions.CommandError(msg)

            interfaces.append(if_info)

        requested_interface_object = {}
        for interface in interfaces:
            slot_no = interface.get('slot-no')
            if_key = 'interface_' + str(slot_no)

            network_id = interface.get('net-id')
            name = interface.get('name')
            fixed_ips_tmp = interface.get('fixed-ips')

            each_if_info = {}

            if name:
                each_if_info.update({'name': name})

            if network_id:
                each_if_info.update({'network_id': network_id})

            if fixed_ips_tmp:
                fixed_ips = [ip for ip in fixed_ips_tmp.split(':')]
                each_if_info.update({'fixed_ips': fixed_ips})

            interface_tmp = {
                if_key: each_if_info
            }
            requested_interface_object.update(interface_tmp)

        current_interface_object = copy.deepcopy(target.interfaces)
        merged_interface_object = jmp.merge(current_interface_object,
                                            requested_interface_object)
        patch = jmp.create_patch(target.interfaces,
                                 merged_interface_object)

        patch = {'interfaces': patch}
        if not patch:
            msg = _('No change will be expected')
            raise exceptions.CommandError(msg)

        data = vnf_client.update_virtual_network_appliance(
            parsed_args.virtual_network_appliance, **patch)

        _set_interfaces_for_display(data)

        return (row_headers, utils.get_item_properties(data, rows))


class UpdateVirtualNetworkApplianceAAPs(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(UpdateVirtualNetworkApplianceAAPs, self).\
            get_parser(prog_name)
        parser.add_argument(
            'virtual_network_appliance',
            metavar='<virtual-network-appliance name or id>',
            help='Name or ID of virtual network appliance')

        parser.add_argument(
            '--allowed-address-pair',
            metavar="<interface-slot-no=number,ip-address=ip-addr,"
                    "mac-address=mac-addr,type=type,vrid=vrid>",
            action='append',
            default=[],
            help=_("Specify Allowed Address Pair(A.A.P) parameter for "
                   "virtual network appliance. "
                   "slot-no: sequential number of interface,"
                   "ip-address: IP address of A.A.P, "
                   "mac-address: MAC address of A.A.P, "
                   "type: Type of A.A.P. You can use 'vrrp' or '', "
                   "vrid: VRID of A.A.P. You can use this only in case vrrp, "
                   "You can specify same slot number multiple times."
                   "(e.g: --allowed-address-pair slot-no=1,ip-address=1.1.1.1 "
                   "--allowed-address-pair slot-no=1,ipaddress=2.2.2.2 ...) , "
                   "In this case, all values relates to slot-no=1 "
                   "will be appended as interface_1.allowed_address_pairs "
                   "list."),
        )

        return parser

    def take_action(self, parsed_args):
        vnf_client = self.app.eclsdk.conn.virtual_network_appliance

        target = vnf_client.\
            get_virtual_network_appliance(
            parsed_args.virtual_network_appliance)

        rows = [
            'ID',
            'Name',
            'Description',
            'Appliance Type',
            'OS Monitoring Status',
            'OS Login Status',
            'VM Status',
            'Interfaces'
        ]
        row_headers = rows

        aaps = []
        VALID_KEYS = ['interface-slot-no', 'ip-address', 'mac-address', 'type', 'vrid']
        for aap_str in parsed_args.allowed_address_pair:
            aap_info = {}
            aap_info.update(dict(aap_str.split("=", 1)
                           for aap_str in aap_str.split(",")))

            for k in aap_info.keys():
                if k not in VALID_KEYS:
                    msg = 'Invalid key %s is specified.' % k
                    raise exceptions.CommandError(msg)

            aaps.append(aap_info)

        requested_aap_object = {}
        for aap in aaps:
            slot_no = aap.get('interface-slot-no', None)
            if not slot_no:
                msg = 'No interface number is specified.'
                raise exceptions.CommandError(msg)

            # create key <-> value if not exist.
            if_key = 'interface_' + str(slot_no)
            requested_aap_object.setdefault(if_key, {'allowed_address_pairs': []})

            ip_address = aap.get('ip-address')
            mac_address = aap.get('mac-address')
            aap_type = aap.get('type')
            vrid = aap.get('vrid')

            each_aap_info = {}

            if ip_address:
                each_aap_info.update({'ip_address': ip_address})

            if mac_address:
                each_aap_info.update({'mac_address': mac_address})

            if aap_type:
                each_aap_info.update({'type': aap_type})

            if vrid:
                each_aap_info.update({'vrid': vrid})

            requested_aap_object[if_key]['allowed_address_pairs'].\
                append(each_aap_info)

        current_interface_object = copy.deepcopy(target.interfaces)
        merged_interface_object = jmp.merge(current_interface_object,
                                            requested_aap_object)
        patch = jmp.create_patch(target.interfaces,
                                 merged_interface_object)

        patch = {'interfaces': patch}
        if not patch:
            msg = _('No change will be expected')
            raise exceptions.CommandError(msg)

        data = vnf_client.update_virtual_network_appliance(
            parsed_args.virtual_network_appliance, **patch)

        _set_interfaces_for_display(data)

        return (row_headers, utils.get_item_properties(data, rows))


class StartVirtualNetworkAppliance(command.Command):

    def get_parser(self, prog_name):
        parser = super(StartVirtualNetworkAppliance, self).\
            get_parser(prog_name)
        parser.add_argument(
            'virtual_network_appliance',
            metavar='<virtual-network-appliance>',
            nargs="+",
            help=_('Virtual Network Appliance(s) to start (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        vnf_client = self.app.eclsdk.conn.virtual_network_appliance

        for virtual_network_appliance in parsed_args.virtual_network_appliance:
            vnf_client.\
                start_virtual_network_appliance(virtual_network_appliance)


class StopVirtualNetworkAppliance(command.Command):

    def get_parser(self, prog_name):
        parser = super(StopVirtualNetworkAppliance, self).\
            get_parser(prog_name)
        parser.add_argument(
            'virtual_network_appliance',
            metavar='<virtual-network-appliance>',
            nargs="+",
            help=_('Virtual Network Appliance(s) to stop (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        vnf_client = self.app.eclsdk.conn.virtual_network_appliance

        for virtual_network_appliance in parsed_args.virtual_network_appliance:
            vnf_client.\
                stop_virtual_network_appliance(virtual_network_appliance)


class RestartVirtualNetworkAppliance(command.Command):

    def get_parser(self, prog_name):
        parser = super(RestartVirtualNetworkAppliance, self).\
            get_parser(prog_name)
        parser.add_argument(
            'virtual_network_appliance',
            metavar='<virtual-network-appliance>',
            nargs="+",
            help=_('Virtual Network Appliance(s) to restart (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        vnf_client = self.app.eclsdk.conn.virtual_network_appliance

        for virtual_network_appliance in parsed_args.virtual_network_appliance:
            vnf_client.\
                restart_virtual_network_appliance(virtual_network_appliance)


def _set_interfaces_for_display(data):
    ifs = data.interfaces
    interfaces_json = json.dumps(ifs, indent=2)
    setattr(data, 'interfaces', interfaces_json)
