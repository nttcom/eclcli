from eclcli.common import command
from eclcli.common import utils
from eclcli.i18n import _  # noqa
 
 
class ListLicense(command.Lister):
    _description = _("List licenses of dedicated hypervisor")
 
    def get_parser(self, prog_name):
        parser = super(ListLicense, self).get_parser(prog_name)

        parser.add_argument(
            "--license-type",
            help="License type name as string of which you want to list license",
            metavar='<license-type>'
        )

        return parser
 
    def take_action(self, parsed_args):
        dh_client = self.app.client_manager.dh

        search_opts = {
            "license_type": parsed_args.license_type
        }

        self.log.debug('search options: %s', search_opts)

        columns = [
             
            'ID', 'Key', 'Assigned From', 'Expires At', 'License Type', 
        ]

        column_headers = columns

        data = dh_client.licenses.list(search_opts=search_opts)
 
        return (column_headers,
                (utils.get_item_properties(
                    s, columns
                ) for s in data))


class ListLicenseType(command.Lister):
    _description = _("List license-types of dedicated hypervisor")
 
    def get_parser(self, prog_name):
        parser = super(ListLicenseType, self).get_parser(prog_name)
        return parser
 
    def take_action(self, parsed_args):
        dh_client = self.app.client_manager.dh

        columns = [
             
            'ID', 'Name', 'Has License Key', 'Unit', 'Description'
        ]
        
        column_headers = columns
 
        data = dh_client.licenses.list_license_types()
 
        return (column_headers,
                (utils.get_item_properties(
                    s, columns
                ) for s in data)) 


class CreateLicense(command.ShowOne):
    _description = _("Create new license of dedicated hypervisor")
 
    def get_parser(self, prog_name):
        parser = super(CreateLicense, self).get_parser(prog_name)

        parser.add_argument(
            "license_type",
            help="License type name as string of which you want to create license",
            metavar='<license-type>'
        )

        return parser
 
    def take_action(self, parsed_args):
        dh_client = self.app.client_manager.dh
        self.log.debug('license type: %s', parsed_args.license_type)

        rows = [
            "ID",
            "Key",
            "Assigned From",
            "Expires At",
            "License Type"
        ]
        row_headers = rows

        data = dh_client.licenses.create(license_type=parsed_args.license_type)

        return (row_headers,
                utils.get_item_properties(
                    data, rows
                    ))


class DeleteLicense(command.Command):
    _description = _("Delete license of dedicated hypervisor")
 
    def get_parser(self, prog_name):
        parser = super(DeleteLicense, self).get_parser(prog_name)

        parser.add_argument(
            "license_ids",
            nargs="+",
            help="IDs of licenses to be deleted",
            metavar='<license-ids>'
        )

        return parser
 
    def take_action(self, parsed_args):

        dh_client = self.app.client_manager.dh

        self.log.debug('license id: %s', parsed_args.license_ids)
        
        for license_id in parsed_args.license_ids:
            dh_client.licenses.delete(license_id)
