import json


from eclcli.common import command
from eclcli.bare import bare_utils
from eclcli.common import utils


class ShowUEFI(command.ShowOne):
    """Show UEFI details for a server"""

    def get_parser(self, prog_name):
        parser = super(ShowUEFI, self).get_parser(prog_name)
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
            'Flavor ID',
            'Flavor Name',
            'Message',
            'Setting',
            'Updated',
            'Status',
        )

        server_obj = utils.find_resource(bare_client.servers,parsed_args.server)
        data = bare_client.uefis.get(server_obj.id)

        return columns,utils.get_item_properties(
                data,
                columns,
                mixed_case_fields=[],
                formatters={
                    'Setting': bare_utils._format_dicts_list_generic
                }
                )

class UpdateUEFI(command.ShowOne):
    """Update UEFI settings for a server"""

    def get_parser(self, prog_name):
        parser = super(UpdateUEFI, self).get_parser(prog_name)
        parser.add_argument(
            "server",
            metavar="<server>",
            help="Name or ID of server",
        )
        parser.add_argument(
            "--settings",
            metavar="<settings>",
            help="Dict object of settings to update. eg. {\"hoge\": {\"value\": \"Disabled\"}, \"fuga\": {\"value\": \"Enabled\"}}",
        )
        return parser

    def take_action(self, parsed_args):
        bare_client = self.app.client_manager.bare
        identity_client = self.app.client_manager.identity

        body = {"uefi": {"setting" :{}}}
        if parsed_args.settings:
            body['uefi']['settings'] = json.loads(parsed_args.settings)

        server_obj = utils.find_resource(bare_client.servers,parsed_args.server)
        bare_client.uefis.update(server_obj.id,body)
        return {},{}
