from eclcli.common import command
from eclcli.common import utils
from eclcli.bare import bare_utils

class ListFlavor(command.Lister):
    """List all baremetal flavors"""

    def get_parser(self, prog_name):
        parser = super(ListFlavor, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        bare_client = self.app.client_manager.bare
        identity_client = self.app.client_manager.identity

        columns = (
            'ID',
            'Name',
            'Disk',
            'RAM',
            'vCPUs'
            )

        column_headers = (
            'ID',
            'Name',
            'Disk',
            'RAM',
            'VCPUs'
            )

        data = bare_client.flavors.list()
        return (column_headers,
            (utils.get_item_properties(
                s, columns) for s in data))


class ShowFlavor(command.ShowOne):
    """Show baremetal flavor's detail"""

    def get_parser(self, prog_name):
        parser = super(ShowFlavor, self).get_parser(prog_name)
        parser.add_argument(
            "flavor",
            metavar="<flavor>",
            help="Name or ID of flavor",
        )
        return parser

    def take_action(self, parsed_args):
        bare_client = self.app.client_manager.bare
        identity_client = self.app.client_manager.identity

        columns = (
            'ID',
            'Name',
            'Disk',
            'RAM',
            'vCPUs',
            'Links',
        )

        data = utils.find_resource(bare_client.flavors,parsed_args.flavor)

        return (columns,utils.get_item_properties
                (data, columns, mixed_case_fields = [],
                    formatters = {
                        'Links': bare_utils._format_dicts_list_generic
                    }
                ))
