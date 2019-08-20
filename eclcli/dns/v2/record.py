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

"""Record action implementations"""

import re

from eclcli.common import command
from eclcli.common import exceptions
from eclcli.common import utils
from eclcli.i18n import _  # noqa


class CreateRecordSet(command.Lister):
    """Create new recordset"""

    def get_parser(self, prog_name):
        parser = super(CreateRecordSet, self).get_parser(prog_name)
        parser.add_argument(
            "zone_id",
            metavar="<zone_id>",
            help="ID of the zone which the recordset belong to."
        )
        parser.add_argument(
            "--name",
            required=True,
            metavar="<name>",
            help="DNS Name for the recordset.",
        )
        parser.add_argument(
            "--type",
            required=True,
            choices=['A', 'AAAA', 'MX', 'CNAME', 'SRV',
                     'SPF', 'TXT', 'PTR', 'NS'],
            metavar="{ A | AAAA | MX | CNAME | SRV | SPF | TXT | PTR | NS }",
            help="TYPE of the recordset, one of A, AAAA, MX, "
                 "CNAME, SRV, SPF, TXT, PTR, NS.",
        )
        parser.add_argument(
            "--ttl",
            required=True,
            type=int,
            metavar="<ttl>",
            help="TTL (Time to Live) for the recordset.",
        )
        parser.add_argument(
            "--records",
            required=True,
            nargs='+',
            metavar="<records>",
            help="records for the recordset, should match the type.",
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help="Description for this recordset",
        )

        return parser

    def take_action(self, parsed_args):
        dns_client = self.app.eclsdk.conn.dns

        kwargs = {
            'zone_id': parsed_args.zone_id,
            'name': parsed_args.name,
            'records': parsed_args.records,
            'ttl': parsed_args.ttl,
            'type': parsed_args.type,
            'description': parsed_args.description,
        }
        columns = [
            'description',
            'links',
            'updated_at',
            'records',
            'ttl',
            'id',
            'name',
            'zone_id',
            'created_at',
            'version',
            'type',
        ]

        recordset = dns_client.create_recordset(**kwargs)

        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={'Metadata': utils.format_dict},
                ) for s in recordset))


class DeleteRecordSet(command.Command):

    def get_parser(self, prog_name):
        parser = super(DeleteRecordSet, self).get_parser(prog_name)
        parser.add_argument(
            "zone_id",
            metavar="<zone_id>",
            help="ID of the zone which recordset you want to delete belong to.",
        )
        parser.add_argument(
            "recordset_id",
            metavar="<record_id>",
            help="ID of the recordset you want to delete.",
        )
        return parser

    def take_action(self, parsed_args):
        dns_client = self.app.eclsdk.conn.dns
        dns_client.delete_recordset(parsed_args.zone_id, parsed_args.recordset_id)


class DeleteMultipleRecordSets(command.Command):

    def get_parser(self, prog_name):
        parser = super(DeleteMultipleRecordSets, self).get_parser(prog_name)
        parser.add_argument(
            "zone_id",
            metavar="<zone_id>",
            help="ID of the zone which recordset you want to delete belong to.",
        )
        parser.add_argument(
            "recordset_ids",
            metavar="<record_id>",
            nargs='+',
            help="IDs of the recordsets you want to delete.",
        )
        return parser

    def take_action(self, parsed_args):
        dns_client = self.app.eclsdk.conn.dns
        dns_client.delete_multiple_recordsets(parsed_args.zone_id, parsed_args.recordset_ids)


class ShowRecordSet(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(ShowRecordSet, self).get_parser(prog_name)
        parser.add_argument(
            "zone_id",
            metavar="<zone_id>",
            help="ID of the zone which recordset you want to show belong to.",
        )
        parser.add_argument(
            "recordset_id",
            metavar="<record_id>",
            help="ID of the recordset you want to show.",
        )
        return parser

    def take_action(self, parsed_args):
        dns_client = self.app.eclsdk.conn.dns

        row = [
            'id',
            'zone_id',
            'name',
            'ttl',
            'records',
            'status',
            'description',
            'type',
            'version',
            'created_at',
            'updated_at',
            'links',
        ]
        recordset = dns_client.get_recordset(parsed_args.zone_id, parsed_args.recordset_id)

        return row, utils.get_item_properties(recordset, row)


class ListRecordSet(command.Lister):

    def get_parser(self, prog_name):
        parser = super(ListRecordSet, self).get_parser(prog_name)
        parser.add_argument(
            "zone_id",
            metavar="<zone_id>",
            type=_type_uuid,
            help="ID of the zone which recordset you want to list belong to.",
        )
        parser.add_argument(
            "--limit",
            metavar="<limit>",
            type=call_limit_validate_int_range,
            default=None,
            help="The number of record sets that you want to display."
                 "Values range from 1 to 500. (default=100)",
        )
        parser.add_argument(
            "--marker",
            metavar="<marker>",
            type=_type_uuid,
            default=None,
            help="Specify the ID for the resource."
                 "It is displayed from the next record of the specified ID.",
        )
        return parser

    def take_action(self, parsed_args):
        dns_client = self.app.eclsdk.conn.dns

        recordsets = dns_client.recordsets(parsed_args.zone_id, parsed_args.limit, parsed_args.marker)

        columns = [
            'id',
            'zone_id',
            'name',
            'ttl',
            'records',
            'status',
            'description',
            'type',
            'version',
            'created_at',
            'updated_at',
            'links',
        ]

        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={'Metadata': utils.format_dict},
                ) for s in recordsets))


class UpdateRecordSet(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(UpdateRecordSet, self).get_parser(prog_name)
        parser.add_argument(
            "zone_id",
            metavar="<zone_id>",
            help="ID of the zone which recordset you want to update belong to.",
        )
        parser.add_argument(
            "recordset_id",
            metavar="<record_id>",
            help="ID of the recordset you want to delete.",
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help="Description for this description",
        )
        parser.add_argument(
            "--name",
            metavar="<name>",
            help="DNS Name for the recordset.",
        )
        parser.add_argument(
            "--records",
            nargs='+',
            metavar="<record>",
            help="A list of data for this recordset.",
        )
        parser.add_argument(
            "--ttl",
            type=int,
            metavar="<ttl>",
            help="TTL (Time to Live) for the recordset.",
        )
        return parser

    def take_action(self, parsed_args):
        dns_client = self.app.eclsdk.conn.dns

        kwargs = {
            'zone_id': parsed_args.zone_id,
            'recordset': parsed_args.recordset_id,
            'name': parsed_args.name,
            'records': parsed_args.records,
            'ttl': parsed_args.ttl,
            'description': parsed_args.description,
        }

        recordset = dns_client.update_recordset(**kwargs)

        row = [
            'description',
            'links',
            'updated_at',
            'records',
            'ttl',
            'id',
            'name',
            'zone_id',
            'created_at',
            'version',
            'type',
        ]

        return row, utils.get_item_properties(recordset, row)


def call_limit_validate_int_range(text):
    return utils.validate_int_range(text, 1, 500)


def _type_uuid(uuid):
    regex = re.compile("^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z", re.I)
    if not regex.match(uuid):
        msg = _("%r is not a valid uuid")
        raise exceptions.CommandError(msg % uuid)
    return uuid
