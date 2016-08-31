from eclcli.common import command
from eclcli.common import utils
from ..networkclient.common import utils as to_obj


class ShowQuota(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(ShowQuota, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        dic = network_client.get_quotas_tenant().get('quota')
        columns = utils.get_columns(dic)
        obj = to_obj.Quota(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data
