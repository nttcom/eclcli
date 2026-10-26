# -*- coding: utf-8 -*-

from eclcli.common import command
from eclcli.common import utils
from eclcli.i18n import _  # noqa


class CreateDevice(command.ShowOne):
    _description = _("Create new ha-device")
    def get_parser(self, prog_name):
        parser = super(CreateDevice, self).get_parser(prog_name)
        parser.add_argument(
            "--operatingmode",
            metavar="<operatingmode>",
            help='Set "UTM_HA" or "FW_HA" to this value.',
            required=True,
            choices=["UTM_HA", "FW_HA"],
        )
        parser.add_argument(
            "--licensekind",
            metavar="<licensekind>",
            help='Set "02" or "08" as Managed FW/UTM plan.',
            required=True,
            choices=["02", "08"],
        )
        parser.add_argument(
            "--azgroup1",
            metavar="<azgroup1>",
            help="Availability Zone.",
            required=True,
        )
        parser.add_argument(
            "--azgroup2",
            metavar="<azgroup2>",
            help="Availability Zone.",
            required=True,
        )
        parser.add_argument(
            "--halink1networkid",
            metavar="<halink1networkid>",
            help="Set the Network ID to be used for HA line.",
            required=True,
        )
        parser.add_argument(
            "--halink1subnetid",
            metavar="<halink1subnetid>",
            help="Set the Subnet ID to be used for HA line.",
            required=True,
        )
        parser.add_argument(
            "--halink1ipaddress1",
            metavar="<halink1ipaddress1>",
            help="Set value of IPv4.",
            required=True,
        )
        parser.add_argument(
            "--halink1ipaddress2",
            metavar="<halink1ipaddress2>",
            help="Set value of IPv4.",
            required=True,
        )
        parser.add_argument(
            "--halink2networkid",
            metavar="<halink2networkid>",
            help="Set the Network ID to be used for HA line.",
            required=True,
        )
        parser.add_argument(
            "--halink2subnetid",
            metavar="<halink2subnetid>",
            help="Set the Subnet ID to be used for HA line.",
            required=True,
        )
        parser.add_argument(
            "--halink2ipaddress1",
            metavar="<halink2ipaddress1>",
            help="Set value of IPv4.",
            required=True,
        )
        parser.add_argument(
            "--halink2ipaddress2",
            metavar="<halink2ipaddress2>",
            help="Set value of IPv4.",
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
            'azgroup1': parsed_args.azgroup1,
            'azgroup2': parsed_args.azgroup2,
            'halink1networkid': parsed_args.halink1networkid,
            'halink1subnetid': parsed_args.halink1subnetid,
            'halink1ipaddress1': parsed_args.halink1ipaddress1,
            'halink1ipaddress2': parsed_args.halink1ipaddress2,
            'halink2networkid': parsed_args.halink2networkid,
            'halink2subnetid': parsed_args.halink2subnetid,
            'halink2ipaddress1': parsed_args.halink2ipaddress1,
            'halink2ipaddress2': parsed_args.halink2ipaddress2,
            'locale': parsed_args.locale,
        }

        columns = [
            'code',
            'message',
            'soId',
            'status',
        ]

        status = security_order_client.create_ha_device(**kwargs)

        return (columns, utils.get_item_properties(status, columns))


class UpdateDevice(command.ShowOne):
    _description = _("Update ha-device")
    def get_parser(self, prog_name):
        parser = super(UpdateDevice, self).get_parser(prog_name)
        parser.add_argument(
            "hostname1",
            metavar="<hostname1>",
            help="Set the hostname.",
        )
        parser.add_argument(
            "hostname2",
            metavar="<hostname2>",
            help="Set the hostname.",
        )
        parser.add_argument(
            "--operatingmode",
            metavar="<operatingmode>",
            help='Set "UTM_HA" or "FW_HA" to this value.',
            required=True,
            choices=["UTM_HA", "FW_HA"],
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
            'hostname1': parsed_args.hostname1,
            'hostname2': parsed_args.hostname2,
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

        status = security_order_client.update_ha_device(**kwargs)

        return (columns, utils.get_item_properties(status, columns))


class DeleteDevice(command.ShowOne):
    _description = _("Delete ha-device")
    def get_parser(self, prog_name):
        parser = super(DeleteDevice, self).get_parser(prog_name)
        parser.add_argument(
            "hostname1",
            metavar="<hostname1>",
            help="Set the hostname.",
        )
        parser.add_argument(
            "hostname2",
            metavar="<hostname2>",
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
            'hostname1': parsed_args.hostname1,
            'hostname2': parsed_args.hostname2,
            'locale': parsed_args.locale,
        }

        columns = [
            'code',
            'message',
            'soId',
            'status',
        ]

        status = security_order_client.delete_ha_device(**kwargs)

        return (columns, utils.get_item_properties(status, columns))


class ShowStatus(command.ShowOne):
    _description = _("Status ha-device show")
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
    _description = _("List ha-devices")
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
            'ha_id',
            'availability_zone',
            'internal_use',
            'menu',
            'plan',
            'redundancy',
            'zone_name',
            'halink1networkid',
            'halink1subnetid',
            'halink1ipaddress',
            'halink2networkid',
            'halink2subnetid',
            'halink2ipaddress',
        ]

        devices = security_order_client.ha_devices(parsed_args.locale)

        return (columns,
                (utils.get_dict_properties(
                    d, columns,
                ) for d in devices.devices))
