import six

from eclcli.common import command, utils


class ListMetadata(command.ShowOne):
    """List all metadata for server"""

    def get_parser(self, prog_name):
        parser = super(ListMetadata, self).get_parser(prog_name)
        
        parser.add_argument(
            "server",
            metavar="<server>",
            help="Server ID",
        )
        return parser

    def take_action(self, parsed_args):
        bare_client = self.app.client_manager.bare
        server_obj = utils.find_resource(bare_client.servers, parsed_args.server)
        data = bare_client.metadata.list(server_obj.id)
        if len(data._info) == 0:
            return {}, {}
        else:
            return zip(*sorted(six.iteritems(data._info)))


class ShowMetadata(command.ShowOne):
    """Show metadata details for server"""

    def get_parser(self, prog_name):
        parser = super(ShowMetadata, self).get_parser(prog_name)
        parser.add_argument(
            "server",
            metavar="<server>",
            help="Server ID",
        )
        parser.add_argument(
            "key",
            metavar="<key>",
            help="Metadata key",
        )
        return parser

    def take_action(self, parsed_args):
        bare_client = self.app.client_manager.bare
        server_obj = utils.find_resource(bare_client.servers, parsed_args.server)
        data = bare_client.metadata.get(server_obj.id, parsed_args.key)
        return zip(*sorted(six.iteritems(data._info)))


class UpdateMetadata(command.ShowOne):
    """Update metadata details for a server"""

    def get_parser(self, prog_name):
        parser = super(UpdateMetadata, self).get_parser(prog_name)
        parser.add_argument(
            "server",
            metavar="<server>",
            help="Server ID",
        )
        parser.add_argument(
            "key",
            metavar="<key>",
            help="Metadata key",
        )
        parser.add_argument(
            "value",
            metavar="<value>",
            help="New value for the key",
        )
        return parser

    def take_action(self, parsed_args):
        bare_client = self.app.client_manager.bare
        server_obj = utils.find_resource(bare_client.servers, parsed_args.server)
        body = {'metadata': {}}
        body['metadata'][parsed_args.key] = parsed_args.value
        data = bare_client.metadata.update(server_obj.id, parsed_args.key, body)
        return zip(*sorted(six.iteritems(data._info)))


class MergeMetadata(command.ShowOne):
    """Merge new metadata into an existing one"""

    def get_parser(self, prog_name):
        parser = super(MergeMetadata, self).get_parser(prog_name)
        parser.add_argument(
            "server",
            metavar="<server>",
            help="Server ID",
        )
        parser.add_argument(
            "metadata",
            metavar="<metadata>",
            help="Comma separated key-value pairs, e.g. KEY1=VALUE1,KEY2=VALUE2",
        )
        return parser

    def take_action(self, parsed_args):
        bare_client = self.app.client_manager.bare
        server_obj = utils.find_resource(bare_client.servers, parsed_args.server)
        body = {'metadata': {}}
        body['metadata'] = dict((s.split('=')) for s in parsed_args.metadata.split(","))
        data = bare_client.metadata.merge(server_obj.id, body)
        return zip(*sorted(six.iteritems(data._info)))


class ReplaceMetadata(command.ShowOne):
    """Replace existing metadata with new one"""

    def get_parser(self, prog_name):
        parser = super(ReplaceMetadata, self).get_parser(prog_name)
        parser.add_argument(
            "server",
            metavar="<server>",
            help="Server ID",
        )
        parser.add_argument(
            "metadata",
            metavar="<metadata>",
            help="Comma separated key-value pairs, e.g. KEY1=VALUE1,KEY2=VALUE2",
        )
        return parser

    def take_action(self, parsed_args):
        bare_client = self.app.client_manager.bare
        server_obj = utils.find_resource(bare_client.servers, parsed_args.server)
        body = {'metadata': {}}
        body['metadata'] = dict((s.split('=')) for s in parsed_args.metadata.split(","))
        data = bare_client.metadata.replace(server_obj.id, body)
        return zip(*sorted(six.iteritems(data._info)))


class DeleteMetadata(command.ShowOne):
    """Delete metadata for a server"""

    def get_parser(self, prog_name):
        parser = super(DeleteMetadata, self).get_parser(prog_name)
        parser.add_argument(
            "server",
            metavar="<server>",
            help="Server ID",
        )
        parser.add_argument(
            "key",
            metavar="<key>",
            help="Metadata key",
        )
        return parser

    def take_action(self, parsed_args):
        bare_client = self.app.client_manager.bare
        server_obj = utils.find_resource(bare_client.servers, parsed_args.server)
        bare_client.metadata.delete(server_obj.id, parsed_args.key)
        return {}, {}
