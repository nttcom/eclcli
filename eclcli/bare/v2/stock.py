from eclcli.common import command
from eclcli.common import utils


class ShowStock(command.ShowOne):
    """Display flavor's stock details"""

    def get_parser(self, prog_name):
        parser = super(ShowStock, self).get_parser(prog_name)
        parser.add_argument(
            "flavor",
            metavar="<flavor>",
            help="Name or ID of flavor",
        )
        parser.add_argument(
            "--availability-zone",
            metavar="<availability-zone>",
            help="Filter by availability zone",
        )
        return parser

    def take_action(self, parsed_args):
        bare_client = self.app.client_manager.bare

        if parsed_args.availability_zone:
            columns = (
                'Flavor ID',
                'Availability Zone',
                'Stock')
        else:
            columns = (
                'Flavor ID',
                'Stock',
            )
        flavor_obj = utils.find_resource(bare_client.flavors, parsed_args.flavor)
        data = bare_client.stocks.get(flavor_obj.id, parsed_args.availability_zone)
        return columns, utils.get_item_properties(data, columns)
