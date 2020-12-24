from eclcli.common import command
from eclcli.common import utils


class CreateKeypair(command.ShowOne):
    """Create/Import keypair with/without a SSH public key"""

    def get_parser(self, prog_name):
        parser = super(CreateKeypair, self).get_parser(prog_name)
        parser.add_argument(
            "keypair",
            metavar="<keypair>",
            help="keypair name",
        )
        parser.add_argument(
            "--public-key",
            metavar="<public-key>",
            help="public key to import",
        )
        return parser

    def take_action(self, parsed_args):
        bare_client = self.app.client_manager.bare
        if parsed_args.public_key:
            columns = (
                'Name',
                'Fingerprint',
                'Public key',
            )

            data = bare_client.keypairs.create(
                parsed_args.keypair,
                parsed_args.public_key)

        else:
            columns = (
                'Name',
                'Fingerprint',
                'Public Key',
                'Private Key',
            )
            data = bare_client.keypairs.create(parsed_args.keypair)

        return columns, utils.get_item_properties(data, columns)


class DeleteKeypair(command.ShowOne):
    """Delete keypair"""

    def get_parser(self, prog_name):
        parser = super(DeleteKeypair, self).get_parser(prog_name)
        parser.add_argument(
            "keypair",
            metavar="<keypair>",
            help="Keypair name",
        )
        return parser

    def take_action(self, parsed_args):
        bare_client = self.app.client_manager.bare
        bare_client.keypairs.delete(parsed_args.keypair)
        return {}, {}


class ShowKeypair(command.ShowOne):
    """Show keypair's detail"""

    def get_parser(self, prog_name):
        parser = super(ShowKeypair, self).get_parser(prog_name)
        parser.add_argument(
            "keypair",
            metavar="<keypair>",
            help="Keypair name",
        )
        return parser

    def take_action(self, parsed_args):
        bare_client = self.app.client_manager.bare
        columns = (
            'Name',
            'Fingerprint',
            'Public Key',
        )

        data = utils.find_resource(bare_client.keypairs, parsed_args.keypair)
        return columns, utils.get_item_properties(data, columns)


class ListKeypair(command.Lister):
    """List all keypairs"""

    def get_parser(self, prog_name):
        parser = super(ListKeypair, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        bare_client = self.app.client_manager.bare
        columns = (
            'Name',
            'Fingerprint',
            'Public Key',
        )

        data = bare_client.keypairs.list()
        return (columns,
                (utils.get_item_properties(
                    s, columns) for s in data))
