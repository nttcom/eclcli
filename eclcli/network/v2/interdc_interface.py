from eclcli.common import command
from eclcli.common import utils
from eclcli.i18n import _  # noqa
from ..networkclient.common import utils as to_obj


class ListInterDCInterface(command.Lister):
    _description = _("List interdc-interfaces")
    def get_parser(self, prog_name):
        parser = super(ListInterDCInterface, self).get_parser(prog_name)

        parser.add_argument(
            '--description',
            metavar="description",
            help="filter by description")
        parser.add_argument(
            '--gw_vipv4',
            metavar="gw_vipv4",
            help="filter by gateway ipv4")
        parser.add_argument(
            '--gw_vipv6',
            metavar="gw_vipv6",
            help="filter by gateway ipv6")
        parser.add_argument(
            '--id',
            metavar="id",
            help="filter by id")
        parser.add_argument(
            '--interdc_gw_id',
            metavar="interdc_gw_id",
            help="filter by internet gateway id")
        parser.add_argument(
            '--name',
            metavar="name",
            help="filter by name")
        parser.add_argument(
            '--netmask',
            metavar="netmask",
            help="filter by netmask")
        parser.add_argument(
            '--primary_ipv4',
            metavar="primary_ipv4",
            help="filter by primary ipv4")
        parser.add_argument(
            '--primary_ipv6',
            metavar="primary_ipv6",
            help="filter by primary ipv6")
        parser.add_argument(
            '--secondary_ipv4',
            metavar="secondary_ipv4",
            help="filter by secondary ipv4")
        parser.add_argument(
            '--secondary_ipv6',
            metavar="secondary_ipv6",
            help="filter by secondary ipv6")
        parser.add_argument(
            '--status',
            metavar="status",
            help="filter by status")
        parser.add_argument(
            '--vrid',
            metavar="vrid",
            help="filter by vrid")
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

        search_opts = {}
        if parsed_args.description:
            search_opts.update({"description": parsed_args.description})
        if parsed_args.gw_vipv4:
            search_opts.update({"gw_vipv4": parsed_args.gw_vipv4})
        if parsed_args.gw_vipv6:
            search_opts.update({"gw_vipv6": parsed_args.gw_vipv6})
        if parsed_args.id:
            search_opts.update({"id": parsed_args.id})
        if parsed_args.interdc_gw_id:
            search_opts.update({"interdc_gw_id": parsed_args.interdc_gw_id})
        if parsed_args.name:
            search_opts.update({"name": parsed_args.name})
        if parsed_args.netmask:
            search_opts.update({"netmask": parsed_args.netmask})
        if parsed_args.primary_ipv4:
            search_opts.update({"primary_ipv4": parsed_args.primary_ipv4})
        if parsed_args.primary_ipv6:
            search_opts.update({"primary_ipv6": parsed_args.primary_ipv6})
        if parsed_args.secondary_ipv4:
            search_opts.update({"secondary_ipv4": parsed_args.secondary_ipv4})
        if parsed_args.secondary_ipv6:
            search_opts.update({"secondary_ipv6": parsed_args.secondary_ipv6})
        if parsed_args.status:
            search_opts.update({"status": parsed_args.status})
        if parsed_args.vrid:
            search_opts.update({"vrid": parsed_args.vrid})
        data = [
            to_obj.InterDCInterface(idcif)
            for idcif in network_client.list_interdc_interfaces(
                **search_opts).get('interdc_interfaces')
        ]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowInterDCInterface(command.ShowOne):
    _description = _("Show interdc-interface")
    def get_parser(self, prog_name):
        parser = super(ShowInterDCInterface, self).get_parser(prog_name)
        parser.add_argument(
            'interdc_interface_id',
            metavar="INTERDC_INTERFACE_ID",
            help="ID of Inter Data Center Interface to show."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        interdc_interface_id = parsed_args.interdc_interface_id

        dic = network_client.show_interdc_interface(interdc_interface_id).get('interdc_interface')
        columns = utils.get_columns(dic)
        obj = to_obj.InterDCInterface(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data


class CreateInterDCInterface(command.ShowOne):
    _description = _("Create new interdc-interface")
    def get_parser(self, prog_name):
        parser = super(CreateInterDCInterface, self).get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar='<string>',
            help='Name of InterDC interface to create.')
        parser.add_argument(
            '--description',
            metavar='<string>',
            help='Description of InterDC interface to create.')
        parser.add_argument(
            '--interdc_gw_id',
            metavar='INTERDC_GATEWAY_ID',
            required=True,
            help='InterDC Gateway ID of Gateway interface to create.')
        parser.add_argument(
            '--netmask',
            metavar='NETMASK',
            type=int,
            required=True,
            help='Netmask of Gateway interface to create.')
        parser.add_argument(
            '--primary_ipv4',
            metavar='<ipv4>',
            required=True,
            help='Primary IPv4 of Gateway interface to create.')
        parser.add_argument(
            '--secondary_ipv4',
            metavar='<ipv4>',
            required=True,
            help='Secondary IPv4 of Gateway interface to create.')
        parser.add_argument(
            '--gw_vipv4',
            metavar='<ipv4>',
            required=True,
            help='Secondary IPv4 of Gateway interface to create.')
        parser.add_argument(
            '--vrid',
            metavar='VRID',
            type=int,
            required=True,
            help='VRRP ID of InterDC interface to create.')
        parser.add_argument(
            '--primary_ipv6',
            metavar='<ipv6>',
            help='Primary IPv6 of Gateway interface to create.')
        parser.add_argument(
            '--secondary_ipv6',
            metavar='<ipv6>',
            help='Secondary IPv6 of Gateway interface to create.')
        parser.add_argument(
            '--gw_vipv6',
            metavar='<ipv6>',
            help='Secondary IPv6 of Gateway interface to create.')
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        body = {'interdc_interface': {}}
        utils.update_dict(
            parsed_args,
            body['interdc_interface'],
            ['name', 'description', 'netmask',
             'vrid', 'interdc_gw_id',
             'primary_ipv4', 'secondary_ipv4', 'gw_vipv4',
             'primary_ipv6', 'secondary_ipv6', 'gw_vipv6'])

        dic = network_client.create_interdc_interface(body).get('interdc_interface')
        columns = utils.get_columns(dic)
        obj = to_obj.InterDCInterface(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data


class SetInterDCInterface(command.ShowOne):
    _description = _("Update interdc-interface")
    def get_parser(self, prog_name):
        parser = super(SetInterDCInterface, self).get_parser(prog_name)
        parser.add_argument(
            'interdc_interface_id',
            metavar='<string>',
            help='ID of InterDC Interface to update.')
        parser.add_argument(
            '--name',
            metavar='<string>',
            help='Name of InterDC interface to update.')
        parser.add_argument(
            '--description',
            metavar='<string>',
            help='Description of InterDC interface to update.')
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        body = {'interdc_interface': {}}
        interdc_interface_id = parsed_args.interdc_interface_id
        utils.update_dict(
            parsed_args,
            body['interdc_interface'],
            ['name', 'description'])

        dic = network_client.update_interdc_interface(
            interdc_interface_id, body=body).get('interdc_interface')
        columns = utils.get_columns(dic)
        obj = to_obj.InterDCInterface(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data


class DeleteInterDCInterface(command.Command):
    _description = _("Delete interdc-interface")
    def get_parser(self, prog_name):
        parser = super(DeleteInterDCInterface, self).get_parser(prog_name)
        parser.add_argument(
            'interdc_interface_id',
            metavar="<uuid>",
            nargs="+",
            help="ID(s) of InterDC Interface to delete."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        for idcif_id in parsed_args.interdc_interface_id:
            network_client.delete_interdc_interface(idcif_id)
