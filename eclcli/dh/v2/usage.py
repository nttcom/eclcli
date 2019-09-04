from eclcli.common import command
from eclcli.common import utils


class ListUsage(command.Lister):

    def get_parser(self, prog_name):
        parser = super(ListUsage, self).get_parser(prog_name)

        parser.add_argument(
            "--From",
            help="Date to list usage from",
            metavar='<from>'
        )

        parser.add_argument(
            "--to",
            help="Date to list usage upto. Month of the parameter should be same as 'from'",
            metavar='<to>'
        )

        parser.add_argument(
            "--license-type",
            help="Name of license type to list",
            metavar='<license-type>'
        )

        return parser

    def take_action(self, parsed_args):
        dh_client = self.app.client_manager.dh

        search_opts = {
            "from": parsed_args.From,
            "to": parsed_args.to,
            "license_type": parsed_args.license_type,
        }

        self.log.debug('search options: %s', search_opts)

        columns = [
            'ID', 'Type', 'Value', 'Unit', 'Name', 'Has License Key', 'Resource ID'
        ]

        column_headers = columns

        data = dh_client.usages.list(search_opts=search_opts)

        return (column_headers,
                (utils.get_item_properties(
                    s, columns
                ) for s in data))


class ShowUsageHistory(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(ShowUsageHistory, self).get_parser(prog_name)

        parser.add_argument(
            "usage",
            help="Usage id whose history to be shown",
            metavar='<usage>'
        )

        parser.add_argument(
            "--From",
            help="Date to list usage from",
            metavar='<from>'
        )

        parser.add_argument(
            "--to",
            help="Date to list usage upto. Month of the parameter should be same as 'from'",
            metavar='<to>'
        )

        return parser

    def take_action(self, parsed_args):
        dh_client = self.app.client_manager.dh

        search_opts = {
            "from": parsed_args.From,
            "to": parsed_args.to
        }

        self.log.debug('search options: %s', search_opts)

        rows = [
            'Tenant ID',
            'Unit',
            'Resource ID',
            'License Type',
            'Histories'
        ]

        row_headers = rows

        data = dh_client.usages.get_histories(search_opts=search_opts, usage=parsed_args.usage)

        return (row_headers, (utils.get_item_properties(
            data, rows
        )))
