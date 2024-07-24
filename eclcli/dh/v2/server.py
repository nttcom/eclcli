from eclcli.common import command, utils
from eclcli.i18n import _  # noqa


class ListServer(command.Lister):
    _description = _("List servers of dedicated hypervisor")

    def get_parser(self, prog_name):
        parser = super(ListServer, self).get_parser(prog_name)

        parser.add_argument(
            "--detail",
            help="Detailed view of server list",
            action='store_true',
        )
        parser.add_argument(
            "--changes-since",
            help="Filter by changes after a date",
            metavar='<changes-since>'
        )
        parser.add_argument(
            "--marker",
            help="List servers after the marker. Marker must be a server UUID",
            metavar='<marker>',
        )
        parser.add_argument(
            "--limit",
            help="Limit the list items",
            metavar='<limit>',
        )
        parser.add_argument(
            "--name",
            help="Filter by server name",
            metavar='<name>',
        )
        parser.add_argument(
            "--image",
            help="Filter by image in URL format",
            metavar='<image>',
        )
        parser.add_argument(
            "--flavor",
            help="Filter by flavor in URL format",
            metavar='<flavor>',
        )
        parser.add_argument(
            "--status",
            help="Filter by server status",
            metavar='<status>',
        )

        return parser

    def take_action(self, parsed_args):
        dh_client = self.app.client_manager.dh

        search_opts = {
            "changes-since": parsed_args.changes_since,
            "marker": parsed_args.marker,
            "limit": parsed_args.limit,
            "name": parsed_args.name,
            "image": parsed_args.image,
            "flavor": parsed_args.flavor,
            "status": parsed_args.status
        }
        self.log.debug('search options: %s', search_opts)

        if parsed_args.detail:
            columns = ['ID',
                       'Name',
                       'Status',
                       'Description',
                       'Hypervisor Type',
                       'imageRef',
                       'Baremetal Server'
                       ]

            column_headers = columns

        else:
            columns = ['ID',
                       'Name',
                       'Links']
            column_headers = columns

        mixed_case_fields = ['imageRef']

        data = dh_client.servers.list(search_opts=search_opts,
                                      detailed=parsed_args.detail)

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    mixed_case_fields=mixed_case_fields
                ) for s in data))


class ShowServer(command.ShowOne):
    _description = _("Show server of dedicated hypervisor")

    def get_parser(self, prog_name):
        parser = super(ShowServer, self).get_parser(prog_name)

        parser.add_argument(
            "server_id",
            help="ID of server to be shown",
            metavar='<server-id>'
        )

        return parser

    def take_action(self, parsed_args):
        dh_client = self.app.client_manager.dh

        self.log.debug('server-id: %s', parsed_args.server_id)

        rows = ['ID',
                'Name',
                'Status',
                'Description',
                'Hypervisor Type',
                'imageRef',
                'Baremetal Server'
                ]

        row_headers = rows

        mixed_case_fields = ['imageRef']

        data = dh_client.servers.get(server_id=parsed_args.server_id)

        return (row_headers, (utils.get_item_properties(
            data, rows, mixed_case_fields=mixed_case_fields
        )))


class CreateServer(command.ShowOne):
    _description = _("Create new server of dedicated hypervisor")

    def get_parser(self, prog_name):
        parser = super(CreateServer, self).get_parser(prog_name)

        parser.add_argument(
            "name",
            help="Server Name",
            metavar='<name>'
        )

        parser.add_argument(
            "--description",
            help="Server description",
            metavar='<description>'
        )

        parser.add_argument(
            "networks",
            help="Comma separated list of upto 2 Logical Network ID(s) "
                 "which belong to different plane(Data/Storage), "
                 "eg UUID1,UUID2",
            metavar='<networks>'
        )

        parser.add_argument(
            "--adminPass",
            help="Password for the administrator",
            metavar='<adminPass>'
        )

        parser.add_argument(
            "imageRef",
            help="Image ID",
            metavar='<imageRef>'
        )

        parser.add_argument(
            "flavorRef",
            help="Flavor ID",
            metavar='<flavorRef>'
        )

        parser.add_argument(
            "--availability_zone",
            help="The availability zone name in which to launch the server. "
                 "If omit this parameter, target availability zone is random",
            metavar='<availability-zone>'
        )

        parser.add_argument(
            "--metadata",
            help="Metadata key and value pairs. The maximum size of "
                 "the metadata key and value is 255 bytes each",
            metavar='<metadata>'
        )

        return parser

    def take_action(self, parsed_args):
        dh_client = self.app.client_manager.dh

        nics = []
        net_list = parsed_args.networks.split(",")
        for net in net_list:
            nics.append({"uuid": net})
            nics.append({"uuid": net})

        rows = [
            'ID',
            'Links',
            'adminPass'
        ]
        row_headers = rows

        mixed_case_fields = ['adminPass']

        data = dh_client.servers.create(
            name=parsed_args.name,
            networks=nics,
            image_id=parsed_args.imageRef,
            flavor_id=parsed_args.flavorRef,
            admin_pass=parsed_args.adminPass, metadata=parsed_args.metadata,
            availability_zone=parsed_args.availability_zone,
            description=parsed_args.description
        )

        return (row_headers,
                utils.get_item_properties(
                    data, rows, mixed_case_fields=mixed_case_fields
                ))


class DeleteServer(command.Command):
    _description = _("Delete server of dedicated hypervisor")

    def get_parser(self, prog_name):
        parser = super(DeleteServer, self).get_parser(prog_name)

        parser.add_argument(
            "server_ids",
            nargs="+",
            help="IDs of servers to be deleted",
            metavar='<server-ids>'
        )

        return parser

    def take_action(self, parsed_args):
        dh_client = self.app.client_manager.dh

        self.log.debug('server-ids: %s', parsed_args.server_ids)

        for server_id in parsed_args.server_ids:
            dh_client.servers.delete(server_id)
