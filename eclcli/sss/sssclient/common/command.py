from cliff import command


class OpenStackCommand(command.Command):
    """Base class for OpenStack commands."""

    api = None

    def run(self, parsed_args):
        if not self.api:
            return
        else:
            return super(OpenStackCommand, self).run(parsed_args)

    def get_data(self, parsed_args):
        pass

    def take_action(self, parsed_args):
        return self.get_data(parsed_args)
