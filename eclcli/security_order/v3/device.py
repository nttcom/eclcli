# -*- coding: utf-8 -*-

from eclcli.common import command
from eclcli.common import utils


class CreateDevice(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(CreateDevice, self).get_parser(prog_name)
        parser.add_argument(
            "--operatingmode",
            metavar="<operatingmode>",
            help='Set "FW" or "UTM" to this value.',
            required=True,
            choices=["FW", "UTM"],
        )
        parser.add_argument(
            "--licensekind",
            metavar="<licensekind>",
            help='Set "02" or "08" as FW/UTM plan.',
            required=True,
            choices=["02", "08"],
        )
        parser.add_argument(
            "--azgroup",
            metavar="<azgroup>",
            help="Availability Zone.",
            required=True,
        )
        parser.add_argument(
            "--locale",
            metavar="<locale>",
            help='Messages are displayed in Japanese or English '
                 'depending on this value. ja: Japanese, en: English. '
                 'Default value is "en".',
            choices=["ja", "en"],
        )

        return parser

    def take_action(self, parsed_args):
        security_order_client = self.app.eclsdk.conn.security_order

        kwargs = {
            'operatingmode': parsed_args.operatingmode,
            'licensekind': parsed_args.licensekind,
            'azgroup': parsed_args.azgroup,
            'locale': parsed_args.locale,
        }

        columns = [
            'code',
            'message',
            'soId',
            'status',
        ]

        status = security_order_client.create_device(**kwargs)

        return (columns, utils.get_item_properties(status, columns))


class UpdateDevice(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(UpdateDevice, self).get_parser(prog_name)
        parser.add_argument(
            "hostname",
            metavar="<hostname>",
            help="Set the hostname.",
        )
        parser.add_argument(
            "--operatingmode",
            metavar="<operatingmode>",
            help='Set "FW" or "UTM" to this value.',
            required=True,
            choices=["FW", "UTM"],
        )
        parser.add_argument(
            "--licensekind",
            metavar="<licensekind>",
            help='Set "02" or "08" as FW/UTM plan.',
            required=True,
            choices=["02", "08"],
        )
        parser.add_argument(
            "--locale",
            metavar="<locale>",
            help='Messages are displayed in Japanese or English '
                 'depending on this value. ja: Japanese, en: English. '
                 'Default value is "en".',
            choices=["ja", "en"],
        )

        return parser

    def take_action(self, parsed_args):
        security_order_client = self.app.eclsdk.conn.security_order

        kwargs = {
            'hostname': parsed_args.hostname,
            'operatingmode': parsed_args.operatingmode,
            'licensekind': parsed_args.licensekind,
            'locale': parsed_args.locale,
        }

        columns = [
            'code',
            'message',
            'soId',
            'status',
        ]

        status = security_order_client.update_device(**kwargs)

        return (columns, utils.get_item_properties(status, columns))


class DeleteDevice(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(DeleteDevice, self).get_parser(prog_name)
        parser.add_argument(
            "hostname",
            metavar="<hostname>",
            help="Set the hostname.",
        )
        parser.add_argument(
            "--locale",
            metavar="<locale>",
            help='Messages are displayed in Japanese or English '
                 'depending on this value. ja: Japanese, en: English. '
                 'Default value is "en".',
            choices=["ja", "en"],
        )

        return parser

    def take_action(self, parsed_args):
        security_order_client = self.app.eclsdk.conn.security_order

        kwargs = {
            'hostname': parsed_args.hostname,
            'locale': parsed_args.locale,
        }

        columns = [
            'code',
            'message',
            'soId',
            'status',
        ]

        status = security_order_client.delete_device(**kwargs)

        return (columns, utils.get_item_properties(status, columns))


class ShowStatus(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(ShowStatus, self).get_parser(prog_name)
        parser.add_argument(
            "soId",
            metavar="<soId>",
            help="This value is returned value of when you execute"
                 "Create Server, Update Server or Delete Server API.",
        )
        parser.add_argument(
            "--locale",
            metavar="<locale>",
            help='Messages are displayed in Japanese or English '
                 'depending on this value. ja: Japanese, en: English. '
                 'Default value is "en".',
            choices=["ja", "en"],
        )

        return parser

    def take_action(self, parsed_args):
        security_order_client = self.app.eclsdk.conn.security_order

        kwargs = {
            'soid': parsed_args.soId,
            'locale': parsed_args.locale,
        }

        columns = [
            'code',
            'message',
            'progress_rate',
            'status',
        ]

        status = security_order_client.get_device_order_status(**kwargs)

        return (columns, utils.get_item_properties(status, columns))


class ListDevices(command.Lister):
    def get_parser(self, prog_name):
        parser = super(ListDevices, self).get_parser(prog_name)
        parser.add_argument(
            "--locale",
            metavar="<locale>",
            help='Messages are displayed in Japanese or English '
                 'depending on this value. ja: Japanese, en: English. '
                 'Default value is "en".',
            choices=["ja", "en"],
        )

        return parser

    def take_action(self, parsed_args):
        security_order_client = self.app.eclsdk.conn.security_order

        columns = [
            'hostname',
            'availability_zone',
            'internal_use',
            'menu',
            'plan',
            'redundancy',
            'zone_name',
        ]

        devices = security_order_client.devices(parsed_args.locale)

        return (columns,
                (utils.get_dict_properties(
                    d, columns,
                ) for d in devices.devices))
