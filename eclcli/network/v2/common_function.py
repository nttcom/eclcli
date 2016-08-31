from eclcli.common import command
from eclcli.common import utils
from ..networkclient.common import utils as to_obj


class ListCommonFunction(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListCommonFunction, self).get_parser(prog_name)
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

        data = [to_obj.CommonFunction(cfp)
            for cfp in network_client.list_common_functions().get('common_functions')]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowCommonFunction(command.ShowOne):
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
