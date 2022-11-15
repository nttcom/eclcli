# -*- coding: utf-8 -*-
import base64

try:
    import json
except ImportError:
    import simplejson as json

import copy
import json_merge_patch as jmp
from eclcli.common import command, exceptions, utils
from eclcli.i18n import _  # noqa

ROWS_FOR_SHOW = [
    'ID',
    'Name',
    'Description',
    'Tags',
    'Tenant ID',
    'CA Cert Status',
    'SSL Cert Status',
    'SSL Key Status',
]


class ListCertificate(command.Lister):

    def get_parser(self, prog_name):
        parser = super(ListCertificate, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        columns = [
            'ID',
            'Name',
            'Description',
            'Tags',
            'CA Cert Status',
            'SSL Cert Status',
            'SSL Key Status',
        ]
        column_headers = copy.deepcopy(columns)

        data = client.certificates()

        column_values = []
        for s in data:
            _set_statuses_for_display(s)
            column_values.append(utils.get_item_properties(
                s, columns,
                formatters={'Metadata': utils.format_dict},
            ))

        return column_headers, column_values


class ShowCertificate(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(ShowCertificate, self).\
            get_parser(prog_name)
        parser.add_argument(
            'certificate',
            metavar='<certificate-id>',
            help='ID of certificate id to look up.')
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        rows = ROWS_FOR_SHOW
        row_headers = rows

        data = client.get_certificate(parsed_args.certificate)
        _set_statuses_for_display(data)

        return row_headers, (utils.get_item_properties(data, rows))


class CreateCertificate(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(CreateCertificate, self). \
            get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Name of certificate'),
        )

        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description of certificate'),
        )

        parser.add_argument(
            "--tags",
            help="Tags of certificate"
                 " (e.g. '{\"tag1\": 1,\"tag2\": \"a\"...}' )",
            metavar='<string>'
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        rows = ROWS_FOR_SHOW
        row_headers = rows

        tags = parsed_args.tags or '{}'
        try:
            tags = json.loads(tags)
        except Exception:
            msg = _("You must specify JSON object format")
            raise exceptions.CommandError(msg)

        data = client.create_certificate(
            name=parsed_args.name,
            description=parsed_args.description,
            tags=tags,
        )

        _set_statuses_for_display(data)

        return row_headers, utils.get_item_properties(data, rows)


class DeleteCertificate(command.Command):

    def get_parser(self, prog_name):
        parser = super(DeleteCertificate, self). \
            get_parser(prog_name)
        parser.add_argument(
            "certificate",
            nargs="+",
            help="IDs of certificate to be deleted",
            metavar='<certificate-id>'
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna
        for certificate_id in parsed_args.certificate:
            client.delete_certificate(certificate_id)


class UpdateCertificate(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(UpdateCertificate, self). \
            get_parser(prog_name)
        parser.add_argument(
            "certificate",
            help="IDs of certificate to be deleted",
            metavar='<certificate-id>'
        )

        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Name of certificate'),
        )

        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description of certificate'),
        )

        parser.add_argument(
            "--tags",
            help="Tags of certificate"
                 " (e.g. '{\"tag1\": 1,\"tag2\": \"a\"...}' )",
            metavar='<string>'
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        rows = ROWS_FOR_SHOW
        row_headers = rows

        target = client.get_certificate(parsed_args.certificate)

        # serialize request parameter as JSON
        requested_param = {}
        if hasattr(parsed_args, 'name') and parsed_args.name is not None:
            requested_param['name'] = parsed_args.name
        if hasattr(parsed_args, 'description') and \
                parsed_args.description is not None:
            requested_param['description'] = parsed_args.description
        if hasattr(parsed_args, 'tags') and parsed_args.tags is not None:
            tags = parsed_args.tags or '{}'
            try:
                requested_param['tags'] = json.loads(tags)
            except Exception:
                msg = _("You must specify JSON object format")
                raise exceptions.CommandError(msg)

        # serialize current parameter as JSON
        current_param = {
            'name': target.name,
            'description': target.description,
            'tags': target.tags,
        }
        origin_param = copy.deepcopy(current_param)
        merged_param = jmp.merge(current_param, requested_param)
        patch = jmp.create_patch(origin_param, merged_param)

        if 'tags' in requested_param and requested_param['tags'] != target.tags:
            patch['tags'] = requested_param['tags']

        if not patch:
            msg = _('No change will be expected')
            raise exceptions.CommandError(msg)

        data = client.update_certificate(
            parsed_args.certificate, **patch)

        _set_statuses_for_display(data)

        return row_headers, utils.get_item_properties(data, rows)


class UploadCertificate(command.Command):

    def get_parser(self, prog_name):
        parser = super(UploadCertificate, self). \
            get_parser(prog_name)
        parser.add_argument(
            "certificate",
            help="IDs of certificate to be deleted",
            metavar='<certificate-id>'
        )

        parser.add_argument(
            '--type',
            metavar='<type>',
            required=True,
            choices=["ca-cert", "ssl-cert", "ssl-key"],
            help=_('Type of the certificate file to be uploaded'),
        )

        parser.add_argument(
            '--content',
            metavar='<description>',
            required=True,
            help=_('Content of the certificate file to be uploaded'),
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.eclsdk.conn.mvna

        content_path = parsed_args.content

        # encode content file to Base64
        certificate_content = None
        if content_path:
            try:
                with open(content_path, 'rb') as f:
                    certificate_content = base64.b64encode(f.read()).decode()
            except IOError as e:
                msg = "content file %s not found: %s"
                raise exceptions.CommandError(msg % (content_path, e))

        client.upload_certificate(
            parsed_args.certificate,
            certificate_type=parsed_args.type,
            certificate_content=certificate_content,
        )


def _set_statuses_for_display(data):
    ca_cert = data.ca_cert["status"]
    setattr(data, 'ca_cert_status', ca_cert)

    ssl_cert = data.ssl_cert["status"]
    setattr(data, 'ssl_cert_status', ssl_cert)

    ssl_key = data.ssl_key["status"]
    setattr(data, 'ssl_key_status', ssl_key)
