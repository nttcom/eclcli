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

class ListResource(command.Lister):
    """Lists all metering resources."""
    def get_parser(self, prog_name):
        parser = super(ListResource, self).get_parser(prog_name)

        parser.add_argument(
            "--field",
            metavar="<field>",
            help="q.field. A meter column of retrieving target",
        )
        parser.add_argument(
            "--value",
            metavar="<value>",
            help="q.value. A field value for retrieving meters",
        )
        parser.add_argument(
            "--op",
            metavar="<operator>",
            help="q.op. A comparison operator",
            default="eq"
        )
        parser.add_argument(
            "--type",
            metavar="<type>",
            help="q.type. Format used to convert the value for comparison",
        )
        parser.add_argument(
            "--meter_links",
            metavar="<meter_links>",
            help="All meter links will be returned if setting 'meter_links' equal to 1",
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

        data = monitoring_client.resources.list(
            q=q,
            links=parsed_args.meter_links,
            page=parsed_args.page,
            per_page=parsed_args.per_page,
        )
        if parsed_args.meter_links:
            columns = (
                'links',
                'meter_links',
                'display_name',
                'project_id',
                'resource_id',
                'namespace',
                'deleted',
            )
            data = monitoring_utils._format_links_resource(data)

            return (columns,
                    (monitoring_utils.get_dict_properties
                         (
                         s._info, columns,
                         formatters={
                             'links': monitoring_utils._format_links,
                             'meter_links': monitoring_utils._format_links,
                         }
                     ) for s in data
                     )
                    )

        columns = (
            'links',
            'display_name',
            'project_id',
            'resource_id',
            'namespace',
            'deleted',
        )
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={
                        'links':monitoring_utils._format_links
                    }
                ) for s in data))

class ShowResource(command.ShowOne):
    """Show details of the specified resource."""

    def get_parser(self, prog_name):
        parser = super(ShowResource, self).get_parser(prog_name)
        parser.add_argument(
            "resource",
            metavar="<resource>",
            help="ID of target resource",
        )
        return parser

    def take_action(self, parsed_args):
        monitoring_client = self.app.client_manager.monitoring
        data = monitoring_client.resources.get(parsed_args.resource)
        columns = (
            "deleted",
            "display_name",
            "links",
            "namespace",
            "project_id",
            "resource_id",
        )
        return (columns,
                utils.get_item_properties(
                    data, columns,
                    formatters={
                        'links':monitoring_utils._format_links
                    }
                ))