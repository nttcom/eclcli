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


from eclcli.common import command
from eclcli.common import utils


class ShowNameServer(command.Lister):

    def get_parser(self, prog_name):
        parser = super(ShowNameServer, self).get_parser(prog_name)
        parser.add_argument(
            "zone_id",
            metavar="<zone_id>",
            help="ID of the zone which nameservers you want to show belong to.",
        )
        return parser

    def take_action(self, parsed_args):
        dns_client = self.app.eclsdk.conn.dns

        nameservers = dns_client.get_name_server(parsed_args.zone_id)

        columns = [
            'hostname',
            'priority',
        ]

        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={'Metadata': utils.format_dict},
                ) for s in nameservers))