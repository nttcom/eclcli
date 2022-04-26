# -*- coding: utf-8 -*-

from eclcli.common import command, utils
from ..sssclient.common.utils import objectify


class ListWorkspace(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListWorkspace, self).get_parser(prog_name)
        parser.add_argument(
            '--contract_id',
            metavar='<contract_id>',
            help='Contract ID of Workspace information to be acquired'
        )
        return parser

    def take_action(self, parsed_args):
        sss_client = self.app.client_manager.sss

        columns = (
            'workspace_id',
            'workspace_name',
            'description',
            'start_time',
        )
        column_headers = (
            'ID',
            'Name',
            'Description',
            'Start Time',
        )

        data = [objectify(workspace)
                for workspace in sss_client.list_workspaces(parsed_args.contract_id).get('workspaces')]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowWorkspace(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(ShowWorkspace, self).get_parser(prog_name)
        parser.add_argument(
            'workspace_id',
            metavar="<workspace_id>",
            help="ID of workspace to be shown"
        )
        return parser

    def take_action(self, parsed_args):
        sss_client = self.app.client_manager.sss
        workspace = sss_client.show_workspace(parsed_args.workspace_id)
        columns = utils.get_columns(workspace)
        obj = objectify(workspace)
        data = utils.get_item_properties(obj, columns)
        return columns, data


class CreateWorkspace(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(CreateWorkspace, self).get_parser(prog_name)
        parser.add_argument(
            'workspace_name',
            metavar='<workspace_name>',
            help="New workspace\'s name. This name need to be unique globally."
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help='Description for this workspace.'
        )
        parser.add_argument(
            '--contract_id',
            metavar='<contract_id>',
            help='The Contract ID where the workspace will be created.'
        )
        return parser

    def take_action(self, parsed_args):
        sss_client = self.app.client_manager.sss

        body = {}
        if parsed_args.workspace_name is not None:
            body['workspace_name'] = str(parsed_args.workspace_name)
        if parsed_args.description is not None:
            body['description'] = str(parsed_args.description)
        if parsed_args.contract_id is not None:
            body['contract_id'] = str(parsed_args.contract_id)

        workspace = sss_client.create_workspace(body)
        columns = utils.get_columns(workspace)
        obj = objectify(workspace)
        data = utils.get_item_properties(obj, columns)
        return columns, data


class SetWorkspace(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(SetWorkspace, self).get_parser(prog_name)
        parser.add_argument(
            'workspace_id',
            metavar="<workspace_id>",
            help="ID of workspace to be update"
        )
        parser.add_argument(
            'description',
            metavar='<description>',
            help="Description for this workspace."
        )
        return parser

    def take_action(self, parsed_args):
        sss_client = self.app.client_manager.sss

        body = {}
        if parsed_args.description is not None:
            body['description'] = str(parsed_args.description)

        sss_client.set_workspace(parsed_args.workspace_id, body)
        workspace = sss_client.show_workspace(parsed_args.workspace_id)
        columns = utils.get_columns(workspace)
        obj = objectify(workspace)
        data = utils.get_item_properties(obj, columns)
        return columns, data


class DeleteWorkspace(command.Command):
    def get_parser(self, prog_name):
        parser = super(DeleteWorkspace, self).get_parser(prog_name)
        parser.add_argument(
            'workspace_id',
            metavar="<workspace_id>",
            help="ID of workspace to be delete"
        )
        return parser

    def take_action(self, parsed_args):
        sss_client = self.app.client_manager.sss

        sss_client.delete_workspace(parsed_args.workspace_id)


class AddWorkspaceRoleAssignment(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(AddWorkspaceRoleAssignment, self).get_parser(prog_name)
        parser.add_argument(
            'workspace_id',
            metavar="<workspace_id>",
            help="Workspace ID for workspace role"
        )
        parser.add_argument(
            'user_id',
            metavar='<user_id>',
            help='User ID for workspace role'
        )

        return parser

    def take_action(self, parsed_args):
        sss_client = self.app.client_manager.sss

        body = {}
        if parsed_args.user_id is not None:
            body['user_id'] = str(parsed_args.user_id)
        if parsed_args.workspace_id is not None:
            body['workspace_id'] = str(parsed_args.workspace_id)

        workspace_role = sss_client.add_workspace_role_assignment(body)
        columns = utils.get_columns(workspace_role)
        obj = objectify(workspace_role)
        data = utils.get_item_properties(obj, columns)
        return columns, data


class DeleteWorkspaceRoleAssignment(command.Command):
    def get_parser(self, prog_name):
        parser = super(DeleteWorkspaceRoleAssignment, self).get_parser(prog_name)
        parser.add_argument(
            'workspace_id',
            metavar="<workspace_id>",
            help="Workspace ID for workspace role"
        )
        parser.add_argument(
            'user_id',
            metavar='<user_id>',
            help='User ID for workspace role'
        )
        return parser

    def take_action(self, parsed_args):
        sss_client = self.app.client_manager.sss

        sss_client.delete_workspace_role_assignment(parsed_args.workspace_id, parsed_args.user_id)
