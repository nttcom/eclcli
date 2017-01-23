
import six
import sys

from eclcli.common import command

from eclcli.common import exceptions
from eclcli.common import utils
from eclcli.i18n import _  # noqa
from eclcli.bare import bare_utils


def _format_servers_list_networks(networks):
    """Return a formatted string of a server's networks

    :param networks: a Server.networks field
    :rtype: a string of formatted network addresses
    """
    output = []
    for (network, addresses) in networks.items():
        if not addresses:
            continue
        addresses_csv = ', '.join(addresses)
        group = "%s=%s" % (network, addresses_csv)
        output.append(group)
    return '; '.join(output)


def _format_servers_list_power_state(state):
    """Return a formatted string of a server's power state

    :param state: the power state number of a server
    :rtype: a string mapped to the power state number
    """
    power_states = [
        'NOSTATE',      # 0x00
        'Running',      # 0x01
        '',             # 0x02
        'Paused',       # 0x03
        'Shutdown',     # 0x04
        '',             # 0x05
        'Crashed',      # 0x06
        'Suspended'     # 0x07
    ]

    try:
        return power_states[state]
    except Exception:
        return 'N/A'


def _get_ip_address(addresses, address_type, ip_address_family):
        # Old style addresses
        if address_type in addresses:
            for addy in addresses[address_type]:
                if int(addy['version']) in ip_address_family:
                    return addy['addr']

        # New style addresses
        new_address_type = address_type
        if address_type == 'public':
            new_address_type = 'floating'
        if address_type == 'private':
            new_address_type = 'fixed'
        for network in addresses:
            for addy in addresses[network]:
                # Case where it is list of strings
                if isinstance(addy, six.string_types):
                    if new_address_type == 'fixed':
                        return addresses[network][0]
                    else:
                        return addresses[network][-1]
                # Case where it is a dict
                if 'OS-EXT-IPS:type' not in addy:
                    continue
                if addy['OS-EXT-IPS:type'] == new_address_type:
                    if int(addy['version']) in ip_address_family:
                        return addy['addr']
        raise exceptions.CommandError(
            "ERROR: No %s IP version %s address found" %
            (address_type, ip_address_family)
        )


def _prep_server_detail(compute_client, server):
    """Prepare the detailed server dict for printing

    :param compute_client: a compute client instance
    :param server: a Server resource
    :rtype: a dict of server details
    """
    info = server._info.copy()

    # Call .get() to retrieve all of the server information
    # as findall(name=blah) and REST /details are not the same
    # and do not return flavor and image information.
    server = compute_client.servers.get(info['id'])
    info.update(server._info)

    # Convert the image blob to a name
    image_info = info.get('image', {})
    if image_info:
        image_id = image_info.get('id', '')
        try:
            image = utils.find_resource(compute_client.images, image_id)
            info['image'] = "%s (%s)" % (image.name, image_id)
        except Exception:
            info['image'] = image_id

    # Convert the flavor blob to a name
    flavor_info = info.get('flavor', {})
    flavor_id = flavor_info.get('id', '')
    try:
        flavor = utils.find_resource(compute_client.flavors, flavor_id)
        info['flavor'] = "%s (%s)" % (flavor.name, flavor_id)
    except Exception:
        info['flavor'] = flavor_id

    # NOTE(dtroyer): novaclient splits these into separate entries...
    # Format addresses in a useful way
    info['addresses'] = _format_servers_list_networks(server.networks)

    # Map 'metadata' field to 'properties'
    info.update(
        {'properties': utils.format_dict(info.pop('metadata'))}
    )

    # Migrate tenant_id to project_id naming
    if 'tenant_id' in info:
        info['project_id'] = info.pop('tenant_id')

    # Remove values that are long and not too useful
    info.pop('links', None)

    return info


def _show_progress(progress):
    if progress:
        sys.stdout.write('\rProgress: %s' % progress)
        sys.stdout.flush()


class ListServer(command.Lister):
    """List all baremetal servers"""

    def get_parser(self, prog_name):
        parser = super(ListServer, self).get_parser(prog_name)

        parser.add_argument(
            "--detail",
            help="Detailed view of server list",
            action='store_true',
        )
        parser.add_argument(
            "--changes-since",
            help="Filter by changes after a date",
            metavar='<changes-since>'
        )
        parser.add_argument(
            "--marker",
            help="List servers after the marker. Marker must be a server UUID",
            metavar='<marker>',
        )
        parser.add_argument(
            "--limit",
            help="Limit the list items",
            metavar='<limit>',
        )
        parser.add_argument(
            "--name",
            help="Filter by server name",
            metavar='<name>',
        )
        parser.add_argument(
            "--image",
            help="Filter by image in URL format",
            metavar='<image>',
        )
        parser.add_argument(
            "--flavor",
            help="Filter by flavor in URL format",
            metavar='<flavor>',
        )
        parser.add_argument(
            "--status",
            help="Filter by server status",
            metavar='<status>',
        )
        return parser

    def take_action(self, parsed_args):
        bare_client = self.app.client_manager.bare

        search_opts = {
            "changes-since":parsed_args.changes_since,
            "marker":parsed_args.marker,
            "limit":parsed_args.limit,
            "name":parsed_args.name,
            "image":parsed_args.image,
            "flavor":parsed_args.flavor,
            "status":parsed_args.status
        }
        self.log.debug('search options: %s', search_opts)

        if parsed_args.detail:
            columns = (
                'ID',
                'Name',
                'Status',
                'Progress',
                'LVM Volume Groups',
                'Filesystems',
                'Chassis-Status',
            )
            column_headers = (
                'ID',
                'Name',
                'Status',
                'Progress',
                'LVM Volume Groups',
                'Filesystems',
                'Chassis-Status',
            )
        else:
            columns = (
                'ID',
                'Name',
            )
            column_headers = (
                'ID',
                'Name',
            )
        mixed_case_fields = []

        data = bare_client.servers.list(search_opts=search_opts,detailed=parsed_args.detail)
        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    mixed_case_fields=mixed_case_fields,
                    formatters={
                        'OS-EXT-STS:power_state':
                            _format_servers_list_power_state,
                        'Networks': _format_servers_list_networks,
                        'Metadata': utils.format_dict,
                        'Filesystems': bare_utils._format_dicts_list_generic,
                        'Chassis-Status':bare_utils._format_dicts_list_generic,
                    },
                ) for s in data))


class ShowServer(command.ShowOne):
    """Show baremetal server's detail"""

    def get_parser(self, prog_name):
        parser = super(ShowServer, self).get_parser(prog_name)
        parser.add_argument(
            "server",
            metavar="<server>",
            help="Name or ID of server",
        )
        return parser

    def take_action(self, parsed_args):
        bare_client = self.app.client_manager.bare

        columns = (
            'ID',
            'Name',
            'Status',
            'Networks',
            'OS-EXT-STS:power_state',
            'OS-EXT-STS:task_state',
            'OS-EXT-STS:vm_state',
            'OS-EXT-AZ:availability_zone',
            'created',
            'flavor',
            'Image',
            'Links',
            'Metadata',
            'Progress',
            'Tenant Id',
            'Updated',
            'User Id',
            'Raid Arrays',
            'LVM Volume Groups',
            'Filesystems',
            'Nic Physical Ports',
            'Chassis-Status'
        )
        column_headers = (
            'ID',
            'Name',
            'Status',
            'Networks',
            'OS-EXT-STS:power_state',
            'OS-EXT-STS:task_state',
            'OS-EXT-STS:vm_state',
            'OS-EXT-AZ:availability_zone',
            'created',
            'flavor',
            'Image',
            'Links',
            'Metadata',
            'Progress',
            'Tenant Id',
            'Updated',
            'User Id',
            'Raid Arrays',
            'LVM Volume Groups',
            'Filesystems',
            'Nic Physical Ports',
            'Chassis-Status'
        )
        mixed_case_fields = ['OS-EXT-STS:power_state',
                             'OS-EXT-STS:task_state',
                             'OS-EXT-STS:vm_state',
                             'OS-EXT-AZ:availability_zone',]

        data = utils.find_resource(bare_client.servers,parsed_args.server)
        return column_headers, utils.get_item_properties(
            data, columns, mixed_case_fields, formatters={
                'flavor': bare_utils._format_imageORflavor,
                'Image': bare_utils._format_imageORflavor,
                'Links': bare_utils._format_links,
                'Metadata': bare_utils._format_dicts_list_generic,
                'Raid Arrays': bare_utils._format_dicts_list_generic,
                'Nic Physical Ports': bare_utils._format_dicts_list_generic,
                'Filesystems': bare_utils._format_dicts_list_generic,
                'Chassis-Status': bare_utils._format_dicts_list_generic
            })


class CreateServer(command.ShowOne):
    """Create a baremetal server"""

    def get_parser(self, prog_name):
        parser = super(CreateServer, self).get_parser(prog_name)
        parser.add_argument(
            "name",
            metavar="<name>",
            help="Server name",
        )
        parser.add_argument(
            "flavor",
            metavar="<flavor>",
            help="Flavor ID",
        )
        parser.add_argument(
            "image",
            metavar="<image>",
            help="Image ID",
        )

        parser.add_argument(
            "--nic",
            metavar="<uuid=net-uuid, fixed_ip=ip-addr, port=port-uuid,",
            action='append',
            default=[],
            help=_("Create a NIC on the server. "
                   "Specify option multiple times to create multiple NICs. "
                   "Either net-id or port-id must be provided, but not both. "
                   "uuid: attach NIC to network with this UUID, "
                   "port: attach NIC to port with this UUID, "
                   "fixed_ip: IPv4 fixed address for NIC (optional)"),
        )

        parser.add_argument(
            "--key",
            metavar="<key>",
            help="Name of SSH key to create/attach",
        )

        parser.add_argument(
            "--adminPass",
            metavar="<adminPass>",
            help="Password for the administrator",
        )

        parser.add_argument(
            "--availability-zone",
            metavar="<availability-zone>",
            help="Availability zone to the launch the server in",
        )
        parser.add_argument(
            "--user-data",
            metavar="<user-data>",
            help="Configuration information or scripts to use upon launch",
        )
        parser.add_argument(
            "--metadata",
            metavar="<metadata>",
            help="Command separated list of key-value pairs, eg. KEY1=VALUE1,KEY2,VALUE2",
        )
        parser.add_argument(
            "--personality",
            metavar="<personality>",
            help="File path and contents to be injected in server upon launch. (Not supported in esxi)",
        )
        parser.add_argument(
            "--raid-arrays",
            metavar="<raid-arrays>",
            help="Comma separated list of raid array(s)",
        )
        parser.add_argument(
            "--filesystems",
            metavar="<filesystems>",
            help="Partition filesystems and mount point information",
        )
        parser.add_argument(
            "--lvm-volume-groups",
            metavar="<lvm_volume_groups>",
            help="LVM information required if you want to enable lvm flag in raid array",
        )
        return parser

    def take_action(self, parsed_args):
        bare_client = self.app.client_manager.bare

        nics = []
        for nic_str in parsed_args.nic:
            nic_info = (dict(kv_str.split("=", 1)
                             for kv_str in nic_str.split(",")))
            if "uuid" in nic_info and "port" in nic_info or \
                    "uuid" not in nic_info and "port" not in nic_info:
                msg = _("either uuid or port should be specified "
                        "but not both")
                raise exceptions.CommandError(msg)

            nics.append(nic_info)

        columns = (
            'ID',
            'Name',
            'Status',
            'Networks',
            'OS-EXT-STS:power_state',
            'OS-EXT-STS:task_state',
            'OS-EXT-STS:vm_state',
            'OS-EXT-AZ:availability_zone',
            'created',
            'flavor',
            'Image',
            'Links',
            'Metadata',
            'Progress',
            'Tenant Id',
            'Updated',
            'User Id',
            'Raid Arrays',
            'LVM Volume Groups',
            'Filesystems',
            'Nic Physical Ports',
            'Chassis-Status'
        )
        disk_config = {}
        if parsed_args.raid_arrays:
            disk_config['raid_arrays'] = parsed_args.raid_arrays
        if parsed_args.lvm_volume_groups:
            disk_config['lvm_volume_groups'] = parsed_args.lvm_volume_groups
        if parsed_args.filesystems:
            disk_config['filesystems'] = parsed_args.filesystems

        mixed_case_fields = ['OS-EXT-STS:power_state',
                             'OS-EXT-STS:task_state',
                             'OS-EXT-STS:vm_state',
                             'OS-EXT-AZ:availability_zone', ]

        data = bare_client.servers.create(name=parsed_args.name,
                                          flavor=parsed_args.flavor,
                                          image=parsed_args.image,
                                          nics=nics,
                                          admin_pass=parsed_args.adminPass,
                                          key_name=parsed_args.key,
                                          availability_zone=parsed_args.availability_zone,
                                          userdata=parsed_args.user_data,
                                          meta=parsed_args.metadata,
                                          files=parsed_args.personality,
                                          disk_config=str(disk_config)
                                          )
        return (columns, utils.get_item_properties(data, columns, mixed_case_fields, formatters=
                {
                    'flavor': bare_utils._format_imageORflavor,
                    'Image': bare_utils._format_imageORflavor,
                    'Links': bare_utils._format_links,
                    'Metadata': bare_utils._format_dicts_list_generic,
                    'Nic Physical Ports': bare_utils._format_dicts_list_generic,
                    'Raid Arrays': bare_utils._format_dicts_list_generic,
                    'Filesystems': bare_utils._format_dicts_list_generic,
                    'Chassis-Status': bare_utils._format_dicts_list_generic
                }))


class DeleteServer(command.ShowOne):
    """Delete a baremetal server"""

    def get_parser(self, prog_name):
        parser = super(DeleteServer, self).get_parser(prog_name)
        parser.add_argument(
            "server",
            metavar="<server>",
            help="Name or ID of server",
        )
        return parser

    def take_action(self, parsed_args):
        bare_client = self.app.client_manager.bare
        server_obj = utils.find_resource(bare_client.servers,parsed_args.server)
        bare_client.servers.delete(server_obj.id)
        return {}, {}


class StartServer(command.ShowOne):
    """Start a baremetal server"""

    def get_parser(self, prog_name):
        parser = super(StartServer, self).get_parser(prog_name)
        parser.add_argument(
            "server",
            metavar="<server>",
            help="Name or ID or server",
        )
        parser.add_argument(
            "--boot-mode",
            metavar="<boot-mode>",
            help="Baremetal Server boot mode. A valid value is DISK, PXE or ISO",
        )
        return parser

    def take_action(self, parsed_args):
        bare_client = self.app.client_manager.bare

        server_obj = utils.find_resource(bare_client.servers,parsed_args.server)
        if parsed_args.boot_mode:
            data = bare_client.servers.start_with_mode(server_obj.id,{"boot_mode":parsed_args.boot_mode})
        else:
            data = bare_client.servers.start(server_obj.id)
        return {}, {}


class StopServer(command.ShowOne):
    """Stop a baremetal server"""

    def get_parser(self, prog_name):
        parser = super(StopServer, self).get_parser(prog_name)
        parser.add_argument(
            "server",
            metavar="<server>",
            help="Name or ID of server",
        )
        return parser

    def take_action(self, parsed_args):
        bare_client = self.app.client_manager.bare

        server_obj = utils.find_resource(bare_client.servers,parsed_args.server)
        bare_client.servers.stop(server_obj.id)
        return {}, {}


class RebootServer(command.ShowOne):
    """Reboot a baremetal server"""

    def get_parser(self, prog_name):
        parser = super(RebootServer, self).get_parser(prog_name)
        parser.add_argument(
            "server",
            metavar="<server>",
            help="Name or ID of server",
        )
        parser.add_argument(
            "--type",
            metavar="<type>",
            default="SOFT",
            help="Server shutdown mode. A valid value is HARD (IPMI) or SOFT (ACPI)",
        )
        parser.add_argument(
            "--boot-mode",
            metavar="<boot-mode>",
            help="baremetal server boot mode. A valid value is DISK, PXE or ISO.",
        )
        return parser

    def take_action(self, parsed_args):
        bare_client = self.app.client_manager.bare

        body = {'type': parsed_args.type}
        if parsed_args.boot_mode:
            body['boot_mode'] = parsed_args.boot_mode
        server_obj = utils.find_resource(bare_client.servers,parsed_args.server)
        bare_client.servers.reboot_with_mode(server_obj.id,body)
        return {}, {}


class GetConsoleServer(command.ShowOne):
    """Get management console details"""

    def get_parser(self, prog_name):
        parser = super(GetConsoleServer, self).get_parser(prog_name)
        parser.add_argument(
            "server",
            metavar="<server>",
            help="Name or ID of server",
        )
        return parser

    def take_action(self, parsed_args):
        bare_client = self.app.client_manager.bare

        columns = (
            'Type',
            'URL',
            'User ID',
            'Password',
        )

        server_obj = utils.find_resource(bare_client.servers,parsed_args.server)
        data = bare_client.servers.get_management_console(server_obj.id)['console']
        return columns, utils.get_dict_properties(data, columns)
