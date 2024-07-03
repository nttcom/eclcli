from eclcli.common import command
from eclcli.common import utils


class ListUser(command.ShowOne):
    """List all users in a group"""

    def get_parser(self, prog_name):
        parser = super(ListUser, self).get_parser(prog_name)
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
            'iam_group_name',
            'iam_group_id',
            'description',
            'users',
        )

        column_headers = (
            'Group Name',
            'ID',
            'Description',
            'Users',
        )

        data = iam_client.iam_user_list(parsed_args.group)
        return (column_headers, utils.get_dict_properties(data, columns))
