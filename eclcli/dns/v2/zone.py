#   Copyright 2013 OpenStack Foundation
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

"""Zone action implementations"""


from eclcli.common import command
from eclcli.common import utils
from eclcli.i18n import _  # noqa


class CreateZone(command.ShowOne):
    """Create new zone"""

    def get_parser(self, prog_name):
        parser = super(CreateZone, self).get_parser(prog_name)
        parser.add_argument(
            "name",
            metavar="<name>",
            help="DNS Name for the zone."
        )
        parser.add_argument(
            "--email",
            metavar="<email>",
            help="e-mail for the zone. Used in SOA records for the zone.",
        )
        parser.add_argument(
            "--masters",
            nargs='+',
            metavar="<masters>",
            help="For secondary zones. The servers to slave from to get DNS information. ",
        )
        parser.add_argument(
            "--ttl",
            type=int,
            metavar="<ttl>",
            help="TTL (Time to Live) for the zone.",
        )
        parser.add_argument(
            "--type",
            metavar="<type>",
            default="PRIMARY",
            choices=["PRIMARY", "SECONDARY"],
            help="Type of zone. Optional values are PRIMARY or SECONDARY. Defaults to PRIMARY.",
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help="Description for this zone",
        )
        return parser

    def take_action(self, parsed_args):
        dns_client = self.app.eclsdk.conn.dns

        kwargs = {
            'name': parsed_args.name,
            'email': parsed_args.email,
            'masters': parsed_args.masters,
            'ttl': parsed_args.ttl,
            'type': parsed_args.type,
            'description': parsed_args.description,
        }
        row = [
            'id',
            'pool_id',
            'project_id',
            'name',
            'email',
            'ttl',
            'serial',
            'status',
            'description',
            'masters',
            'type',
            'transferred_at',
            'version',
            'created_at',
            'updated_at',
            'links',
        ]

        zone = dns_client.create_zone(**kwargs)

        return row, utils.get_item_properties(zone, row)


class DeleteZone(command.Command):
    _description = _("Delete zone of DNS")

    def get_parser(self, prog_name):
        parser = super(DeleteZone, self).get_parser(prog_name)
        parser.add_argument(
            "zone_id",
            metavar="<zone_id>",
            help="ID of the zone you want to delete.",
        )
        return parser

    def take_action(self, parsed_args):
        dns_client = self.app.eclsdk.conn.dns
        dns_client.delete_zone(parsed_args.zone_id)


class ShowZone(command.ShowOne):
    _description = _("Show zone of DNS")

    def get_parser(self, prog_name):
        parser = super(ShowZone, self).get_parser(prog_name)
        parser.add_argument(
            "zone_id",
            metavar='<zone_id>',
            help='ID of the zone to show.'
        )
        return parser

    def take_action(self, parsed_args):
        dns_client = self.app.eclsdk.conn.dns

        row = [
            'id',
            'pool_id',
            'project_id',
            'name',
            'email',
            'ttl',
            'serial',
            'status',
            'description',
            'masters',
            'type',
            'transferred_at',
            'version',
            'created_at',
            'updated_at',
            'links',
        ]

        zone = dns_client.get_zone(parsed_args.zone_id)

        return row, utils.get_item_properties(zone, row)


class ListZone(command.Lister):
    _description = _("List zones of DNS")

    def get_parser(self, prog_name):
        parser = super(ListZone, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        dns_client = self.app.eclsdk.conn.dns

        zones = dns_client.zones()

        columns = [
            'id',
            'pool_id',
            'project_id',
            'name',
            'email',
            'ttl',
            'serial',
            'status',
            'description',
            'masters',
            'type',
            'transferred_at',
            'version',
            'created_at',
            'updated_at',
            'links',
        ]

        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={'Metadata': utils.format_dict},
                ) for s in zones))


class UpdateZone(command.ShowOne):
    _description = _("Update zone of DNS")

    def get_parser(self, prog_name):
        parser = super(UpdateZone, self).get_parser(prog_name)
        parser.add_argument(
            "zone_id",
            metavar="<zone_id>",
            help="zone id which you want to update"
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help="Description for this zone",
        )
        parser.add_argument(
            "--email",
            metavar="<email>",
            help="e-mail for the zone. Used in SOA records for the zone.",
        )
        parser.add_argument(
            "--masters",
            nargs='+',
            metavar="<masters>",
            help="For secondary zones. The servers to slave from to get DNS information. ",
        )
        parser.add_argument(
            "--ttl",
            type=int,
            metavar="<ttl>",
            help="TTL (Time to Live) for the zone.",
        )
        return parser

    def take_action(self, parsed_args):
        dns_client = self.app.eclsdk.conn.dns

        kwargs = {
            'zone': parsed_args.zone_id,
            'email': parsed_args.email,
            'masters': parsed_args.masters,
            'ttl': parsed_args.ttl,
            'description': parsed_args.description,
        }
        zone = dns_client.update_zone(**kwargs)

        row = [
            'id',
            'pool_id',
            'project_id',
            'name',
            'email',
            'ttl',
            'serial',
            'status',
            'description',
            'masters',
            'type',
            'transferred_at',
            'version',
            'created_at',
            'updated_at',
            'links',
        ]

        return row, utils.get_item_properties(zone, row)
