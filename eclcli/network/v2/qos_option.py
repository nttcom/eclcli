from eclcli.common import command
from eclcli.common import utils
from ..networkclient.common import utils as to_obj


class ListQosOption(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListQosOption, self).get_parser(prog_name)
        parser.add_argument(
            '--service-type',
            metavar="service_type",
            help="filter by service_type: internet, vpn, interdc")
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network
        service_type = parsed_args.service_type
        columns = (
            'id',
            'name',
            'qos_type',
            'service_type',
            'status',
        )
        column_headers = (
            'ID',
            'Name',
            'QoS Type',
            'Service Type',
            'Status',
        )
        params = dict()
        if service_type:
            params.update({"service_type": service_type})

        data = [to_obj.QosOption(inetsv)
                for inetsv in network_client.list_qos_options(
                    **params).get('qos_options')]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowQosOption(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(ShowQosOption, self).get_parser(prog_name)
        parser.add_argument(
            'qos_option_id',
            metavar="QOS_OPTION_ID",
            help="ID of QoS Option to show."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        qos_id = parsed_args.qos_option_id

        dic = network_client.show_qos_option(qos_id).get('qos_option')
        columns = utils.get_columns(dic)
        obj = to_obj.QosOption(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data
