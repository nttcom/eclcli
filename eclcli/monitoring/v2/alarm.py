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
from eclcli.common import exceptions
from eclcli.i18n import _  # noqa
from .. import monitoring_utils
import six


class CreateAlarm(command.ShowOne):
    _description = _("Create new alarm of monitoring")
    def get_parser(self, prog_name):
        """create an alarm"""

        parser = super(CreateAlarm, self).get_parser(prog_name)
        parser.add_argument(
            "name",
            metavar="<name>",
            help="The name for the alarm.")

        parser.add_argument(
            "--description",
            metavar="<description>",
            help="The description of the alarm")
        parser.add_argument(
            "--enabled",
            metavar="<enabled>",
            type=bool,
            help="Whether this alarm is enabled or not",
            default=True)
        parser.add_argument(
            "--state",
            metavar="<state>",
            help="The state of the alarm. Set 'ok' or 'alarm'",
            default='alarm'
        )
        parser.add_argument(
            "--repeat_actions",
            metavar="<repeat_actions>",
            default=False,
            type=bool,
            help="If set to true, the alarm notifications are repeated. Otherwise, this value is False.")
        parser.add_argument(
            "--severity",
            metavar="<severity>",
            help="The severity of the alarm. Set 'low', 'moderate', or 'critical'.",
            default="moderate")
        parser.add_argument(
            "--alarm_actions",
            metavar="<alarm_actions>",
            help="The actions to do when alarm state change to alarm")
        parser.add_argument(
            "--ok_actions",
            metavar="<ok_actions>",
            help="List of actions to do when alarm state change to ok",
        )
        parser.add_argument(
            "--type",
            metavar="<type>",
            help="Type specifier to select which rule to follow. Set 'threshold'",
            default="threshold"
        )
        parser.add_argument(
            "--project_id",
            metavar="<project_id>",
            help="Tenant that owns the alarm")
        parser.add_argument(
            "--user_id",
            metavar="<user_id>",
            help="User who created the alarm")

        # -----threshold_rules----- #
        parser.add_argument(
            "--meter_name",
            metavar="<meter_name>",
            help="")
        parser.add_argument(
            "--threshold",
            metavar="<threshold>",
            help="Describe when to trigger the alarm based on computed statistics",
            default=1
        )
        parser.add_argument(
            "--period",
            metavar="<period>",
            default=300,
            help="The time range in seconds over which query"
        )
        parser.add_argument(
            "--statistic",
            metavar="<statistic>",
            help="The statistic to compare to the threshold. Set 'max', 'min', 'avg', 'sum', or 'count'",
            default='max'
        )
        parser.add_argument(
            "--evaluation_periods",
            metavar="<evaluation_period>",
            default=1,
            help="The number of historical periods to evaluate the threshold"
        )
        parser.add_argument(
            "--comparison_operator",
            metavar="<comparison_operator>",
            help="The comparison against the alarm threshold. Set 'lt', 'le', 'eq', 'ne', 'ge', or 'gt'",
            default='gt'
        )

        # ---query--- #
        parser.add_argument(
            "--field",
            metavar="<field>",
            help="A meter column of retrieving target; Only equal operation allowed",
        )
        parser.add_argument(
            "--value",
            metavar="<value>",
            help="A field value for retrieving meters",
        )

        return parser

    def take_action(self, parsed_args):
        monitoring_client = self.app.client_manager.monitoring

        query = monitoring_utils._make_query(parsed_args)
        if parsed_args.enabled == "False" or parsed_args.enabled == "F":
            parsed_args.enabled = False
        else:
            parsed_args.enabled = True

        if parsed_args.repeat_actions == "True" or parsed_args.repeat_actions == "T":
            parsed_args.repeat_actions = True
        else:
            parsed_args.repeat_actions = False

        alarm_actions = None
        if parsed_args.alarm_actions:
            alarm_actions = parsed_args.alarm_actions.split(',')

        ok_actions = None
        if parsed_args.ok_actions:
            ok_actions = parsed_args.ok_actions.split(',')

        try:
            data = monitoring_client.alarms.create(
                name=parsed_args.name,
                description=parsed_args.description,
                enabled=parsed_args.enabled,
                state=parsed_args.state,
                repeat_actions=parsed_args.repeat_actions,
                severity=parsed_args.severity,
                alarm_actions=alarm_actions,
                ok_actions=ok_actions,
                type=parsed_args.type,
                project_id=parsed_args.project_id,
                user_id=parsed_args.user_id,
                meter_name=parsed_args.meter_name,
                threshold=parsed_args.threshold,
                period=parsed_args.period,
                statistic=parsed_args.statistic,
                evaluation_periods=parsed_args.evaluation_periods,
                comparison_operator=parsed_args.comparison_operator,
                query=query,
            )
            info = monitoring_utils._tidy_data_info(data._info)

        except exceptions.ClientException as cli_exp:
            info = {"message": cli_exp.message,
                    "details": cli_exp.details,
                    "code": cli_exp.code}

        return zip(*sorted(six.iteritems(info)))


class UpdateAlarm(command.ShowOne):
    _description = _("Update alarm of monitoring")
    def get_parser(self, prog_name):
        parser = super(UpdateAlarm, self).get_parser(prog_name)
        parser.add_argument(
            "alarm_id",
            metavar="<alarm_id>",
            help="ID for the alarm"
        )
        parser.add_argument(
            "--name",
            metavar="<name>",
            help="name for the alarm"
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help="The description of the alarm")
        parser.add_argument(
            "--enabled",
            metavar="<enabled>",
            type=bool,
            help="Whether this alarm is enabled or not",
            default=True)
        parser.add_argument(
            "--state",
            metavar="<state>",
            help="The state of the alarm. Set 'ok' or 'alarm'",
            default='alarm'
        )
        parser.add_argument(
            "--repeat_actions",
            metavar="<repeat_actions>",
            default=False,
            type=bool,
            help="If set to true, the alarm notifications are repeated. Otherwise, this value is False.")
        parser.add_argument(
            "--severity",
            metavar="<severity>",
            help="The severity of the alarm. Set 'low', 'moderate', or 'critical'.",
            default="moderate")
        parser.add_argument(
            "--alarm_actions",
            metavar="<alarm_actions>",
            help="The actions to do when alarm state change to alarm")
        parser.add_argument(
            "--ok_actions",
            metavar="<ok_actions>",
            help="List of actions to do when alarm state change to ok",
        )
        parser.add_argument(
            "--type",
            metavar="<type>",
            help="Type specifier to select which rule to follow. Set 'threshold'",
            default="threshold"
        )
        parser.add_argument(
            "--project_id",
            metavar="<project_id>",
            help="Tenant that owns the alarm")
        parser.add_argument(
            "--user_id",
            metavar="<user_id>",
            help="User who created the alarm")

        # -----threshold_rules-----#
        parser.add_argument(
            "--meter_name",
            metavar="<meter_name>",
            help="")
        parser.add_argument(
            "--threshold",
            metavar="<threshold>",
            help="Describe when to trigger the alarm based on computed statistics",
            default=1
        )
        parser.add_argument(
            "--period",
            metavar="<period>",
            default=300,
            help="The time range in seconds over which query"
        )
        parser.add_argument(
            "--statistic",
            metavar="<statistic>",
            help="The statistic to compare to the threshold. Set 'max', 'min', 'avg', 'sum', or 'count'",
            default='max'
        )
        parser.add_argument(
            "--evaluation_periods",
            metavar="<evaluation_period>",
            default=1,
            help="The number of historical periods to evaluate the threshold"
        )
        parser.add_argument(
            "--comparison_operator",
            metavar="<comparison_operator>",
            help="The comparison against the alarm threshold. Set 'lt', 'le', 'eq', 'ne', 'ge', or 'gt'",
            default='gt'
        )

        # ---query---#
        parser.add_argument(
            "--field",
            metavar="<field>",
            help="A meter column of retrieving target; Only equal operation allowed",
        )
        parser.add_argument(
            "--value",
            metavar="<value>",
            help="A field value for retrieving meters",
        )

        return parser

    def take_action(self, parsed_args):
        monitoring_client = self.app.client_manager.monitoring

        if parsed_args.field:
            query = monitoring_utils._make_query(parsed_args)
        else:
            query = None

        alarm_actions = None
        if parsed_args.alarm_actions:
            alarm_actions = parsed_args.alarm_actions.split(',')

        ok_actions = None
        if parsed_args.ok_actions:
            ok_actions = parsed_args.ok_actions.split(',')

        data = monitoring_client.alarms.update(
            alarm_id=parsed_args.alarm_id,
            name=parsed_args.name,
            description=parsed_args.description,
            enabled=parsed_args.enabled,
            state=parsed_args.state,
            repeat_actions=parsed_args.repeat_actions,
            severity=parsed_args.severity,
            alarm_actions=alarm_actions,
            ok_actions=ok_actions,
            type=parsed_args.type,
            project_id=parsed_args.project_id,
            user_id=parsed_args.user_id,
            meter_name=parsed_args.meter_name,
            threshold=parsed_args.threshold,
            period=parsed_args.period,
            statistic=parsed_args.statistic,
            evaluation_periods=parsed_args.evaluation_periods,
            comparison_operator=parsed_args.comparison_operator,
            query=query,
        )
        info = monitoring_utils._tidy_data_info(data._info)
        return zip(*sorted(six.iteritems(info)))


class DeleteAlarm(command.Command):
    """Delete an alarm"""

    def get_parser(self, prog_name):
        parser = super(DeleteAlarm, self).get_parser(prog_name)
        parser.add_argument(
            "alarm_id",
            metavar="<alarm_id>",
            help="Alarm to delete ID or name",
        )
        return parser

    def take_action(self, parsed_args):
        monitoring_client = self.app.client_manager.monitoring
        monitoring_client.alarms.delete(parsed_args.alarm_id)
        return


class ListAlarm(command.Lister):
    """Lists alarms, based on a query."""

    def get_parser(self, prog_name):
        parser = super(ListAlarm, self).get_parser(prog_name)

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
        parser.add_argument(
            "--detail",
            help="List all columns of alarms information",
            action='store_true'
        )

        return parser

    def take_action(self, parsed_args):
        q = monitoring_utils._make_query(parsed_args)
        monitoring_client = self.app.client_manager.monitoring
        data = monitoring_client.alarms.list(
            q=q,
            page=parsed_args.page,
            per_page=parsed_args.per_page,
        )
        if parsed_args.detail:
            columns = (
                'alarm_id',
                'project_id',
                'user_id',
                'name',
                'description',
                'enabled',
                'state',
                'repeat_actions',
                'severity',
                'alarm_actions',
                'ok_actions',
                'type',
                'threshold_rule',
                'timestamp',
                'state_timestamp',
                'resource_name',
                'deleted',
            )
            return (columns, (utils.get_item_properties(
                s, columns,
                formatters={
                    'threshold_rule': monitoring_utils._format_show_dicts_list,
                    'alarm_actions': monitoring_utils._format_show_dicts_list,
                    'ok_actions': monitoring_utils._format_show_dicts_list,
                }) for s in data))
        else:
            columns = (
                'alarm_id',
                'project_id',
                'user_id',
                'name',
                'description',
                'severity',
                'resource_name',
                'deleted',
            )
        return (columns, (utils.get_item_properties(
            s, columns) for s in data))


class ShowAlarmHistory(command.Lister):
    """Show the history for an alarm, by alarm ID"""

    def get_parser(self, prog_name):
        parser = super(ShowAlarmHistory, self).get_parser(prog_name)
        parser.add_argument(
            "alarm_id",
            metavar="<alarm_id>",
            help="ID of target alarm",
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
        return parser

    def take_action(self, parsed_args):
        q = monitoring_utils._make_query(parsed_args)
        monitoring_client = self.app.client_manager.monitoring

        data = monitoring_client.alarms.get_history(parsed_args.alarm_id, q)

        columns = (
            "alarm_id",
            "user_id",
            "project_id",
            "type",
            "detail",
            "timestamp",
            "on_behalf_of",
        )
        return (columns,
                (utils.get_item_properties(
                    s, columns) for s in data))


class ListOverallAlarmHistories(command.Lister):
    """Show the history for an alarm, by alarm ID"""

    def get_parser(self, prog_name):
        parser = super(ListOverallAlarmHistories, self).get_parser(prog_name)

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

        data = monitoring_client.alarms.list_history(q, parsed_args.page, parsed_args.per_page)

        columns = (
            "alarm_id",
            "user_id",
            "project_id",
            "type",
            "detail",
            "timestamp",
            "on_behalf_of",
        )
        return (columns,
                (utils.get_item_properties(
                    s, columns) for s in data))
