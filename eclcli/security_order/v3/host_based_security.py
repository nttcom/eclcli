# -*- coding: utf-8 -*-

from eclcli.common import command
from eclcli.common import utils


class OrderApp(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(OrderApp, self).get_parser(prog_name)
        parser.add_argument(
            "--service_order_service",
            metavar="<service_order_service>",
            help='"Requested menu. Set "Managed Anti-Virus", '
                 '"Managed Virtual Patch" or '
                 '"Managed Host-based Security Package" to this field.',
            required=True,
            choices=[
                "Managed Anti-Virus",
                "Managed Virtual Patch",
                "Managed Host-based Security Package",
            ],
        )
        parser.add_argument(
            "--max_agent_value",
            metavar="<max_agent_value>",
            help="Set maximum quantity of Agenet usage.",
            required=True,
            type=int,
        )
        parser.add_argument(
            "--mailaddress",
            metavar="<mailaddress>",
            help="Contactable mail address.",
            required=True,
        )
        parser.add_argument(
            "--dsm_lang",
            metavar="<dsm_lang>",
            help="This value is used for language of Deep Security Manager. "
                 "ja: Japanese, en: English.",
            required=True,
            choices=["ja", "en"],
        )
        parser.add_argument(
            "--time_zone",
            metavar="<time_zone>",
            help='Set "Asia/Tokyo" for JST or "Etc/GMT" for UTC.',
            required=True,
            choices=["Asia/Tokyo", "Etc/GMT"],
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
            'service_order_service': parsed_args.service_order_service,
            'max_agent_value': parsed_args.max_agent_value,
            'mailaddress': parsed_args.mailaddress,
            'dsm_lang': parsed_args.dsm_lang,
            'time_zone': parsed_args.time_zone,
            'locale': parsed_args.locale,
        }

        columns = [
            'code',
            'message',
            'soId',
            'status',
        ]

        status = security_order_client.order_hbs(**kwargs)

        return (columns, utils.get_item_properties(status, columns))


class ChangeAppMenu(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(ChangeAppMenu, self).get_parser(prog_name)
        parser.add_argument(
            "--service_order_service",
            metavar="<service_order_service>",
            help='"Requested menu. Set "Managed Anti-Virus", '
                 '"Managed Virtual Patch" or '
                 '"Managed Host-based Security Package" to this field.',
            required=True,
            choices=[
                "Managed Anti-Virus",
                "Managed Virtual Patch",
                "Managed Host-based Security Package",
            ],
        )
        parser.add_argument(
            "--mailaddress",
            metavar="<mailaddress>",
            help="Contactable mail address.",
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
            'service_order_service': parsed_args.service_order_service,
            'mailaddress': parsed_args.mailaddress,
            'locale': parsed_args.locale,
        }

        columns = [
            'code',
            'message',
            'soId',
            'status',
        ]

        status = security_order_client.change_hbs_menu(**kwargs)

        return (columns, utils.get_item_properties(status, columns))


class ChangeAppQuantity(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(ChangeAppQuantity, self).get_parser(prog_name)
        parser.add_argument(
            "--max_agent_value",
            metavar="<max_agent_value>",
            help="Set maximum quantity of Agenet usage.",
            required=True,
            type=int,
        )
        parser.add_argument(
            "--mailaddress",
            metavar="<mailaddress>",
            help="Contactable mail address.",
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
            'max_agent_value': parsed_args.max_agent_value,
            'mailaddress': parsed_args.mailaddress,
            'locale': parsed_args.locale,
        }

        columns = [
            'code',
            'message',
            'soId',
            'status',
        ]

        status = security_order_client.change_hbs_quantity(**kwargs)

        return (columns, utils.get_item_properties(status, columns))


class CancelApp(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(CancelApp, self).get_parser(prog_name)
        parser.add_argument(
            "--mailaddress",
            metavar="<mailaddress>",
            help="Contactable mail address.",
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
            'mailaddress': parsed_args.mailaddress,
            'locale': parsed_args.locale,
        }

        columns = [
            'code',
            'message',
            'soId',
            'status',
        ]

        status = security_order_client.cancel_hbs(**kwargs)

        return (columns, utils.get_item_properties(status, columns))


class ShowStatus(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(ShowStatus, self).get_parser(prog_name)
        parser.add_argument(
            "soId",
            metavar="<soId>",
            help="This value is returned value of when you execute API "
                 "of Order Host-based Security, Change menu or quantity, "
                 "or Cancel the order.",
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

        status = security_order_client.get_hbs_order_status(**kwargs)

        return (columns, utils.get_item_properties(status, columns))


class ShowInfo(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super(ShowInfo, self).get_parser(prog_name)
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
            'code',
            'message',
            'region',
            'tenant_name',
            'tenant_description',
            'contract_id',
            'service_order_service',
            'max_agent_value',
            'customer_name',
            'mailaddress',
            'dsm_lang',
            'tenant_flg',
            'status',
        ]

        info = security_order_client.get_hbs_order_info(parsed_args.locale)

        return (columns, utils.get_item_properties(info, columns))
