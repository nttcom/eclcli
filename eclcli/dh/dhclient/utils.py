import json
import re
import textwrap
import uuid

from oslo.serialization import jsonutils
from oslo.utils import encodeutils
import pkg_resources
import prettytable
import six

from . import exceptions
from .i18n import _
from .common import cliutils


VALID_KEY_REGEX = re.compile(r"[\w\.\- :]+$", re.UNICODE)


def add_resource_manager_extra_kwargs_hook(f, hook):
    """Add hook to bind CLI arguments to ResourceManager calls.

    The `do_foo` calls in shell.py will receive CLI args and then in turn pass
    them through to the ResourceManager. Before passing through the args, the
    hooks registered here will be called, giving us a chance to add extra
    kwargs (taken from the command-line) to what's passed to the
    ResourceManager.
    """
    if not hasattr(f, 'resource_manager_kwargs_hooks'):
        f.resource_manager_kwargs_hooks = []

    names = [h.__name__ for h in f.resource_manager_kwargs_hooks]
    if hook.__name__ not in names:
        f.resource_manager_kwargs_hooks.append(hook)


def get_resource_manager_extra_kwargs(f, args, allow_conflicts=False):
    """Return extra_kwargs by calling resource manager kwargs hooks."""
    hooks = getattr(f, "resource_manager_kwargs_hooks", [])
    extra_kwargs = {}
    for hook in hooks:
        hook_kwargs = hook(args)
        hook_name = hook.__name__
        conflicting_keys = set(hook_kwargs.keys()) & set(extra_kwargs.keys())
        if conflicting_keys and not allow_conflicts:
            msg = (_("Hook '%(hook_name)s' is attempting to redefine "
                     "attributes '%(conflicting_keys)s'") %
                   {'hook_name': hook_name,
                    'conflicting_keys': conflicting_keys})
            raise exceptions.NoUniqueMatch(msg)

        extra_kwargs.update(hook_kwargs)

    return extra_kwargs


def pretty_choice_dict(d):
    """Returns a formatted dict as 'key=value'."""
    return cliutils.pretty_choice_list(
        ['%s=%s' % (k, d[k]) for k in sorted(d.keys())])


def print_list(objs, fields, formatters={}, sortby_index=None):
    if sortby_index is None:
        sortby = None
    else:
        sortby = fields[sortby_index]
    mixed_case_fields = ['serverId']
    pt = prettytable.PrettyTable([f for f in fields], caching=False)
    pt.align = 'l'

    for o in objs:
        row = []
        for field in fields:
            if field in formatters:
                row.append(formatters[field](o))
            else:
                if field in mixed_case_fields:
                    field_name = field.replace(' ', '_')
                else:
                    field_name = field.lower().replace(' ', '_')
                data = getattr(o, field_name, '')
                if data is None:
                    data = '-'
                row.append(data)
        pt.add_row(row)

    if sortby is not None:
        result = encodeutils.safe_encode(pt.get_string(sortby=sortby))
    else:
        result = encodeutils.safe_encode(pt.get_string())

    if six.PY3:
        result = result.decode()

    print(result)


def _flatten(data, prefix=None):
    """Flatten a dict, using name as a prefix for the keys of dict.

    >>> _flatten('cpu_info', {'arch':'x86_64'})
    [('cpu_info_arch': 'x86_64')]

    """
    if isinstance(data, dict):
        for key, value in six.iteritems(data):
            new_key = '%s_%s' % (prefix, key) if prefix else key
            if isinstance(value, (dict, list)):
                for item in _flatten(value, new_key):
                    yield item
            else:
                yield new_key, value
    else:
        yield prefix, data


def flatten_dict(data):
    """Return a new dict whose sub-dicts have been merged into the
    original.  Each of the parents keys are prepended to the child's
    to prevent collisions.  Any string elements will be JSON parsed
    before flattening.

    >>> flatten_dict({'service': {'host':'cloud9@compute-068', 'id': 143}})
    {'service_host': colud9@compute-068', 'service_id': 143}

    """
    data = data.copy()
    # Try and decode any nested JSON structures.
    for key, value in six.iteritems(data):
        if isinstance(value, six.string_types):
            try:
                data[key] = json.loads(value)
            except ValueError:
                pass

    return dict(_flatten(data))


def print_dict(d, dict_property="Property", dict_value="Value", wrap=0):
    pt = prettytable.PrettyTable([dict_property, dict_value], caching=False)
    pt.align = 'l'
    for k, v in sorted(d.items()):
        # convert dict to str to check length
        if isinstance(v, (dict, list)):
            v = jsonutils.dumps(v)
        if wrap > 0:
            v = textwrap.fill(str(v), wrap)
        # if value has a newline, add in multiple rows
        # e.g. fault with stacktrace
        if v and isinstance(v, six.string_types) and r'\n' in v:
            lines = v.strip().split(r'\n')
            col1 = k
            for line in lines:
                pt.add_row([col1, line])
                col1 = ''
        else:
            if v is None:
                v = '-'
            pt.add_row([k, v])

    result = encodeutils.safe_encode(pt.get_string())

    if six.PY3:
        result = result.decode()

    print(result)


def find_resource(manager, name_or_id, **find_args):
    """Helper for the _find_* methods."""
    # for str id which is not uuid (for Flavor and Keypair search currently)
    if getattr(manager, 'is_alphanum_id_allowed', False):
        try:
            return manager.get(name_or_id)
        except exceptions.NotFound:
            pass

    # try to get entity as integer id
    try:
        return manager.get(int(name_or_id))
    except (TypeError, ValueError, exceptions.NotFound):
        pass

    # now try to get entity as uuid
    try:
        tmp_id = encodeutils.safe_encode(name_or_id)

        if six.PY3:
            tmp_id = tmp_id.decode()

        uuid.UUID(tmp_id)
        return manager.get(tmp_id)
    except (TypeError, ValueError, exceptions.NotFound):
        pass

    try:
        try:
            resource = getattr(manager, 'resource_class', None)
            name_attr = resource.NAME_ATTR if resource else 'name'
            kwargs = {name_attr: name_or_id}
            kwargs.update(find_args)
            return manager.find(**kwargs)
        except exceptions.NotFound:
            pass

        # finally try to find entity by human_id
        try:
            return manager.find(human_id=name_or_id, **find_args)
        except exceptions.NotFound:
            msg = (_("No %(class)s with a name or ID of '%(name)s' exists.") %
                   {'class': manager.resource_class.__name__.lower(),
                    'name': name_or_id})
            raise exceptions.CommandError(msg)
    except exceptions.NoUniqueMatch:
        msg = (_("Multiple %(class)s matches found for '%(name)s', use an ID "
                 "to be more specific.") %
               {'class': manager.resource_class.__name__.lower(),
                'name': name_or_id})
        raise exceptions.CommandError(msg)


def _format_servers_list_networks(server):
    output = []
    for (network, addresses) in server.networks.items():
        if len(addresses) == 0:
            continue
        addresses_csv = ', '.join(addresses)
        group = "%s=%s" % (network, addresses_csv)
        output.append(group)

    return '; '.join(output)


def _format_security_groups(groups):
    return ', '.join(group['name'] for group in groups)


def _format_field_name(attr):
    """Format an object attribute in a human-friendly way."""
    # Split at ':' and leave the extension name as-is.
    parts = attr.rsplit(':', 1)
    name = parts[-1].replace('_', ' ')
    # Don't title() on mixed case
    if name.isupper() or name.islower():
        name = name.title()
    parts[-1] = name
    return ': '.join(parts)


def _make_field_formatter(attr, filters=None):
    """
    Given an object attribute, return a formatted field name and a
    formatter suitable for passing to print_list.

    Optionally pass a dict mapping attribute names to a function. The function
    will be passed the value of the attribute and should return the string to
    display.
    """
    filter_ = None
    if filters:
        filter_ = filters.get(attr)

    def get_field(obj):
        field = getattr(obj, attr, '')
        if field and filter_:
            field = filter_(field)
        return field

    name = _format_field_name(attr)
    formatter = get_field
    return name, formatter


def safe_issubclass(*args):
    """Like issubclass, but will just return False if not a class."""

    try:
        if issubclass(*args):
            return True
    except TypeError:
        pass

    return False


def do_action_on_many(action, resources, success_msg, error_msg):
    """Helper to run an action on many resources."""
    failure_flag = False

    for resource in resources:
        try:
            action(resource)
            print(success_msg % resource)
        except Exception as e:
            failure_flag = True
            print(e)

    if failure_flag:
        raise exceptions.CommandError(error_msg)


def _load_entry_point(ep_name, name=None):
    """Try to load the entry point ep_name that matches name."""
    for ep in pkg_resources.iter_entry_points(ep_name, name=name):
        try:
            return ep.load()
        except (ImportError, pkg_resources.UnknownExtra, AttributeError):
            continue


def is_integer_like(val):
    """Returns validation of a value as an integer."""
    try:
        int(val)
        return True
    except (TypeError, ValueError, AttributeError):
        return False


def validate_flavor_metadata_keys(keys):
    for key in keys:
        valid_name = VALID_KEY_REGEX.match(key)
        if not valid_name:
            msg = _('Invalid key: "%s". Keys may only contain letters, '
                    'numbers, spaces, underscores, periods, colons and '
                    'hyphens.')
            raise exceptions.CommandError(msg % key)
