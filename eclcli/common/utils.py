import getpass
import ipaddress
import logging
import os
import re
import six
import time

try:
    from oslo_utils import importutils
except ImportError:
    from oslo.utils import importutils

from eclcli.common import exceptions


def find_resource(manager, name_or_id, **kwargs):
    try:
        if isinstance(name_or_id, int) or name_or_id.isdigit():
            return manager.get(int(name_or_id), **kwargs)
    except Exception as ex:
        if type(ex).__name__ == 'NotFound':
            pass
        else:
            raise

    try:
        return manager.get(name_or_id, **kwargs)
    except Exception:
        pass

    if len(kwargs) == 0:
        kwargs = {}

    try:
        if 'NAME_ATTR' in manager.resource_class.__dict__:
            kwargs[manager.resource_class.NAME_ATTR] = name_or_id
        else:
            kwargs['name'] = name_or_id
    except Exception:
        pass

    try:
        return manager.find(**kwargs)
    except Exception as ex:
        if type(ex).__name__ == 'NotFound':
            msg = "No %s with a name or ID of '%s' exists." % \
                (manager.resource_class.__name__.lower(), name_or_id)
            raise exceptions.CommandError(msg)
        if type(ex).__name__ == 'NoUniqueMatch':
            msg = "More than one %s exists with the name '%s'." % \
                (manager.resource_class.__name__.lower(), name_or_id)
            raise exceptions.CommandError(msg)
        else:
            pass

    try:
        for resource in manager.list():
            if (resource.get('id') == name_or_id or
                    resource.get('name') == name_or_id):
                return resource
        else:
            pass
    except Exception:
        pass

    msg = "Could not find resource %s" % name_or_id
    raise exceptions.CommandError(msg)


def format_dict(data):
    if data is None:
        return ""

    output = ""
    for s in sorted(data):
        output = output + s + "='" + six.text_type(data[s]) + "', "
    return output[:-2]


def format_list(data, separator=', '):
    return separator.join(sorted(data))


def format_lister(data, separator='\n'):
    return separator.join(sorted(data))


def format_list_of_dicts(data):
    return '\n'.join(format_dict(i) for i in data)


def get_field(item, field):
    try:
        if isinstance(item, dict):
            return item[field]
        else:
            return getattr(item, field)
    except Exception:
        msg = "Resource doesn't have field %s" % field
        raise exceptions.CommandError(msg)


def get_columns(item):
    columns = list(item.keys())
    if 'tenant_id' in columns:
        columns.remove('tenant_id')
        columns.append('project_id')
        item['project_id'] = item.pop('tenant_id')
    return tuple(sorted(columns))


def get_item_properties(item, fields, mixed_case_fields=None, formatters=None):
    if mixed_case_fields is None:
        mixed_case_fields = []
    if formatters is None:
        formatters = {}

    row = []

    for field in fields:
        if field in mixed_case_fields:
            field_name = field.replace(' ', '_')
        else:
            field_name = field.lower().replace(' ', '_')
        data = getattr(item, field_name, '')
        if data == '' and field_name == 'project_id':
            data = getattr(item, 'tenant_id', '')
        if field in formatters:
            row.append(formatters[field](data))
        else:
            row.append(data)
    return tuple(row)


def get_dict_properties(item, fields, mixed_case_fields=None, formatters=None):
    if mixed_case_fields is None:
        mixed_case_fields = []
    if formatters is None:
        formatters = {}

    row = []

    for field in fields:
        if field in mixed_case_fields:
            field_name = field.replace(' ', '_')
        else:
            field_name = field.lower().replace(' ', '_')
        data = item[field_name] if field_name in item else ''
        if field in formatters:
            row.append(formatters[field](data))
        else:
            row.append(data)
    return tuple(row)


def sort_items(items, sort_str):
    if not sort_str:
        return items
    items = list(items)
    sort_keys = sort_str.strip().split(',')
    for sort_key in reversed(sort_keys):
        reverse = False
        if ':' in sort_key:
            sort_key, direction = sort_key.split(':', 1)
            if not sort_key:
                msg = "empty string is not a valid sort key"
                raise exceptions.CommandError(msg)
            if direction not in ['asc', 'desc']:
                if not direction:
                    direction = "empty string"
                msg = ("%s is not a valid sort direction for sort key %s, "
                       "use asc or desc instead" % (direction, sort_key))
                raise exceptions.CommandError(msg)
            if direction == 'desc':
                reverse = True
        items.sort(key=lambda item: get_field(item, sort_key),
                   reverse=reverse)
    return items


def env(*vars, **kwargs):
    for v in vars:
        value = os.environ.get(v, None)
        if value:
            return value
    return kwargs.get('default', '')


def get_client_class(api_name, version, version_map):
    try:
        client_path = version_map[str(version)]
    except (KeyError, ValueError):
        msg = "Invalid %s client version '%s'. must be one of: %s" % (
              (api_name, version, ', '.join(version_map.keys())))
        raise exceptions.UnsupportedVersion(msg)

    return importutils.import_class(client_path)


def wait_for_status(status_f,
                    res_id,
                    status_field='status',
                    success_status=['active'],
                    error_status=['error'],
                    sleep_time=5,
                    callback=None):
    while True:
        res = status_f(res_id)
        status = getattr(res, status_field, '').lower()
        if status in success_status:
            retval = True
            break
        elif status in error_status:
            retval = False
            break
        if callback:
            progress = getattr(res, 'progress', None) or 0
            callback(progress)
        time.sleep(sleep_time)
    return retval


def wait_for_delete(manager,
                    res_id,
                    status_field='status',
                    error_status=['error'],
                    exception_name=['NotFound'],
                    sleep_time=5,
                    timeout=300,
                    callback=None):
    total_time = 0
    while total_time < timeout:
        try:
            res = manager.get(res_id)
        except Exception as ex:
            if type(ex).__name__ in exception_name:
                return True
            raise

        status = getattr(res, status_field, '').lower()
        if status in error_status:
            return False

        if callback:
            progress = getattr(res, 'progress', None) or 0
            callback(progress)
        time.sleep(sleep_time)
        total_time += sleep_time

    return False


def get_effective_log_level():
    root_log = logging.getLogger()
    min_log_lvl = logging.CRITICAL
    for handler in root_log.handlers:
        min_log_lvl = min(min_log_lvl, handler.level)
    return min_log_lvl


def get_password(stdin, prompt=None, confirm=True):
    message = prompt or "User Password:"
    if hasattr(stdin, 'isatty') and stdin.isatty():
        try:
            while True:
                first_pass = getpass.getpass(message)
                if not confirm:
                    return first_pass
                second_pass = getpass.getpass("Repeat " + message)
                if first_pass == second_pass:
                    return first_pass
                print("The passwords entered were not the same")
        except EOFError:
            raise exceptions.CommandError("Error reading password.")
    raise exceptions.CommandError("There was a request to be prompted for a"
                                  " password and a terminal was not detected.")


def read_blob_file_contents(blob_file):
    try:
        with open(blob_file) as file:
            blob = file.read().strip()
        return blob
    except IOError:
        msg = "Error occurred trying to read from file %s"
        raise exceptions.CommandError(msg % blob_file)


def build_kwargs_dict(arg_name, value):
    kwargs = {}
    if value:
        kwargs[arg_name] = value
    return kwargs


def is_ascii(string):
    try:
        if six.PY2:
            string.decode('ascii')
        else:
            if type(string) != six.text_type:
                return False
        return True
    except UnicodeDecodeError:
        return False


def update_dict(obj, dict, attributes):
    for attribute in attributes:
        if hasattr(obj, attribute) and getattr(obj, attribute) is not None:
            if getattr(obj, attribute) == "null":
                dict[attribute] = None
            else:
                dict[attribute] = getattr(obj, attribute)


def parse_tags(text):
    try:
        k, v = text.split('=', 1)
        return {k: v}
    except ValueError:
        msg = "%r is not in the format of key=value"
        raise exceptions.CommandError(msg % text)


def parse_bool(text):
    if text == 'true':
        return True
    elif text == 'false':
        return False
    else:
        msg = "%r is not boolean (true or false)"
        raise exceptions.CommandError(msg % text)


def parse_allocation_pools(text):
    if not text:
        return {}
    lst = text.split(',')
    if len(lst) != 2:
        msg = "%r is not in the format of ipv4,ipv4"
        raise exceptions.CommandError(msg % text)
    return {
        'start': lst[0],
        'end': lst[1]
    }


def validate_ipv4(text):
    try:
        if type(text) is not six.text_type:
            text = six.u(text)
        ipaddress.IPv4Address(text)
    except ipaddress.AddressValueError:
        msg = "%r is not a valid IPv4 address"
        raise exceptions.CommandError(msg % text)
    return text


def validate_int_range(text, min_val, max_val):
    try:
        int_text = int(text)
    except ValueError:
        msg = "%s is not an integer." % text
        raise exceptions.CommandError(msg)

    if min_val <= int_text <= max_val:
        return int_text

    msg = "%s is out of range[%i-%i]." % (text, min_val, max_val)
    raise exceptions.CommandError(msg)


def parse_host_routes(text):
    if not text:
        return {}
    lst = text.split(',')
    if len(lst) != 2:
        msg = "%r is not in the format of cidr,ipv4"
        raise exceptions.CommandError(msg % text)
    return {
        'destination': lst[0],
        'nexthop': lst[1]
    }


def parse_fixed_ips(text):
    if not text:
        return {}
    lst = text.split(',')
    if len(lst) > 2:
        msg = "%r is not in the format of subnet_id,ipv4 or ipv4"
        raise exceptions.CommandError(msg % text)
    if len(lst) == 2:
        return {
            'subnet_id': lst[0],
            'ip_address': lst[1]
        }
    if len(lst) == 1:
        return {'ip_address': lst[0]}


def parse_allowed_address_pairs(text):
    if not text:
        return {}
    lst = text.split(',')
    if len(lst) > 2:
        msg = "%r is not in the format of ipv4|cidr,mac or ipv4|cidr"
        raise exceptions.CommandError(msg % text)
    if len(lst) == 2:
        return {
            'ip_address': lst[0],
            'mac_address': lst[1]
        }
    if len(lst) == 1:
        return {'ip_address': lst[0]}


def filter_list_with_property(datalist, attribute, value):
    if value is None:
        return datalist
    postfilter = []
    for data in datalist:
        attr = getattr(data, attribute, None)
        if attr is None:
            continue
        if value in attr:
            postfilter.append(data)
    return postfilter


def parse_vna_interface(text, valid_keys):
    """parse vna interface text

    :param text: not in one of the following format
              net-id=net-uuid,ip-address=ip-addr,name=interface-name,
              slot-no=number,name=name
              slot-no=number,net-id=net-uuid,fixed-ips=ip-addr1:ip-addr2...
              interface-slot-no=number,ip-address=ip-addr, \
                     mac-address=mac-addr,type=type,vrid=vrid
    :param valid_keys: keys of the vna interface
    :return:
    """
    try:
        params = {}
        pattern_valid_keys = r'(%s)' % '|'.join(map(lambda x: x + '=', valid_keys))
        match_keys = re.findall(pattern_valid_keys, text)
        tmp_text = re.sub(r'\\t', '', text)
        match_values = re.sub(pattern_valid_keys, '\t', tmp_text).split('\t')
        for index, key in enumerate(match_keys):
            params[key.strip('=')] = match_values[index + 1].rstrip(',')

        if len(params) == 0:
            raise ValueError

        return params
    except ValueError:
        msg = "%r is not in the format of " \
              " net-id=net-uuid,ip-address=ip-addr,name=interface-name, or," \
              " slot-no=number,name=name, or," \
              " slot-no=number,net-id=net-uuid,fixed-ips=ip-addr1:ip-addr2," \
              " or, interface-slot-no=number,ip-address=ip-addr, " \
              "mac-address=mac-addr,type=type,vrid=vrid>"
        raise exceptions.CommandError(msg % text)


def parse_mlb_params(text, valid_keys, key_map):
    """parse mlb params text

    :param text: not in one of the following format
    :param valid_keys: keys of the params
    :param key_map: keys of the request body
    :return:
    """
    try:
        params = {}
        pattern_valid_keys = r'(%s)' % '|'.join(map(lambda x: x + '=', valid_keys))
        match_keys = re.findall(pattern_valid_keys, text)
        tmp_text = re.sub(r'\\t', '', text)
        match_values = re.sub(pattern_valid_keys, '\t', tmp_text).split('\t')
        for index, key in enumerate(match_keys):
            params[key_map[key.strip('=')]] = match_values[index + 1].rstrip(',')

        if len(params) == 0:
            raise ValueError

        return params
    except ValueError:
        msg = "%r is not in the format"
        raise exceptions.CommandError(msg % text)