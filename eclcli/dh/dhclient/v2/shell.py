from __future__ import print_function

import logging

from .. import exceptions
from ..i18n import _
from ..common import cliutils
from .. import utils

logger = logging.getLogger(__name__)


def do_server_list(cs, args):
    """List User Names for Inter Connect Gateway Service."""
    servers = cs.servers.list()
    columns = ["name", "vpn_endpoints"]
    utils.print_list(servers, columns)


@cliutils.arg(
    '--id',
    metavar='<uuid>',
    help="UUID for Inter Connect Gateway Service")
def do_server_show(cs, args):
    """Show User Detail for Inter Connect Gateway Service."""
    servers = []
    servers.append(cs.servers.get(args.id))
    columns = ["name", "description"]
    utils.print_list(servers, columns)


@cliutils.arg(
    'name',
    metavar='<name>',
    help="User Name for Inter Connect Gateway Service")
@cliutils.arg(
    'networks',
    metavar='<networks>',
    help="Networks for Inter Connect Gateway Service")
@cliutils.arg(
    'imageRef',
    metavar='<image>',
    help="Networks for Inter Connect Gateway Service")
@cliutils.arg(
    'flavorRef',
    metavar='<flavor>',
    help="Networks for Inter Connect Gateway Service")
@cliutils.arg(
    '--adminPass',
    metavar='<adminPass>',
    help="User Name for Inter Connect Gateway Service")
@cliutils.arg(
    '--metadata',
    metavar='<metadata>',
    help="User Name for Inter Connect Gateway Service")
@cliutils.arg(
    '--availability_zone',
    metavar='<az>',
    help="User Name for Inter Connect Gateway Service")
@cliutils.arg(
    '--description',
    metavar='<desc>',
    help="User Name for Inter Connect Gateway Service")
def do_server_create(cs, args):
    """Create User for Inter Connect Gateway Service."""
    servers = []
    kwargs = {}
    keys = ["name", "networks", "imageRef",
                "flavorRef", "adminPass", "metadata",
                "availability_zone", "description"]
    for k in keys:
        if hasattr(args, k):
            kwargs[k] = getattr(args, k, "")
    created = cs.servers.create(**kwargs)
    servers.append(created)
    columns = ["name", "description"]
    utils.print_list(servers, columns)


@cliutils.arg(
    'id',
    metavar='<name>',
    nargs='+',
    help="User Name for Inter Connect Gateway Service")
def do_server_delete(cs, args):
    """Delete User(s) from Inter Connect Gateway Service."""
    utils.do_action_on_many(cs.servers.delete,
        args.id,
        _("Request to delete server %s has been accepted."),
        _("Unable to delete the specified server(s)."))


def do_usage_list(cs, args):
    usages = cs.usages.list()
    columns = ["id"]
    utils.print_list(usages, columns)


@cliutils.arg(
    '--id',
    metavar='<uuid>',
    help="UUID for Usage")
def do_history_get(cs, args):
    histories = []
    histories.append(cs.usages.get_histories(args.id))
    columns = ["tenant_id", "histories"]
    utils.print_list(usages, columns)


def do_license_list(cs, args):
    licenses = cs.licenses.list()
    columns = ["id", "key", "license_type"]
    utils.print_list(licenses, columns)


def do_license_type_list(cs, args):
    license_types = cs.licenses.list_license_types()
    columns = ["id", "key", "license_type"]
    utils.print_list(license_types, columns)


# @cliutils.arg(
#     '--id',
#     metavar='<uuid>',
#     help="UUID for License")
# def do_license_show(cs, args):
#     licenses = []
#     licenses.append(cs.licenses.get(args.id))
#     columns = ["id", "key, license_type"]
#     utils.print_list(licenses, columns)


@cliutils.arg(
    '--license_type',
    metavar='<str>',
    help="Type")
def do_license_create(cs, args):
    licenses = []
    created = cs.licenses.create(getattr(args, "license_type", None))
    licenses.append(created)
    columns = ["id", "key, license_type"]
    utils.print_list(licenses, columns)


@cliutils.arg(
    '--id',
    metavar='<str>',
    nargs='+',
    help="License ID")
def do_license_delete(cs, args):
    utils.do_action_on_many(cs.licenses.delete,
        args.id,
        _("Request to delete license %s has been accepted."),
        _("Unable to delete the specified license(s)."))
