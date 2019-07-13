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

from eclcli.common import command
from eclcli.common import utils
from .. import monitoring_utils


class ListSample(command.Lister):
    """Lists samples in a specified time range."""
    def get_parser(self, prog_name):
        parser = super(ListSample, self).get_parser(prog_name)

        parser.add_argument(
            "--field",
            metavar="<field>",
            help="A meter column of retrieving target",
        )
        parser.add_argument(
            "--value",
            metavar="<value>",
            help="A field value for retrieving meters",
        )
        parser.add_argument(
            "--op",
            metavar="<operator>",
            help="A comparison operator",
            default="eq"
        )
        parser.add_argument(
            "--type",
            metavar="<type>",
            help="Format used to convert the value for comparison",
        )
        parser.add_argument(
            "--page",
            metavar="<page>",
            help="Target page number",
            default=1
        )
        parser.add_argument(
            "--per_page",
            metavar="<per_page>",
            help="Number of resources contained in a page",
            default=100
        )

        return parser

    def take_action(self, parsed_args):
        q = monitoring_utils._make_query(parsed_args)
        monitoring_client = self.app.client_manager.monitoring
        data = monitoring_client.samples.list(
            q=q, page=parsed_args.page, per_page=parsed_args.per_page)

        columns = (
            'meter',
            'display_name',
            'project_id',
            'recorded_at',
            'resource_id',
            'namespace',
            'timestamp',
            'type',
            'unit',
            'volume',
        )
        return (columns,
                (utils.get_item_properties(
                    s, columns) for s in data))
