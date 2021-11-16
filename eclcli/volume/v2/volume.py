#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

"""Volume V2 Volume action implementations"""

import copy

import six

from eclcli.common import command
from eclcli.common import parseractions
from eclcli.common import utils
from eclcli.identity import common as identity_common


class CreateVolume(command.ShowOne):
    """Create new volume"""

    def get_parser(self, prog_name):
        parser = super(CreateVolume, self).get_parser(prog_name)
        parser.add_argument(
            "name",
            metavar="<name>",
            help="New volume name"
        )
        parser.add_argument(
            "--size",
            metavar="<size>",
            type=int,
            required=True,
            help="New volume size in GB"
        )
        parser.add_argument(
            "--snapshot",
            metavar="<snapshot>",
            help="Use <snapshot> as source of new volume (name or ID)"
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help="New volume description"
        )
        parser.add_argument(
            "--type",
            metavar="<volume-type>",
            help="Use <volume-type> as the new volume type",
        )
        parser.add_argument(
            "--availability-zone",
            metavar="<availability-zone>",
            help="Create new volume in <availability_zone>"
        )
        parser.add_argument(
            "--image",
            metavar="<image>",
            help="Use <image> as source of new volume (name or ID)"
        )
        parser.add_argument(
            "--property",
            metavar="<key=value>",
            action=parseractions.KeyValueAction,
            help="Set a property to this volume "
                 "(repeat option to set multiple properties)"
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        image_client = self.app.client_manager.image

        image = None
        if parsed_args.image:
            image = utils.find_resource(
                image_client.images,
                parsed_args.image).id

        snapshot = None
        if parsed_args.snapshot:
            snapshot = utils.find_resource(
                volume_client.snapshots,
                parsed_args.snapshot).id

        volume = volume_client.volumes.create(
            size=parsed_args.size,
            snapshot_id=snapshot,
            name=parsed_args.name,
            description=parsed_args.description,
            volume_type=parsed_args.type,
            availability_zone=parsed_args.availability_zone,
            metadata=parsed_args.property,
            imageRef=image
        )
        # Remove key links from being displayed
        volume._info.update(
            {
                'properties': utils.format_dict(volume._info.pop('metadata')),
                'type': volume._info.pop('volume_type')
            }
        )
        volume._info.pop("links", None)
        return zip(*sorted(six.iteritems(volume._info)))


class DeleteVolume(command.Command):
    """Delete volume(s)"""

    def get_parser(self, prog_name):
        parser = super(DeleteVolume, self).get_parser(prog_name)
        parser.add_argument(
            "volumes",
            metavar="<volume>",
            nargs="+",
            help="Volume(s) to delete (name or ID)"
        )
        parser.add_argument(
            "--force",
            dest="force",
            action="store_true",
            default=False,
            help="Attempt forced removal of volume(s), regardless of state "
                 "(defaults to False)"
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        for volume in parsed_args.volumes:
            volume_obj = utils.find_resource(
                volume_client.volumes, volume)
            if parsed_args.force:
                volume_client.volumes.force_delete(volume_obj.id)
            else:
                volume_client.volumes.delete(volume_obj.id)


class ListVolume(command.Lister):
    """List volumes"""

    def get_parser(self, prog_name):
        parser = super(ListVolume, self).get_parser(prog_name)
        parser.add_argument(
            '--project',
            metavar='<project-id>',
            help='Filter results by project (name or ID) (admin only)'
        )
        identity_common.add_project_domain_option_to_parser(parser)
        parser.add_argument(
            '--user',
            metavar='<user-id>',
            help='Filter results by user (name or ID) (admin only)'
        )
        identity_common.add_user_domain_option_to_parser(parser)
        parser.add_argument(
            '--name',
            metavar='<name>',
            help='Filter results by volume name',
        )
        parser.add_argument(
            '--status',
            metavar='<status>',
            help='Filter results by status',
        )
        parser.add_argument(
            '--all-projects',
            action='store_true',
            default=False,
            help='Include all projects (admin only)',
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='List additional fields in output',
        )
        return parser

    def take_action(self, parsed_args):

        volume_client = self.app.client_manager.volume
        compute_client = self.app.client_manager.compute
        identity_client = self.app.client_manager.identity

        def _format_attach(attachments):
            """Return a formatted string of a volume's attached instances

            :param attachments: a volume.attachments field
            :rtype: a string of formatted instances
            """

            msg = ''
            for attachment in attachments:
                server = attachment['server_id']
                if server in server_cache:
                    server = server_cache[server].name
                device = attachment['device']
                msg += 'Attached to %s on %s ' % (server, device)
            return msg

        if parsed_args.long:
            columns = [
                'ID',
                'Name',
                'Status',
                'Size',
                'Volume Type',
                'Bootable',
                'Attachments',
                'Metadata',
            ]
            column_headers = copy.deepcopy(columns)
            column_headers[1] = 'Display Name'
            column_headers[4] = 'Type'
            column_headers[6] = 'Attached to'
            column_headers[7] = 'Properties'
        else:
            columns = [
                'ID',
                'Name',
                'Status',
                'Size',
                'Attachments',
            ]
            column_headers = copy.deepcopy(columns)
            column_headers[1] = 'Display Name'
            column_headers[4] = 'Attached to'

        # Cache the server list
        server_cache = {}
        try:
            for s in compute_client.servers.list():
                server_cache[s.id] = s
        except Exception:
            # Just forget it if there's any trouble
            pass

        project_id = None
        if parsed_args.project:
            project_id = identity_common.find_project(
                identity_client,
                parsed_args.project,
                parsed_args.project_domain)

        user_id = None
        if parsed_args.user:
            user_id = identity_common.find_user(identity_client,
                                                parsed_args.user,
                                                parsed_args.user_domain)

        search_opts = {
            'all_tenants': parsed_args.all_projects,
            'project_id': project_id,
            'user_id': user_id,
            'display_name': parsed_args.name,
            'status': parsed_args.status,
        }

        data = volume_client.volumes.list(search_opts=search_opts)

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={'Metadata': utils.format_dict,
                                'Attachments': _format_attach},
                ) for s in data))


class SetVolume(command.Command):
    """Set volume properties"""

    def get_parser(self, prog_name):
        parser = super(SetVolume, self).get_parser(prog_name)
        parser.add_argument(
            'volume',
            metavar='<volume>',
            help='Volume to change (name or ID)',
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help='New volume name',
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help='New volume description',
        )
        parser.add_argument(
            '--size',
            metavar='<size>',
            type=int,
            help='Extend volume size in GB',
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            help='Property to add or modify for this volume '
                 '(repeat option to set multiple properties)',
        )
        parser.add_argument(
            '--bootable',
            metavar='<boolean>',
            type=utils.parse_bool,
            choices=[True, False],
            help='Update bootable status of a volume.'
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        volume = utils.find_resource(volume_client.volumes, parsed_args.volume)

        if parsed_args.size:
            if volume.status != 'available':
                self.app.log.error("Volume is in %s state, it must be "
                                   "available before size can be extended" %
                                   volume.status)
                return
            if parsed_args.size <= volume.size:
                self.app.log.error("New size must be greater than %s GB" %
                                   volume.size)
                return
            volume_client.volumes.extend(volume.id, parsed_args.size)

        if parsed_args.property:
            volume_client.volumes.set_metadata(volume.id, parsed_args.property)

        if parsed_args.bootable is not None:
            volume_client.volumes.set_bootable(volume.id, parsed_args.bootable)

        kwargs = {}
        if parsed_args.name:
            kwargs['display_name'] = parsed_args.name
        if parsed_args.description:
            kwargs['display_description'] = parsed_args.description
        if kwargs:
            volume_client.volumes.update(volume.id, **kwargs)

        if not kwargs and not parsed_args.property and not parsed_args.size \
           and not parsed_args.bootable:
            self.app.log.error("No changes requested\n")


class ShowVolume(command.ShowOne):
    """Display volume details"""

    def get_parser(self, prog_name):
        parser = super(ShowVolume, self).get_parser(prog_name)
        parser.add_argument(
            'volume',
            metavar="<volume-id>",
            help="Volume to display (name or ID)"
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        volume = utils.find_resource(volume_client.volumes, parsed_args.volume)

        # Special mapping for columns to make the output easier to read:
        # 'metadata' --> 'properties'
        # 'volume_type' --> 'type'
        volume._info.update(
            {
                'properties': utils.format_dict(volume._info.pop('metadata')),
                'type': volume._info.pop('volume_type'),
            },
        )

        # Remove key links from being displayed
        volume._info.pop("links", None)
        return zip(*sorted(six.iteritems(volume._info)))


class UnsetVolume(command.Command):
    """Unset volume properties"""

    def get_parser(self, prog_name):
        parser = super(UnsetVolume, self).get_parser(prog_name)
        parser.add_argument(
            'volume',
            metavar='<volume>',
            help='Volume to modify (name or ID)',
        )
        parser.add_argument(
            '--property',
            metavar='<key>',
            required=True,
            action='append',
            default=[],
            help='Property to remove from volume '
                 '(repeat option to remove multiple properties)',
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        volume = utils.find_resource(
            volume_client.volumes, parsed_args.volume)

        volume_client.volumes.delete_metadata(
            volume.id, parsed_args.property)
