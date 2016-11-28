from eclcli.common import command
from eclcli.bare import bare_utils
from eclcli.common import utils


class ListPort(command.Lister):
    """List all nic physical ports for a server"""

    def get_parser(self, prog_name):
        parser = super(ListPort, self).get_parser(prog_name)
        parser.add_argument(
            "server",
            metavar="<server>",
            help="Name or ID of server",
        )
        return parser

    def take_action(self, parsed_args):
        bare_client = self.app.client_manager.bare
        identity_client = self.app.client_manager.identity

        search_opts = {}
        self.log.debug('search options: %s', search_opts)

        columns = (
            'ID',
            'Mac Addr',
            'Network Physical Port ID',
            'Plane',
            'Hardware ID',
        )

        server_obj = utils.find_resource(bare_client.servers,parsed_args.server)
        data = bare_client.ports.list(server_obj.id)
        return (columns, (utils.get_item_properties(s,columns) for s in data))

class ShowPort(command.ShowOne):
    """Show nic physical port's detail for a server"""

    def get_parser(self, prog_name):
        parser = super(ShowPort, self).get_parser(prog_name)
        parser.add_argument(
            "server",
            metavar="<server>",
            help="Name or ID of server",
        )
        parser.add_argument(
            "port",
            metavar="<port>",
            help="Port ID",
        )
        return parser

    def take_action(self, parsed_args):
        bare_client = self.app.client_manager.bare
        identity_client = self.app.client_manager.identity

        server_obj = utils.find_resource(bare_client.servers,parsed_args.server)
        data = bare_client.ports.get(server_obj.id,parsed_args.port)
        columns = (
            'ID',
            'Mac Addr',
            'Network Physical Port ID',
            'Plane',
            'Attached Ports',
            'Hardware ID',
        )
        return columns, (utils.get_item_properties(
                        data,
                        columns,
                        mixed_case_fields=[],
                        formatters={
                            'Attached Ports':bare_utils._format_dicts_list_generic
                        }
                        ))
