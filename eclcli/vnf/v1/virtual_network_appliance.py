# -*- coding: utf-8 -*-

try:
    import json
except ImportError:
    import simplejson as json
import json_merge_patch as jmp
import copy
import re
import six
from eclcli.common import command, exceptions, utils
from eclcli.i18n import _  # noqa

ROWS_FOR_SHOW = [
    'ID',
    'Name',
    'Description',
    'Tags',
    'Virtual Network Appliance Plan',
    'Appliance Type',
    'Availability Zone',
    'OS Monitoring Status',
    'OS Login Status',
    'VM Status',
    'Operation Status',
    'Interfaces',
]


UUID_PATTERN = '^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-' \
               '?[a-f0-9]{12}$'


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
            'Tags',
            'Virtual Network Appliance Plan',
            'Appliance Type',
            'Availability Zone',
            'OS Monitoring Status',
            'OS Login Status',
            'VM Status',
            'Operation Status',
        ]
        column_headers = copy.deepcopy(columns)

        data = client.virtual_network_appliances()
        plans = client.virtual_network_appliance_plans()
        for datum in data:
            for plan in plans:
                if datum.virtual_network_appliance_plan_id == plan.id:
                    setattr(datum, 'virtual_network_appliance_plan', plan.name)
                    break

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
            metavar='<virtual-network-appliance-id>',
            help='ID of virtual network appliance id to look up.')
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.virtual_network_appliance

        rows = ROWS_FOR_SHOW
        row_headers = rows

        data = client.get_virtual_network_appliance(
            parsed_args.virtual_network_appliance_id)

        # Set plan name
        plan = client.get_virtual_network_appliance_plan(
            data.virtual_network_appliance_plan_id)
        setattr(data, 'virtual_network_appliance_plan', plan.name)

        _set_interfaces_for_display(data)

        return row_headers, (utils.get_item_properties(data, rows))


class CreateVirtualNetworkAppliance(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(CreateVirtualNetworkAppliance, self). \
            get_parser(prog_name)
        parser.add_argument(
            'virtual_network_appliance_plan_id',
            metavar='<virtual-network-appliance-plan-id>',
            help='ID of virtual network appliance plan')

        parser.add_argument(
            '--interface',
            metavar="<net-id=net-uuid,ip-address=ip-addr,name=interface-name,"
                    "description=interface-description,tags=interface-tags>",
            action='append',
            default=[],
            help=_("Specify interface parameter for "
                   "virtual network appliance. "
                   "You can specify only one interface in creation of "
                   "virtual network appliance. "
                   "net-id: attach interface to network with this UUID, "
                   "ip-address: IPv4 fixed address for interface. "
                   "(You can specify only one address in creation), "
                   "name: Name of Interface (optional)."
                   "description: Description of the interface,"
                   "tags: Tags of the interface,"
                   "      (e.g. '{\"tag1\": 1,\"tag2\": \"a\"...}' )"),
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
            "--tags",
            help="Tags of virtual network appliance"
                 " (e.g. '{\"tag1\": 1,\"tag2\": \"a\"...}' )",
            metavar='<string>'
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
            'Tags',
            'Virtual Network Appliance Plan',
            'Appliance Type',
            'Default Gateway',
            'Availability Zone',
            'OS Monitoring Status',
            'OS Login Status',
            'VM Status',
            'Operation Status',
            'Username',
            'Password',
            'Interfaces',
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
        valid_keys = ['net-id', 'ip-address', 'name', 'description', 'tags']
        for if_str in parsed_args.interface:
            if_info = {}
            if_info.update(utils.parse_vna_interface(if_str, valid_keys))
            try:
                if not bool(if_info["net-id"]) or \
                        not bool(if_info["ip-address"]):
                    raise
            except Exception:
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
            if 'name' in interface:
                name = interface.get('name', '')
                tmp[if_key].update({'name': name})

            if 'description' in interface:
                description = interface.get('description', '')
                tmp[if_key].update({'description': description})

            if 'tags' in interface:
                interface_tags = interface.get('tags') or '{}'
                try:
                    obj = json.loads(interface_tags)
                except Exception:
                    msg = _("You must specify JSON object format")
                    raise exceptions.CommandError(msg)

                tmp[if_key].update({'tags': obj})

            interface_object.update(tmp)
            if_num += 1

        plan_id = \
            parsed_args.virtual_network_appliance_plan_id

        name = parsed_args.name
        description = parsed_args.description
        default_gateway = parsed_args.default_gateway
        zone = parsed_args.availability_zone
        tags = parsed_args.tags or '{}'
        try:
            tags = json.loads(tags)
        except Exception:
            msg = _("You must specify JSON object format")
            raise exceptions.CommandError(msg)

        data = client.create_virtual_network_appliance(
            virtual_network_appliance_plan_id=plan_id,
            interfaces=interface_object,
            name=name,
            description=description,
            default_gateway=default_gateway,
            availability_zone=zone,
            tags=tags,
        )

        # Set plan name
        plan = client.get_virtual_network_appliance_plan(
            data.virtual_network_appliance_plan_id)
        setattr(data, 'virtual_network_appliance_plan', plan.name)

        _set_interfaces_for_display(data)

        return row_headers, utils.get_item_properties(data, rows)


class DeleteVirtualNetworkAppliance(command.Command):

    def get_parser(self, prog_name):
        parser = super(DeleteVirtualNetworkAppliance, self). \
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
        parser = super(UpdateVirtualNetworkApplianceMetaData, self). \
            get_parser(prog_name)
        parser.add_argument(
            'virtual_network_appliance',
            metavar='<virtual-network-appliance-id>',
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
        parser.add_argument(
            "--tags",
            help="Tags of virtual network appliance"
                 " (e.g. '{\"tag1\": 1,\"tag2\": \"a\"...}' )",
            metavar='<string>'
        )

        return parser

    def take_action(self, parsed_args):
        vnf_client = self.app.eclsdk.conn.virtual_network_appliance

        target = vnf_client.get_virtual_network_appliance(
            parsed_args.virtual_network_appliance)

        rows = ROWS_FOR_SHOW
        row_headers = rows

        # serialize request parmeter as JSON
        requested_param = {}
        if hasattr(parsed_args, 'name') and parsed_args.name is not None:
            requested_param['name'] = parsed_args.name
        if hasattr(parsed_args, 'description') and \
                parsed_args.description is not None:
            requested_param['description'] = parsed_args.description
        if hasattr(parsed_args, 'tags') and parsed_args.tags is not None:
            tags = parsed_args.tags or '{}'
            try:
                requested_param['tags'] = json.loads(tags)
            except Exception:
                msg = _("You must specify JSON object format")
                raise exceptions.CommandError(msg)

        # serialize current parmeter as JSON
        current_param = {
            'name': target.name,
            'description': target.description,
            'tags': target.tags,
        }
        origin_param = copy.deepcopy(current_param)
        merged_param = jmp.merge(current_param, requested_param)
        patch = jmp.create_patch(origin_param, merged_param)

        if 'tags' in requested_param and requested_param['tags'] != target.tags:
            patch['tags'] = requested_param['tags']

        if not patch:
            msg = _('No change will be expected')
            raise exceptions.CommandError(msg)

        data = vnf_client.update_virtual_network_appliance(
            parsed_args.virtual_network_appliance, **patch)

        # Set plan name
        plan = vnf_client.get_virtual_network_appliance_plan(
            data.virtual_network_appliance_plan_id)
        setattr(data, 'virtual_network_appliance_plan', plan.name)

        _set_interfaces_for_display(data)

        return row_headers, utils.get_item_properties(data, rows)


class UpdateVirtualNetworkApplianceInterfaces(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(UpdateVirtualNetworkApplianceInterfaces, self). \
            get_parser(prog_name)
        parser.add_argument(
            'interface',
            metavar="<slot-no=number,name=interface-name,"
                    "description=interface-description,"
                    "tags=interface-tags,net-id=net-uuid,"
                    "fixed-ips=ip-addr1:ip-addr2...>",
            action='store',
            nargs='+',
            help=_("Specify interface parameter "
                   "for virtual network appliance. "
                   "slot-no: sequential number of interface,"
                   "name: Name of the interface,"
                   "description: Description of the interface,"
                   "tags: Tags of the interface,"
                   "      (e.g. '{\"tag1\": 1,\"tag2\": \"a\"...}' )"
                   "net-id: attach interface to network with this UUID, "
                   "fixed-ips: IPv4 fixed address for NIC. "
                   "You can specif multiple ip address by using ':' "
                   "(e.g: 1.1.1.1:2.2.2.2:...)")
        )
        parser.add_argument(
            'virtual_network_appliance',
            metavar='<virtual-network-appliance-id>',
            type=_type_uuid,
            help='Name or ID of virtual network appliance')

        return parser

    def take_action(self, parsed_args):
        vnf_client = self.app.eclsdk.conn.virtual_network_appliance

        target = vnf_client.get_virtual_network_appliance(
            parsed_args.virtual_network_appliance)

        rows = ROWS_FOR_SHOW
        row_headers = rows

        interfaces = []
        valid_keys = ['slot-no', 'name', 'description', 'tags', 'net-id',
                      'fixed-ips']
        for if_str in parsed_args.interface:
            # if_info = {"net-id": "", "fixed-ips": "",
            #            "slot-no": ""}
            if_info = {}
            if_info.update(utils.parse_vna_interface(if_str, valid_keys))

            interfaces.append(if_info)

        # conflict interfaces
        tmp_interfaces = []
        for interface in interfaces:
            tmp_interfaces.append(interface.get('slot-no'))

        if len(tmp_interfaces) != len(set(tmp_interfaces)):
            msg = _("Interfaces are duplicates")
            raise exceptions.CommandError(msg)

        requested_interface_object = {}
        tag_flag = False
        for interface in interfaces:
            slot_no = interface.get('slot-no')
            if_key = 'interface_' + str(slot_no)

            network_id = interface.get('net-id')
            fixed_ips_tmp = interface.get('fixed-ips')

            each_if_info = {}

            if 'name' in interface:
                name = interface.get('name', '')
                each_if_info.update({'name': name})

            if 'description' in interface:
                description = interface.get('description', '')
                each_if_info.update({'description': description})

            if 'tags' in interface:
                tag_flag = True
                tags = interface.get('tags')
                tags = tags if tags else '{}'
                try:
                    obj = json.loads(tags)
                except Exception:
                    msg = _("You must specify JSON object format")
                    raise exceptions.CommandError(msg)

                each_if_info.update({'tags': obj})

            if 'net-id' in interface:
                each_if_info.update({'network_id': network_id})

            if 'fixed-ips' in interface:
                fixed_ips = []
                if fixed_ips_tmp:
                    fixed_ips = [{'ip_address': ip}
                                 for ip in fixed_ips_tmp.split(':')]
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

        if patch == {} and tag_flag is False:
            msg = _('No change will be expected')
            raise exceptions.CommandError(msg)

        # ridding keys of unnecessary keys
        def __ridding_none_value(current, json_keys):
            for json_key in json_keys:
                if type(current) == 'dict':
                    next_current = tmp_current = current[json_key]
                    if tmp_current is None:
                        del current[json_key]
                    else:
                        next_keys = tmp_current.keys()
                        if len(next_keys) > 0:
                            current[json_key] = __ridding_none_value(
                                next_current, next_keys)
            return current

        if len(patch.keys()) > 0:
            patch = __ridding_none_value(patch, patch.keys())

        # replacing patched tags with requested tags
        for if_key in requested_interface_object.keys():
            interface = requested_interface_object[if_key]
            if 'tags' in interface:
                patch[if_key]['tags'] = interface.get('tags')

        patch = {'interfaces': patch}
        data = vnf_client.update_virtual_network_appliance(
            parsed_args.virtual_network_appliance, **patch)

        # Set plan name
        plan = vnf_client.get_virtual_network_appliance_plan(
            data.virtual_network_appliance_plan_id)
        setattr(data, 'virtual_network_appliance_plan', plan.name)

        _set_interfaces_for_display(data)

        return row_headers, utils.get_item_properties(data, rows)


class UpdateVirtualNetworkApplianceAAPs(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(UpdateVirtualNetworkApplianceAAPs, self). \
            get_parser(prog_name)
        parser.add_argument(
            '--add',
            metavar="<interface-slot-no=number,ip-address=ip-addr,"
                    "mac-address=mac-addr,type=type,vrid=vrid>",
            action='append',
            nargs='?',
            dest='adds',
            help=_("Specify Allowed Address Pair(A.A.P) parameter for "
                   "virtual network appliance. "
                   "interface-slot-no: sequential number of interface,"
                   "ip-address: IP address of A.A.P, "
                   "mac-address: MAC address of A.A.P, "
                   "type: Type of A.A.P. You can use 'vrrp' or '', "
                   "vrid: VRID of A.A.P. You can use this only in case vrrp, "
                   "You can specify same slot number multiple times."
                   "(e.g: interface-slot-no=1,ip-address=1.1.1.1 "
                   "interface-slot-no=1,ipaddress=2.2.2.2 ...) , "
                   "In this case, all values relates to interface-slot-no=1 "
                   "will be appended as interface_1.allowed_address_pairs "
                   "list."))
        parser.add_argument(
            '--delete',
            metavar='<interface-slot-no>',
            action='append',
            nargs='?',
            dest='deletes',
            help=_('interface-slot-no: sequential number of interface'))
        parser.add_argument(
            'virtual_network_appliance',
            metavar='<virtual-network-appliance-id>',
            type=_type_uuid,
            help=_('Name or ID of virtual network appliance'))

        return parser

    def take_action(self, parsed_args):
        vnf_client = self.app.eclsdk.conn.virtual_network_appliance

        target = vnf_client.get_virtual_network_appliance(
            parsed_args.virtual_network_appliance)

        rows = ROWS_FOR_SHOW
        row_headers = rows

        aaps = []
        adds = parsed_args.adds or []
        delete_aaps = []
        deletes = parsed_args.deletes or []

        if len(adds) == 0 and len(deletes) == 0:
            msg = _("No options are specified.")
            raise exceptions.CommandError(msg)

        valid_keys = ['interface-slot-no', 'ip-address', 'mac-address', 'type',
                      'vrid']
        for aap_str in adds:
            aap_info = {}
            aap_info.update(utils.parse_vna_interface(aap_str, valid_keys))
            aaps.append(aap_info)

        for aap_str in deletes:
            slot_no = re.sub(r'^interface-slot-no=(\d+)$', '\\1', aap_str)
            if not re.match(r'^\d+$', slot_no):
                msg = 'No interface number is specified.'
                raise exceptions.CommandError(msg)

            delete_aaps.append(slot_no)

        # duplicate interfaces check
        tmp_aaps = []
        for aap in aaps:
            tmp_aaps.append(aap.get('interface-slot-no'))

        for slot_no in delete_aaps:
            tmp_aaps.append(slot_no)

        if len(tmp_aaps) != len(set(tmp_aaps)):
            msg = _("Interfaces are duplicates")
            raise exceptions.CommandError(msg)

        requested_aap_object = {}
        for aap in aaps:
            slot_no = aap.get('interface-slot-no', None)
            if not slot_no:
                msg = 'No interface number is specified.'
                raise exceptions.CommandError(msg)

            # create key <-> value if not exist.
            if_key = 'interface_' + str(slot_no)
            requested_aap_object.setdefault(if_key,
                                            {'allowed_address_pairs': []})

            ip_address = aap.get('ip-address')
            mac_address = aap.get('mac-address')
            aap_type = aap.get('type')
            vrid = aap.get('vrid')

            each_aap_info = {
                'mac_address': '',
                'type': '',
                'vrid': None
            }

            if ip_address:
                each_aap_info.update({'ip_address': ip_address})

            if mac_address:
                each_aap_info.update({'mac_address': mac_address})

            if aap_type:
                each_aap_info.update({'type': aap_type})

            if vrid:
                try:
                    each_aap_info.update({'vrid': int(vrid)})
                except ValueError:
                    msg = 'vrid should be a positive number 1〜255'
                    raise exceptions.CommandError(msg)

            requested_aap_object[if_key]['allowed_address_pairs']. \
                append(each_aap_info)

            if mac_address and (aap_type == "vrrp" or vrid):
                msg = 'mac_address and vrrp type cannot be set ' \
                      'at the same time.'
                raise exceptions.CommandError(msg)

        for slot_no in delete_aaps:
            if_key = 'interface_' + slot_no
            requested_aap_object[if_key] = {'allowed_address_pairs': []}

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

        # Set plan name
        plan = vnf_client.get_virtual_network_appliance_plan(
            data.virtual_network_appliance_plan_id)
        setattr(data, 'virtual_network_appliance_plan', plan.name)

        _set_interfaces_for_display(data)

        return row_headers, utils.get_item_properties(data, rows)


class StartVirtualNetworkAppliance(command.Command):

    def get_parser(self, prog_name):
        parser = super(StartVirtualNetworkAppliance, self). \
            get_parser(prog_name)
        parser.add_argument(
            'virtual_network_appliance',
            metavar='<virtual-network-appliance-id>',
            nargs="+",
            help=_('Virtual Network Appliance ID to start'),
        )
        return parser

    def take_action(self, parsed_args):
        vnf_client = self.app.eclsdk.conn.virtual_network_appliance

        for virtual_network_appliance in parsed_args.virtual_network_appliance:
            vnf_client.start_virtual_network_appliance(
                virtual_network_appliance)


class StopVirtualNetworkAppliance(command.Command):

    def get_parser(self, prog_name):
        parser = super(StopVirtualNetworkAppliance, self). \
            get_parser(prog_name)
        parser.add_argument(
            'virtual_network_appliance',
            metavar='<virtual-network-appliance-id>',
            nargs="+",
            help=_('Virtual Network Appliance(s) to stop'),
        )
        return parser

    def take_action(self, parsed_args):
        vnf_client = self.app.eclsdk.conn.virtual_network_appliance

        for virtual_network_appliance in parsed_args.virtual_network_appliance:
            vnf_client.stop_virtual_network_appliance(
                virtual_network_appliance)


class RestartVirtualNetworkAppliance(command.Command):

    def get_parser(self, prog_name):
        parser = super(RestartVirtualNetworkAppliance, self). \
            get_parser(prog_name)
        parser.add_argument(
            'virtual_network_appliance',
            metavar='<virtual-network-appliance-id>',
            nargs="+",
            help=_('Virtual Network Appliance(s) to restart'),
        )
        return parser

    def take_action(self, parsed_args):
        vnf_client = self.app.eclsdk.conn.virtual_network_appliance

        for virtual_network_appliance in parsed_args.virtual_network_appliance:
            vnf_client.restart_virtual_network_appliance(
                virtual_network_appliance)


class ResetPasswordVirtualNetworkAppliance(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(ResetPasswordVirtualNetworkAppliance, self). \
            get_parser(prog_name)
        parser.add_argument(
            'virtual_network_appliance',
            metavar='<virtual-network-appliance-id>',
            # nargs="+",
            help=_('Virtual Network Appliance ID to restart'),
        )
        return parser

    def take_action(self, parsed_args):
        vnf_client = self.app.eclsdk.conn.virtual_network_appliance

        rows = [
            'ID',
            'Name',
            'Username',
            'New Password'
        ]
        row_headers = rows

        vna = parsed_args.virtual_network_appliance
        data = vnf_client.reset_password_virtual_network_appliance(vna)
        return row_headers, utils.get_item_properties(data, rows)


class ShowVirtualNetworkApplianceConsole(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(ShowVirtualNetworkApplianceConsole, self). \
            get_parser(prog_name)
        parser.add_argument(
            'virtual_network_appliance',
            metavar='<virtual-network-appliance-id>',
            help=_('Virtual Network Appliance ID to show console url'),
        )
        type_group = parser.add_mutually_exclusive_group()
        type_group.add_argument(
            '--novnc',
            dest='url_type',
            action='store_const',
            const='novnc',
            default='novnc',
            help='Show noVNC console URL (default)',
        )
        type_group.add_argument(
            '--xvpvnc',
            dest='url_type',
            action='store_const',
            const='xvpvnc',
            help='Show xpvnc console URL',
        )
        return parser

    def take_action(self, parsed_args):
        vnf_client = self.app.eclsdk.conn.virtual_network_appliance
        vna = parsed_args.virtual_network_appliance
        data = vnf_client.get_virtual_network_appliance_console(
            vna, parsed_args.url_type)

        return zip(*sorted(six.iteritems(data)))


def _set_interfaces_for_display(data):
    ifs = data.interfaces
    interfaces_json = json.dumps(ifs, indent=2)
    setattr(data, 'interfaces', interfaces_json)


def _type_uuid(uuid):
    regex = re.compile(UUID_PATTERN, re.I)
    if not regex.match(uuid):
        msg = _("%r is not a valid uuid")
        raise exceptions.CommandError(msg % uuid)
    return uuid
