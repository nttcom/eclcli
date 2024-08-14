from eclcli.common import command
from eclcli.common import utils


class ListGroup(command.Lister):
    """List all groups"""

    def get_parser(self, prog_name):
        parser = super(ListGroup, self).get_parser(prog_name)
        parser.add_argument(
            "--contract-id",
            metavar="<contract-id>",
            help="Filter by contract ID",
        )
        return parser

    def take_action(self, parsed_args):
        iam_client = self.app.client_manager.sss
        identity_client = self.app.client_manager.identity

        columns = (
            'iam_group_name',
            'iam_group_id',
            'description',
            'iam_roles',
        )

        column_headers = (
            'Name',
            'ID',
            'Description',
            'Roles',
        )

        data = iam_client.iam_group_list(
            contract_id=parsed_args.contract_id)['iam_groups']
        return (column_headers, (utils.get_dict_properties(s, columns)
                                 for s in data))


class CreateGroup(command.ShowOne):
    """Create group"""

    def get_parser(self, prog_name):
        parser = super(CreateGroup, self).get_parser(prog_name)
        parser.add_argument(
            "name",
            metavar="<name>",
            help="Group name",
        )
        parser.add_argument(
            "--contract-id",
            metavar="<contract-id>",
            help="Contract ID",
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help="Group description",
        )
        return parser

    def take_action(self, parsed_args):
        iam_client = self.app.client_manager.sss
        identity_client = self.app.client_manager.identity

        columns = (
            'contract_id',
            'iam_group_id',
            'iam_group_name',
            'description'
        )
        column_headers = (
            'Contract ID',
            'ID',
            'Name',
            'Description'
        )
        data = iam_client.iam_group_create(contract_id=parsed_args.contract_id,
                                           iam_group_name=parsed_args.name,
                                           description=parsed_args.description)
        return (column_headers, utils.get_dict_properties(data, columns))


class DeleteGroup(command.ShowOne):
    """Delete group"""

    def get_parser(self, prog_name):
        parser = super(DeleteGroup, self).get_parser(prog_name)
        parser.add_argument(
            "group",
            metavar="<group>",
            help="Group ID",
        )
        return parser

    def take_action(self, parsed_args):
        iam_client = self.app.client_manager.sss
        identity_client = self.app.client_manager.identity

        data = iam_client.iam_group_delete(parsed_args.group)
        return {}, {}


class AttachUser(command.ShowOne):
    """Attach user to a group"""

    def get_parser(self, prog_name):
        parser = super(AttachUser, self).get_parser(prog_name)
        parser.add_argument(
            "user",
            metavar="<user>",
            help="User ID",
        )
        parser.add_argument(
            "group",
            metavar="<group>",
            help="Group ID",
        )
        return parser

    def take_action(self, parsed_args):
        iam_client = self.app.client_manager.sss
        identity_client = self.app.client_manager.identity

        columns = (
            'iam_group_id',
            'iam_group_name',
            'user_id',
        )
        column_headers = (
            'Group ID',
            'Group Name',
            'User ID',
        )

        data = iam_client.iam_group_attach_user(iam_group_id=parsed_args.group,
                                                iam_user_id=parsed_args.user)

        return (column_headers, utils.get_dict_properties(data, columns))


class DetachUser(command.ShowOne):
    """Detach user from a group"""

    def get_parser(self, prog_name):
        parser = super(DetachUser, self).get_parser(prog_name)
        parser.add_argument(
            "user",
            metavar="<user>",
            help="User ID",
        )
        parser.add_argument(
            "group",
            metavar="<group>",
            help="Group ID",
        )
        return parser

    def take_action(self, parsed_args):
        iam_client = self.app.client_manager.sss
        identity_client = self.app.client_manager.identity

        data = iam_client.iam_group_detach_user(iam_group_id=parsed_args.group,
                                                iam_user_id=parsed_args.user)
        return {}, {}


class AttachRole(command.ShowOne):
    """Attach role to a group"""

    def get_parser(self, prog_name):
        parser = super(AttachRole, self).get_parser(prog_name)
        parser.add_argument(
            "role",
            metavar="<role>",
            help="Role ID",
        )
        parser.add_argument(
            "group",
            metavar="<group>",
            help="Group ID",
        )
        return parser

    def take_action(self, parsed_args):
        iam_client = self.app.client_manager.sss
        identity_client = self.app.client_manager.identity

        columns = (
            'iam_group_id',
            'iam_group_name',
            'iam_role_id',
            'iam_role_name',
        )
        column_headers = (
            'Group ID',
            'Group Name',
            'Role ID',
            'Role Name',
        )

        data = iam_client.iam_group_attach_role(iam_group_id=parsed_args.group,
                                                iam_role_id=parsed_args.role)

        return (column_headers, utils.get_dict_properties(data, columns))


class DetachRole(command.ShowOne):
    """Detach role from a group"""

    def get_parser(self, prog_name):
        parser = super(DetachRole, self).get_parser(prog_name)
        parser.add_argument(
            "role",
            metavar="<role>",
            help="Role ID",
        )
        parser.add_argument(
            "group",
            metavar="<group>",
            help="Group ID",
        )
        return parser

    def take_action(self, parsed_args):
        iam_client = self.app.client_manager.sss
        identity_client = self.app.client_manager.identity

        data = iam_client.iam_group_detach_role(iam_group_id=parsed_args.group,
                                                iam_role_id=parsed_args.role)

        return {}, {}
