import argparse
import logging
import netaddr
import os

from oslo_utils import encodeutils
from oslo_utils import importutils

import six

from . import exceptions
from ..i18n import _

ON_STATE = "ON"
OFF_STATE = "OFF"


def env(*vars, **kwargs):
    for v in vars:
        value = os.environ.get(v)
        if value:
            return value
    return kwargs.get('default', '')


def get_client_class(api_name, version, version_map):
    try:
        client_path = version_map[str(version)]
    except (KeyError, ValueError):
        msg = _("Invalid %(api_name)s client version '%(version)s'. must be "
                "one of: %(map_keys)s")
        msg = msg % {'api_name': api_name, 'version': version,
                     'map_keys': ', '.join(version_map.keys())}
        raise exceptions.UnsupportedVersion(msg)

    return importutils.import_class(client_path)


def get_item_properties(item, fields, mixed_case_fields=(), formatters=None):
    if formatters is None:
        formatters = {}

    row = []

    for field in fields:
        if field in formatters:
            row.append(formatters[field](item))
        else:
            if field in mixed_case_fields:
                field_name = field.replace(' ', '_')
            else:
                field_name = field.lower().replace(' ', '_')
            if not hasattr(item, field_name) and isinstance(item, dict):
                data = item[field_name]
            else:
                data = getattr(item, field_name, '')
            if data is None:
                data = ''
            row.append(data)
    return tuple(row)


def str2bool(strbool):
    if strbool is None:
        return None
    return strbool.lower() == 'true'


def str2dict(strdict):
    if not strdict:
        return {}
    return dict([kv.split('=', 1) for kv in strdict.split(',')])


def http_log_req(_logger, args, kwargs):
    if not _logger.isEnabledFor(logging.DEBUG):
        return

    string_parts = ['curl -i']
    for element in args:
        if element in ('GET', 'POST', 'DELETE', 'PUT'):
            string_parts.append(' -X %s' % element)
        else:
            string_parts.append(' %s' % element)

    for element in kwargs['headers']:
        header = ' -H "%s: %s"' % (element, kwargs['headers'][element])
        string_parts.append(header)

    if 'body' in kwargs and kwargs['body']:
        string_parts.append(" -d '%s'" % (kwargs['body']))
    req = encodeutils.safe_encode("".join(string_parts))
    _logger.debug("\nREQ: %s\n", req)


def http_log_resp(_logger, resp, body):
    if not _logger.isEnabledFor(logging.DEBUG):
        return
    _logger.debug("RESP:%(code)s %(headers)s %(body)s\n",
                  {'code': resp.status_code,
                   'headers': resp.headers,
                   'body': body})


def _safe_encode_without_obj(data):
    if isinstance(data, six.string_types):
        return encodeutils.safe_encode(data)
    return data


def safe_encode_list(data):
    return list(map(_safe_encode_without_obj, data))


def safe_encode_dict(data):
    def _encode_item(item):
        k, v = item
        if isinstance(v, list):
            return (k, safe_encode_list(v))
        elif isinstance(v, dict):
            return (k, safe_encode_dict(v))
        return (k, _safe_encode_without_obj(v))

    return dict(list(map(_encode_item, data.items())))


def add_boolean_argument(parser, name, **kwargs):
    for keyword in ('metavar', 'choices'):
        kwargs.pop(keyword, None)
    default = kwargs.pop('default', argparse.SUPPRESS)
    parser.add_argument(
        name,
        metavar='{True,False}',
        choices=['True', 'true', 'False', 'false'],
        default=default,
        **kwargs)


def is_valid_cidr(cidr):
    try:
        netaddr.IPNetwork(cidr)
        return True
    except Exception:
        return False


class APIDictWrapper(object):
    _apidict = {}

    def __init__(self, apidict):
        self._apidict = apidict

    def __getattribute__(self, attr):
        try:
            return object.__getattribute__(self, attr)
        except AttributeError:
            if attr not in self._apidict:
                raise
            return self._apidict[attr]

    def __getitem__(self, item):
        try:
            return getattr(self, item)
        except (AttributeError, TypeError) as e:
            raise KeyError(e)

    def __contains__(self, item):
        try:
            return hasattr(self, item)
        except TypeError:
            return False

    def get(self, item, default=None):
        try:
            return getattr(self, item)
        except (AttributeError, TypeError):
            return default

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self._apidict)

    def to_dict(self):
        return self._apidict


class ESIAPIDictWrapper(APIDictWrapper):

    def set_id_as_name_if_empty(self, length=8):
        try:
            if not self._apidict['name']:
                id = self._apidict['id']
                if length:
                    id = id[:length]
                self._apidict['name'] = '(%s)' % id
        except KeyError:
            pass

    def items(self):
        return self._apidict.items()

    @property
    def name_or_id(self):
        return (self._apidict.get('name') or
                '(%s)' % self._apidict['id'][:13])


class Network(ESIAPIDictWrapper):
    def __init__(self, apiresource):
        apiresource['admin_state'] = \
            'UP' if apiresource['admin_state_up'] else 'DOWN'
        for key in apiresource.keys():
            if key.find(':'):
                apiresource['__'.join(key.split(':'))] = apiresource[key]

        super(Network, self).__init__(apiresource)


class Subnet(ESIAPIDictWrapper):
    def __init__(self, apiresource):
        super(Subnet, self).__init__(apiresource)


class Port(ESIAPIDictWrapper):
    def __init__(self, apiresource):
        apiresource['admin_state'] = \
            'UP' if apiresource['admin_state_up'] else 'DOWN'
        if 'mac_learning_enabled' in apiresource:
            apiresource['mac_state'] = \
                ON_STATE if apiresource['mac_learning_enabled'] else OFF_STATE
        super(Port, self).__init__(apiresource)


class PhysicalPort(ESIAPIDictWrapper):
    def __init__(self, apiresource):
        super(PhysicalPort, self).__init__(apiresource)


class ReservedAddress(ESIAPIDictWrapper):
    def __init__(self, apiresource):
        super(ReservedAddress, self).__init__(apiresource)


class Quota(ESIAPIDictWrapper):
    def __init__(self, apiresource):
        super(Quota, self).__init__(apiresource)


class InternetGateway(ESIAPIDictWrapper):
    def __init__(self, apiresource):
        super(InternetGateway, self).__init__(apiresource)


class InternetService(ESIAPIDictWrapper):
    def __init__(self, apiresource):
        super(InternetService, self).__init__(apiresource)


class VPNGateway(ESIAPIDictWrapper):
    def __init__(self, apiresource):
        super(VPNGateway, self).__init__(apiresource)


class InterDCGateway(ESIAPIDictWrapper):
    def __init__(self, apiresource):
        super(InterDCGateway, self).__init__(apiresource)


class InterDCService(ESIAPIDictWrapper):
    def __init__(self, apiresource):
        super(InterDCService, self).__init__(apiresource)


class InterDCInterface(ESIAPIDictWrapper):
    def __init__(self, apiresource):
        super(InterDCInterface, self).__init__(apiresource)


class VPNService(ESIAPIDictWrapper):
    def __init__(self, apiresource):
        super(VPNService, self).__init__(apiresource)


class StaticRoute(ESIAPIDictWrapper):
    def __init__(self, apiresource):
        super(StaticRoute, self).__init__(apiresource)


class PubicIP(ESIAPIDictWrapper):
    def __init__(self, apiresource):
        cidr = apiresource.get('cidr', '')
        submask_length = str(apiresource.get('submask_length', ''))
        apiresource.update({
            'prefixed_cidr': cidr + '/' + submask_length
        })
        super(PubicIP, self).__init__(apiresource)


class GwInterface(ESIAPIDictWrapper):
    def __init__(self, apiresource):
        apiresource.setdefault('network_name', '')
        super(GwInterface, self).__init__(apiresource)


class VPNInterface(ESIAPIDictWrapper):
    def __init__(self, apiresource):
        super(VPNInterface, self).__init__(apiresource)


class QosOption(ESIAPIDictWrapper):
    def __init__(self, apiresource):
        super(QosOption, self).__init__(apiresource)


class Firewall(ESIAPIDictWrapper):
    def __init__(self, apiresource):
        super(Firewall, self).__init__(apiresource)


class FirewallInterface(ESIAPIDictWrapper):
    def __init__(self, apiresource):
        if 'virtual_ip_properties' in apiresource:
            if apiresource['virtual_ip_properties'] is not None:
                apiresource['vrid'] = apiresource['virtual_ip_properties']['vrid']
        super(FirewallInterface, self).__init__(apiresource)


class FirewallPlan(ESIAPIDictWrapper):
    def __init__(self, apiresource):
        super(FirewallPlan, self).__init__(apiresource)


class LoadBalancer(ESIAPIDictWrapper):
    def __init__(self, apiresource):
        super(LoadBalancer, self).__init__(apiresource)


class LoadBalancerPlan(ESIAPIDictWrapper):
    def __init__(self, apiresource):
        super(LoadBalancerPlan, self).__init__(apiresource)


class LoadBalancerInterface(ESIAPIDictWrapper):
    def __init__(self, apiresource):
        super(LoadBalancerInterface, self).__init__(apiresource)


class LoadBalancerSyslogServer(ESIAPIDictWrapper):
    def __init__(self, apiresource):
        super(LoadBalancerSyslogServer, self).__init__(apiresource)

class CommonFunctionPool(ESIAPIDictWrapper):
    def __init__(self, apiresource):
        super(CommonFunctionPool, self).__init__(apiresource)


class CommonFunctionGateway(ESIAPIDictWrapper):
    def __init__(self, apiresource):
        super(CommonFunctionGateway, self).__init__(apiresource)


class CommonFunction(ESIAPIDictWrapper):
    def __init__(self, apiresource):
        super(CommonFunction, self).__init__(apiresource)


class ColoLogicalLink(ESIAPIDictWrapper):
    def __init__(self, apiresource):
        super(ColoLogicalLink, self).__init__(apiresource)


class ColoPhysicalLink(ESIAPIDictWrapper):
    def __init__(self, apiresource):
        super(ColoPhysicalLink, self).__init__(apiresource)


class ColoSpace(ESIAPIDictWrapper):
    def __init__(self, apiresource):
        super(ColoSpace, self).__init__(apiresource)
