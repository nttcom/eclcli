from eclcli.common import command
from eclcli.common import utils
from eclcli.i18n import _  # noqa
from ..networkclient.common import utils as to_obj


class ListPubicIP(command.Lister):
    _description = _("List public-ips")
    def get_parser(self, prog_name):
        parser = super(ListPubicIP, self).get_parser(prog_name)

        parser.add_argument(
            '--name',
            metavar="name",
            help="filter by name")
        parser.add_argument(
            '--id',
            metavar="id",
            help="filter by id")
        parser.add_argument(
            '--status',
            metavar="status",
            help="filter by status")
        parser.add_argument(
            '--internet_gw_id',
            metavar="internet_gw_id",
            help="filter by internet gateway id")
        parser.add_argument(
            '--submask_length',
            metavar="submask_length",
            help="filter by submask length")
        parser.add_argument(
            '--cidr',
            metavar="cidr",
            help="filter by cidr")

        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        columns = (
            'id',
            'name',
            'cidr',
            'submask_length',
            'status',
        )
        column_headers = (
            'ID',
            'Name',
            'CIDR',
            'Submask',
            'Status',
        )

        search_opts = {}
        if parsed_args.name:
            search_opts.update({"name": parsed_args.name})
        if parsed_args.id:
            search_opts.update({"id": parsed_args.id})
        if parsed_args.status:
            search_opts.update({"status": parsed_args.status})
        if parsed_args.internet_gw_id:
            search_opts.update({"internet_gw_id": parsed_args.internet_gw_id})
        if parsed_args.submask_length:
            search_opts.update({"submask_length": parsed_args.submask_length})
        if parsed_args.cidr:
            search_opts.update({"cidr": parsed_args.cidr})

        data = [to_obj.PubicIP(public_ip)
                for public_ip in network_client.list_public_ips(**search_opts).get('public_ips')]

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowPubicIP(command.ShowOne):
    _description = _("Show public-ip")
    def get_parser(self, prog_name):
        parser = super(ShowPubicIP, self).get_parser(prog_name)
        parser.add_argument(
            'public_ip_id',
            metavar="PUBLIC_IP_ID",
            help="ID of Pubic IP to show."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        public_ip_id = parsed_args.public_ip_id

        dic = network_client.show_public_ip(public_ip_id).get('public_ip')
        columns = utils.get_columns(dic)
        obj = to_obj.PubicIP(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data


class CreatePubicIP(command.ShowOne):
    _description = _("Create new public-ip")
    def get_parser(self, prog_name):
        parser = super(CreatePubicIP, self).get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar='<string>',
            help='Name of  public ip to create.')
        parser.add_argument(
            '--description',
            metavar='<string>',
            help='Description of  public ip to create.')
        parser.add_argument(
            '--internet_gw_id',
            metavar='INTERNET_GATEWAY_ID',
            required=True,
            help='Internet Gateway ID of public ip to create')
        parser.add_argument(
            '--submask_length',
            metavar='SUBNET_MASK_LENGTH',
            required=True,
            type=int,
            help='Submask length of  public ip to create.')
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        body = {'public_ip': {}}
        utils.update_dict(
            parsed_args,
            body['public_ip'],
            ['name', 'description',
             'internet_gw_id', 'submask_length'])

        dic = network_client.create_public_ip(body).get('public_ip')
        columns = utils.get_columns(dic)
        obj = to_obj.PubicIP(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data


class SetPubicIP(command.ShowOne):
    _description = _("Update public-ip")
    def get_parser(self, prog_name):
        parser = super(SetPubicIP, self).get_parser(prog_name)
        parser.add_argument(
            'public_ip_id',
            metavar='PUBLIC_IP_ID',
            help='ID of Public IP to update.')
        parser.add_argument(
            '--description',
            metavar='<string>',
            help='Description of public ip to update.')
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        body = {'public_ip': {}}
        public_ip_id = parsed_args.public_ip_id
        utils.update_dict(
            parsed_args,
            body['public_ip'],
            ['description', ])

        dic = network_client.update_public_ip(
            public_ip_id, body).get('public_ip')
        columns = utils.get_columns(dic)
        obj = to_obj.PubicIP(dic)
        data = utils.get_item_properties(
            obj, columns,)
        return columns, data


class DeletePubicIP(command.Command):
    _description = _("Delete public-ip")
    def get_parser(self, prog_name):
        parser = super(DeletePubicIP, self).get_parser(prog_name)
        parser.add_argument(
            'public_ip_id',
            metavar="PUBLIC_IP_ID",
            nargs="+",
            help="ID(s) of Public IP to delete."
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        for giid in parsed_args.public_ip_id:
            network_client.delete_public_ip(giid)
