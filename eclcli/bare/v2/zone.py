from eclcli.common import command
from eclcli.common import utils
from eclcli.bare import bare_utils


class ShowZone(command.Lister):
    """Show availability zone details"""

    def get_parser(self, prog_name):
        parser = super(ShowZone, self).get_parser(prog_name)

        return parser

    def take_action(self, parsed_args):
        bare_client = self.app.client_manager.bare

        data = bare_client.availability_zones.list()
        columns = (
            'zoneName',
            'zoneState',
            'hosts',
        )
        display_columns = (
            'Name',
            'State',
            'Hosts',
        )
        mixed_case_fields = ['zoneState', 'zoneName']
        return (display_columns,
                (utils.get_item_properties(
                    s, columns,
                    mixed_case_fields=mixed_case_fields,
                    formatters={
                        'zoneState': bare_utils._format_zone_state
                    },
                ) for s in data))
