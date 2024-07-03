import json

from eclcli.common import command
from eclcli.common import utils


class ListRole(command.Lister):
    """List all roles"""

    def get_parser(self, prog_name):
        parser = super(ListRole, self).get_parser(prog_name)
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
            'iam_role_name',
            'iam_role_id',
            'description',
        )

        column_headers = (
            'Name',
            'ID',
            'Description',
        )

        data = iam_client.iam_role_list(
            contract_id=parsed_args.contract_id)['iam_roles']
        return (column_headers, (utils.get_dict_properties(s, columns)
                                 for s in data))


class ShowRole(command.ShowOne):
    """Show roles's detail"""

    def get_parser(self, prog_name):
        parser = super(ShowRole, self).get_parser(prog_name)
        parser.add_argument(
            "role",
            metavar="<role>",
            help="Role ID",
        )
        return parser

    def take_action(self, parsed_args):
        iam_client = self.app.client_manager.sss
        identity_client = self.app.client_manager.identity

        columns = (
            'iam_role_name',
            'iam_role_id',
            'description',
            'resources'
        )

        column_headers = (
            'Name',
            'ID',
            'Description',
            'Resources'
        )

        data = iam_client.iam_role_show(parsed_args.role)
        return (column_headers, utils.get_dict_properties(data, columns))


class CreateRole(command.ShowOne):
    """Create role"""

    def get_parser(self, prog_name):
        parser = super(CreateRole, self).get_parser(prog_name)
        parser.add_argument(
            "name",
            metavar="<name>",
            help="Group name",
        )
        parser.add_argument(
            "--resources",
            metavar="<resources>",
            help="Resources in comma separated JSON strings, eg '{\"key1\":\"value1\"},{\"key2\":\"value2\"}'",
            required=True,
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
            'iam_role_id',
            'iam_role_name',
            'description',
            'resources'
        )
        column_headers = (
            'Contract ID',
            'ID',
            'Name',
            'Description'
            'Resources'
        )

        if parsed_args.resources == "":
            resources_list = []
        else:
            resources_list = json.loads("[" + parsed_args.resources + "]")
        data = iam_client.iam_role_create(contract_id=parsed_args.contract_id,
                                          iam_role_name=parsed_args.name,
                                          description=parsed_args.description,
                                          resources=resources_list)

        return (column_headers, utils.get_dict_properties(data, columns))


class DeleteRole(command.ShowOne):
    """Delete role"""

    def get_parser(self, prog_name):
        parser = super(DeleteRole, self).get_parser(prog_name)
        parser.add_argument(
            "role",
            metavar="<role>",
            help="Role ID",
        )
        return parser

    def take_action(self, parsed_args):
        iam_client = self.app.client_manager.sss
        identity_client = self.app.client_manager.identity

        iam_client.iam_role_delete(parsed_args.role)
        return {}, {}
