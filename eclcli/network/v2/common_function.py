from eclcli.common import command
from eclcli.common import utils
from eclcli.i18n import _  # noqa
from ..networkclient.common import utils as to_obj


class ListCommonFunction(command.Lister):
    _description = _("List common-functions")
    def get_parser(self, prog_name):
        parser = super(ListCommonFunction, self).get_parser(prog_name)
        parser.add_argument(
            '--description',
            metavar="description",
            help="filter by description")
        parser.add_argument(
            '--id',
            metavar="id",
            help="filter by id")
        parser.add_argument(
            '--name',
            metavar="name",
            help="filter by name")
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        columns = (
            'id',
            'name',
            'status',
        )
        column_headers = (
            'ID',
            'Name',
            'Status',
        )

        search_opts = dict()
        if parsed_args.description:
            search_opts.update({"description": parsed_args.description})
        if parsed_args.id:
            search_opts.update({"id": parsed_args.id})
        if parsed_args.name:
            search_opts.update({"name": parsed_args.name})

        data = [to_obj.CommonFunction(cfp)
                for cfp in network_client.list_common_functions(
                    **search_opts).get('common_functions')]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowCommonFunction(command.ShowOne):
    _description = _("Show common-function")
    def get_parser(self, prog_name):
        parser = super(ShowCommonFunction, self).get_parser(prog_name)
        parser.add_argument(
            'common_function_id',
            metavar="COMMON_FUNCTION_ID",
            help="ID of Common Function to show."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        common_function_id = parsed_args.common_function_id

        dic = network_client.show_common_function(common_function_id).get('common_function')
        columns = utils.get_columns(dic)
        obj = to_obj.CommonFunction(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data
