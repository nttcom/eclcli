# -*- coding: utf-8 -*-

try:
    import json
except ImportError:
    import simplejson as json

import copy
from eclcli.common import command, utils
from eclcli.i18n import _  # noqa


class ListTlsPolicy(command.Lister):
    _description = _("List tls-policys of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(ListTlsPolicy, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        columns = [
            'ID',
            'Name',
            'Default',
        ]
        column_headers = copy.deepcopy(columns)

        data = client.tls_policies()

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={'Metadata': utils.format_dict},
                ) for s in data))


class ShowTlsPolicy(command.ShowOne):
    _description = _("Show tls-policy of managed load balancer")

    def get_parser(self, prog_name):
        parser = super(ShowTlsPolicy, self).\
            get_parser(prog_name)
        parser.add_argument(
            'tls_policy_id',
            metavar='<tls-policy-id>',
            help='ID of tls policy id to look up.')
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        rows = [
            'ID',
            'Name',
            'Default',
            'TLS Protocols',
            'TLS Ciphers',
        ]
        row_headers = rows

        data = client.get_tls_policy(
            parsed_args.tls_policy_id)

        tls_protocols = data.tls_protocols
        tls_protocols_json = json.dumps(tls_protocols, indent=2)
        setattr(data, 'tls_protocols', tls_protocols_json)

        tls_ciphers = data.tls_ciphers
        tls_ciphers_json = json.dumps(tls_ciphers, indent=2)
        setattr(data, 'tls_ciphers', tls_ciphers_json)

        return row_headers, (utils.get_item_properties(data, rows))
