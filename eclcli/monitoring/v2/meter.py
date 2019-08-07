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
import six
import datetime


class ListMeter(command.Lister):
    """List all metadata for server"""

    def get_parser(self, prog_name):
        parser = super(ListMeter, self).get_parser(prog_name)

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
            default="string"
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
            help="Number of meters contained in a page",
            default=100
        )

        return parser

    def take_action(self, parsed_args):
        q = monitoring_utils._make_query(parsed_args)

        monitoring_client = self.app.client_manager.monitoring
        data = monitoring_client.meters.list(
            q=q,
            page=parsed_args.page,
            per_page=parsed_args.per_page,
        )

        columns = (
            'meter_id',
            'name',
            'display_name',
            'project_id',
            'resource_id',
            'namespace',
            'type',
            'unit',
        )
        return (columns,
                (utils.get_item_properties(
                    s, columns) for s in data))


class ListMeterStatistics(command.Lister):
    """Computes and lists statistics for samples in a specified time range."""

    def get_parser(self, prog_name):
        parser = super(ListMeterStatistics, self).get_parser(prog_name)

        parser.add_argument(
            "meter_name",
            metavar="meter_name",
            help="Name of the meter",
        )
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
            "--period",
            metavar="<period>",
            help="The sampling period to compute statistic, in seconds",
            default=0
        )
        parser.add_argument(
            "--page",
            metavar="<page>",
            help="Target page number",
            default=1,
            type=int
        )
        parser.add_argument(
            "--per_page",
            metavar="<per_page>",
            help="Number of meters contained in a page",
            default=100,
            type=int,
        )

        return parser

    def take_action(self, parsed_args):
        q = monitoring_utils._make_query(parsed_args)
        if q is None:
            print("query required")
            return {}, {}

        monitoring_client = self.app.client_manager.monitoring
        data = monitoring_client.statistics.list(
            meter_name=parsed_args.meter_name,
            q=q,
            period=parsed_args.period,
            page=parsed_args.page,
            per_page=parsed_args.per_page,
        )

        columns = (
            'period',
            'period_start',
            'period_end',
            'duration',
            'duration_start',
            'duration_end',
            'sum',
            'count',
            'avg',
            'max',
            'min',
            'unit',
        )
        return (columns,
                (utils.get_item_properties(
                    s, columns) for s in data))


class CreateMeter(command.ShowOne):
    """Create a custom meter, and put a sample value into the specified custom meter"""

    def get_parser(self, prog_name):
        parser = super(CreateMeter, self).get_parser(prog_name)

        parser.add_argument(
            "custom_meter_name",
            metavar="custom_meter_name",
            help="authentication token",
        )
        parser.add_argument(
            "resource_id",
            metavar="resource_id",
            help="The unique ID of the metering resource to associate with the custom meter",
        )
        parser.add_argument(
            "--counter_name",
            metavar="counter_name",
            help="The name of the custom meter",
        )
        parser.add_argument(
            "--project_id",
            metavar="project_id",
            help="The unique ID of the project(tenant) which the resource and the custom meter are belonging to",
        )
        parser.add_argument(
            "--namespace",
            metavar="namespace",
            help="The namespace of the service",
        )
        parser.add_argument(
            "--counter_type",
            metavar="counter_type",
            help="The type of measurement associated with the custom meter",
            default="delta",
        )
        parser.add_argument(
            "--counter_unit",
            metavar="counter_unit",
            help="The unit of measurement associated with the custom meter",
            default=""
        )
        parser.add_argument(
            "--display_name",
            metavar="display_name",
            help="The friendly display name of the custom meter",
        )
        parser.add_argument(
            "--timestamp",
            metavar="timestamp",
            help="Arbitrary timestamp",
        )
        parser.add_argument(
            "--counter_volume",
            metavar="counter_volume",
            help="The sample value registered with the custom meter",
        )
        parser.add_argument(
            "--recorded_at",
            metavar="recorded_at",
            help="The datetime when the sample value was measured and recorded",
        )

        return parser

    def take_action(self, parsed_args):
        monitoring_client = self.app.client_manager.monitoring

        if not parsed_args.counter_name:
            parsed_args.counter_name = parsed_args.custom_meter_name

        if not parsed_args.display_name:
            parsed_args.display_name = parsed_args.counter_name

        if not parsed_args.recorded_at:
            parsed_args.recorded_at = datetime.datetime.now().isoformat()

        if not parsed_args.timestamp:
            timestamp = datetime.datetime.now().isoformat()

        data = monitoring_client.meters.create(
            custom_meter_name=parsed_args.custom_meter_name,
            project_id=parsed_args.project_id,
            namespace=parsed_args.namespace,
            resource_id=parsed_args.resource_id,
            counter_name=parsed_args.counter_name,
            counter_type=parsed_args.counter_type,
            counter_unit=parsed_args.counter_unit,
            display_name=parsed_args.display_name,
            timestamp=timestamp,
            counter_volume=parsed_args.counter_volume,
            recorded_at=parsed_args.recorded_at,
        )
        info = monitoring_utils._tidy_data_info(data._info)
        return zip(*sorted(six.iteritems(info)))
