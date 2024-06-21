import logging
import time

import requests
import six.moves.urllib.parse as urlparse

from .. import client
from ..common import constants
from ..common import exceptions
from ..common import serializer
from ..common import utils
from ..i18n import _

_logger = logging.getLogger(__name__)


def exception_handler_v20(status_code, error_content):
    error_dict = None
    if isinstance(error_content, dict):
        error_dict = {
            'type': 'Network',
            'message': error_content.get(u'error')
        }

    bad_esi_error_flag = False
    if error_dict:
        try:
            error_type = error_dict['type']
            error_message = error_dict['message']
        except Exception:
            error_type = 'Network'
            error_message = error_dict

        if not bad_esi_error_flag:
            client_exc = getattr(exceptions, '%sClient' % error_type, None)
            if not client_exc:
                client_exc = exceptions.HTTP_EXCEPTION_MAP.get(status_code)
            if client_exc:
                raise client_exc(message=error_message,
                                 status_code=status_code)
            else:
                raise exceptions.ESIClientException(
                    status_code=status_code, message=error_message)
        else:
            raise exceptions.ESIClientException(status_code=status_code,
                                                message=error_dict)
    else:
        message = None
        if isinstance(error_content, dict):
            message = error_content.get('message')
        if message:
            raise exceptions.ESIClientException(status_code=status_code,
                                                message=message)

    msg = "%s-%s" % (status_code, error_content)
    raise exceptions.ESIClientException(status_code=status_code,
                                        message=msg)


class APIParamsCall(object):
    def __init__(self, function):
        self.function = function

    def __get__(self, instance, owner):
        def with_params(*args, **kwargs):
            _format = instance.format
            if 'format' in kwargs:
                instance.format = kwargs['format']
            ret = self.function(instance, *args, **kwargs)
            instance.format = _format
            return ret

        return with_params


class ClientBase(object):
    EXTED_PLURALS = {}

    def __init__(self, **kwargs):
        super(ClientBase, self).__init__()
        self.retries = kwargs.pop('retries', 0)
        self.raise_errors = kwargs.pop('raise_errors', True)
        self.httpclient = client.construct_http_client(**kwargs)
        self.version = '2.0'
        self.format = 'json'
        self.action_prefix = "/v%s" % self.version
        self.retry_interval = 1

    def _handle_fault_response(self, status_code, response_body):
        _logger.debug("Error message: %s", response_body)
        try:
            des_error_body = self.deserialize(response_body, status_code)
        except Exception:
            des_error_body = {'message': response_body}
        exception_handler_v20(status_code, des_error_body)

    def do_request(self, method, action, body=None, headers=None, params=None):
        action = self.action_prefix + action
        if type(params) is dict and params:
            params = utils.safe_encode_dict(params)
            action += '?' + urlparse.urlencode(params, doseq=1)

        if body:
            body = self.serialize(body)

        resp, replybody = self.httpclient.do_request(
            action, method, body=body,
            content_type=self.content_type())

        status_code = resp.status_code
        if status_code in (requests.codes.ok,
                           requests.codes.created,
                           requests.codes.accepted,
                           requests.codes.no_content):
            return self.deserialize(replybody, status_code)
        else:
            if not replybody:
                replybody = resp.reason
            self._handle_fault_response(status_code, replybody)

    def get_auth_info(self):
        return self.httpclient.get_auth_info()

    def serialize(self, data):
        if data is None:
            return None
        elif type(data) is dict:
            return serializer.Serializer(
                self.get_attr_metadata()).serialize(data, self.content_type())
        else:
            raise Exception(_("Unable to serialize object of type = '%s'") %
                            type(data))

    def deserialize(self, data, status_code):
        if status_code == 204:
            return data
        return serializer.Serializer(self.get_attr_metadata()).deserialize(
            data, self.content_type())['body']

    def get_attr_metadata(self):
        if self.format == 'json':
            return {}
        old_request_format = self.format
        self.format = 'json'
        exts = self.list_extensions()['extensions']
        self.format = old_request_format
        ns = dict([(ext['alias'], ext['namespace']) for ext in exts])
        self.EXTED_PLURALS.update(constants.PLURALS)
        return {'plurals': self.EXTED_PLURALS,
                'xmlns': constants.XML_NS_V20,
                constants.EXT_NS: ns}

    def content_type(self, _format=None):
        _format = _format or self.format
        return "application/%s" % _format

    def retry_request(self, method, action, body=None,
                      headers=None, params=None):
        max_attempts = self.retries + 1
        for i in range(max_attempts):
            try:
                return self.do_request(method, action, body=body,
                                       headers=headers, params=params)
            except exceptions.ConnectionFailed:
                if i < self.retries:
                    _logger.debug('Retrying connection to ESI service')
                    time.sleep(self.retry_interval)
                elif self.raise_errors:
                    raise

        if self.retries:
            msg = (_("Failed to connect to ESI server after %d attempts")
                   % max_attempts)
        else:
            msg = _("Failed to connect ESI server")

        raise exceptions.ConnectionFailed(reason=msg)

    def delete(self, action, body=None, headers=None, params=None):
        return self.retry_request("DELETE", action, body=body,
                                  headers=headers, params=params)

    def get(self, action, body=None, headers=None, params=None):
        return self.retry_request("GET", action, body=body,
                                  headers=headers, params=params)

    def post(self, action, body=None, headers=None, params=None):
        return self.do_request("POST", action, body=body,
                               headers=headers, params=params)

    def put(self, action, body=None, headers=None, params=None):
        return self.retry_request("PUT", action, body=body,
                                  headers=headers, params=params)

    def list(self, collection, path, retrieve_all=True, **params):
        if retrieve_all:
            res = []
            for r in self._pagination(collection, path, **params):
                res.extend(r[collection])
            return {collection: res}
        else:
            return self._pagination(collection, path, **params)

    def _pagination(self, collection, path, **params):
        if params.get('page_reverse', False):
            linkrel = 'previous'
        else:
            linkrel = 'next'
        next = True
        while next:
            res = self.get(path, params=params)
            yield res
            next = False
            try:
                for link in res['%s_links' % collection]:
                    if link['rel'] == linkrel:
                        query_str = urlparse.urlparse(link['href']).query
                        params = urlparse.parse_qs(query_str)
                        next = True
                        break
            except KeyError:
                break


class Client(ClientBase):
    networks_path = "/networks"
    network_path = "/networks/%s"
    ports_path = "/ports"
    port_path = "/ports/%s"
    subnets_path = "/subnets"
    subnet_path = "/subnets/%s"
    subnetpools_path = "/subnetpools"
    subnetpool_path = "/subnetpools/%s"
    quotas_path = "/quotas"
    quota_path = "/quotas/%s"
    extensions_path = "/extensions"
    extension_path = "/extensions/%s"

    physical_ports_path = "/physical_ports"
    physical_port_path = "/physical_ports/%s"

    gw_interfaces_path = '/gw_interfaces'
    gw_interface_path = '/gw_interfaces/%s'

    fic_interfaces_path = '/fic_interfaces'
    fic_interface_path = '/fic_interfaces/%s'

    static_routes_path = '/static_routes'
    static_route_path = '/static_routes/%s'

    internet_services_path = '/internet_services'
    internet_service_path = '/internet_services/%s'

    fic_services_path = '/fic_services'
    fic_service_path = '/fic_services/%s'

    internet_gateways_path = '/internet_gateways'
    internet_gateway_path = '/internet_gateways/%s'

    fic_gateways_path = '/fic_gateways'
    fic_gateway_path = '/fic_gateways/%s'

    interdc_gateways_path = "/interdc_gateways"
    interdc_gateway_path = "/interdc_gateways/%s"

    interdc_services_path = "/interdc_services"
    interdc_service_path = "/interdc_services/%s"

    interdc_interfaces_path = "/interdc_interfaces"
    interdc_interface_path = "/interdc_interfaces/%s"

    public_ips_path = '/public_ips'
    public_ip_path = '/public_ips/%s'

    public_ip_pools_path = '/public_ip_pools'
    public_ip_pool_path = '/public_ip_pools/%s'

    qos_options_path = '/qos_options'
    qos_option_path = '/qos_options/%s'

    DHCP_NETS = '/dhcp-networks'
    DHCP_AGENTS = '/dhcp-agents'

    firewalls_path = '/firewalls'
    firewall_path = '/firewalls/%s'

    firewall_interfaces_path = '/firewall_interfaces'
    firewall_interface_path = '/firewall_interfaces/%s'

    firewall_plans_path = '/firewall_plans'
    firewall_plan_path = '/firewall_plans/%s'

    loadbalancers_path = '/load_balancers'
    loadbalancer_path = '/load_balancers/%s'

    loadbalancer_plans_path = '/load_balancer_plans'
    loadbalancer_plan_path = '/load_balancer_plans/%s'

    loadbalancer_interfaces_path = '/load_balancer_interfaces'
    loadbalancer_interface_path = '/load_balancer_interfaces/%s'

    loadbalancer_syslog_servers_path = '/load_balancer_syslog_servers'
    loadbalancer_syslog_server_path = '/load_balancer_syslog_servers/%s'

    _cfgw_singular = 'common_function_gateway'
    _cfgw_plural = _cfgw_singular + 's'

    common_function_gateways_path = '/%s' % _cfgw_plural
    common_function_gateway_path = common_function_gateways_path + '/%s'

    _common_function_pool_singular = 'common_function_pool'
    _common_function_pool_plural = _common_function_pool_singular + 's'

    common_function_pools_path = '/%s' % _common_function_pool_plural
    common_function_pool_path = common_function_pools_path + '/%s'

    _common_function_singular = 'common_function'
    _common_function_plural = _common_function_singular + 's'

    common_functions_path = '/%s' % _common_function_plural
    common_function_path = common_functions_path + '/%s'

    reserve_addresses_path = "/reserve_addresses"
    reserve_address_path = "/reserve_addresses/%s"

    _colo_logical_link_singular = 'colocation_logical_link'
    _colo_logical_link_plural = _colo_logical_link_singular + 's'

    colocation_logical_links_path = '/%s' % _colo_logical_link_plural
    colocation_logical_link_path = colocation_logical_links_path + '/%s'

    _colo_physical_link_singular = 'colocation_physical_link'
    _colo_physical_link_plural = _colo_physical_link_singular + 's'

    colocation_physical_links_path = '/%s' % _colo_physical_link_plural
    colocation_physical_link_path = colocation_physical_links_path + '/%s'

    _colo_space_singular = 'colocation_space'
    _colo_space_plural = _colo_space_singular + 's'

    colocation_spaces_path = '/%s' % _colo_space_plural
    colocation_space_path = colocation_spaces_path + '/%s'

    EXTED_PLURALS = {'routers': 'router',
                     'floatingips': 'floatingip',
                     'service_types': 'service_type',
                     'service_definitions': 'service_definition',
                     'security_groups': 'security_group',
                     'security_group_rules': 'security_group_rule',
                     'ipsecpolicies': 'ipsecpolicy',
                     'ikepolicies': 'ikepolicy',
                     'ipsec_site_connections': 'ipsec_site_connection',
                     'vips': 'vip',
                     'pools': 'pool',
                     'members': 'member',
                     'health_monitors': 'health_monitor',
                     'quotas': 'quota',
                     'service_providers': 'service_provider',
                     'firewall_rules': 'firewall_rule',
                     'firewall_policies': 'firewall_policy',
                     'firewalls': 'firewall',
                     'metering_labels': 'metering_label',
                     'metering_label_rules': 'metering_label_rule',
                     'net_partitions': 'net_partition',
                     'packet_filters': 'packet_filter',
                     'loadbalancers': 'loadbalancer',
                     'listeners': 'listener',
                     'lbaas_pools': 'lbaas_pool',
                     'lbaas_healthmonitors': 'lbaas_healthmonitor',
                     'lbaas_members': 'lbaas_member',
                     'healthmonitors': 'healthmonitor',
                     }

    @APIParamsCall
    def get_quotas_tenant(self, **_params):
        return self.get(self.quota_path % 'tenant', params=_params)

    @APIParamsCall
    def list_quotas(self, **_params):
        return self.get(self.quotas_path, params=_params)

    @APIParamsCall
    def show_quota(self, tenant_id, **_params):
        return self.get(self.quota_path % tenant_id, params=_params)

    @APIParamsCall
    def update_quota(self, tenant_id, body=None):
        return self.put(self.quota_path % tenant_id, body=body)

    @APIParamsCall
    def delete_quota(self, tenant_id):
        return self.delete(self.quota_path % tenant_id)

    @APIParamsCall
    def list_extensions(self, **_params):
        return self.get(self.extensions_path, params=_params)

    @APIParamsCall
    def show_extension(self, ext_alias, **_params):
        return self.get(self.extension_path % ext_alias, params=_params)

    @APIParamsCall
    def list_ports(self, retrieve_all=True, **_params):
        return self.list('ports', self.ports_path, retrieve_all,
                         **_params)

    @APIParamsCall
    def show_port(self, port, **_params):
        return self.get(self.port_path % port, params=_params)

    @APIParamsCall
    def create_port(self, body=None):
        return self.post(self.ports_path, body=body)

    @APIParamsCall
    def update_port(self, port, body=None):
        return self.put(self.port_path % port, body=body)

    @APIParamsCall
    def delete_port(self, port):
        return self.delete(self.port_path % port)

    @APIParamsCall
    def list_physical_ports(self, retrieve_all=True, **_params):
        return self.list('physical_ports',
                         self.physical_ports_path,
                         retrieve_all,
                         **_params)

    @APIParamsCall
    def show_physical_port(self, port, **_params):
        return self.get(self.physical_port_path % port, params=_params)

    @APIParamsCall
    def list_networks(self, retrieve_all=True, **_params):
        return self.list('networks', self.networks_path, retrieve_all,
                         **_params)

    @APIParamsCall
    def show_network(self, network, **_params):
        return self.get(self.network_path % network, params=_params)

    @APIParamsCall
    def create_network(self, body=None):
        return self.post(self.networks_path, body=body)

    @APIParamsCall
    def update_network(self, network, body=None):
        return self.put(self.network_path % network, body=body)

    @APIParamsCall
    def delete_network(self, network):
        return self.delete(self.network_path % network)

    @APIParamsCall
    def list_subnets(self, retrieve_all=True, **_params):
        return self.list(
            'subnets', self.subnets_path, retrieve_all, **_params)

    @APIParamsCall
    def show_subnet(self, subnet, **_params):
        return self.get(self.subnet_path % subnet, params=_params)

    @APIParamsCall
    def create_subnet(self, body=None):
        return self.post(self.subnets_path, body=body)

    @APIParamsCall
    def update_subnet(self, subnet, body=None):
        return self.put(self.subnet_path % subnet, body=body)

    @APIParamsCall
    def delete_subnet(self, subnet):
        return self.delete(self.subnet_path % subnet)

    @APIParamsCall
    def list_internet_gateways(self, **_params):
        return self.list('internet_gateways', self.internet_gateways_path, **_params)

    @APIParamsCall
    def show_internet_gateway(self, internet_gateway_id, **_params):
        return self.get(self.internet_gateway_path % internet_gateway_id, params=_params)

    @APIParamsCall
    def create_internet_gateway(self, body=None):
        return self.post(self.internet_gateways_path, body=body)

    @APIParamsCall
    def update_internet_gateway(self, internet_gateway_id, body=None):
        return self.put(self.internet_gateway_path % internet_gateway_id, body=body)

    @APIParamsCall
    def delete_internet_gateway(self, internet_gateway_id):
        return self.delete(self.internet_gateway_path % internet_gateway_id)

    @APIParamsCall
    def list_fic_gateways(self, **_params):
        return self.list('fic_gateways', self.fic_gateways_path, **_params)

    @APIParamsCall
    def show_fic_gateway(self, fic_gateway_id, **_params):
        return self.get(self.fic_gateway_path % fic_gateway_id, params=_params)

    @APIParamsCall
    def list_interdc_services(self, **_params):
        return self.list('interdc_services', self.interdc_services_path, **_params)

    @APIParamsCall
    def show_interdc_service(self, interdc_service_id, **_params):
        return self.get(self.interdc_service_path % interdc_service_id,
                        **_params)

    @APIParamsCall
    def list_interdc_gateways(self, **_params):
        return self.list('interdc_gateways', self.interdc_gateways_path, **_params)

    @APIParamsCall
    def show_interdc_gateway(self, interdc_gateway_id, **_params):
        return self.get(self.interdc_gateway_path % interdc_gateway_id,
                        **_params)

    @APIParamsCall
    def create_interdc_gateway(self, body=None):
        return self.post(self.interdc_gateways_path, body=body)

    @APIParamsCall
    def update_interdc_gateway(self, interdc_gateway_id, body=None):
        return self.put(self.interdc_gateway_path % interdc_gateway_id, body=body)

    @APIParamsCall
    def delete_interdc_gateway(self, interdc_gateway_id):
        return self.delete(self.interdc_gateway_path % interdc_gateway_id)

    @APIParamsCall
    def list_interdc_interfaces(self, **_params):
        return self.list('interdc_interfaces',
                         self.interdc_interfaces_path,
                         **_params)

    @APIParamsCall
    def show_interdc_interface(self, interdc_interface_id, **_params):
        return self.get(self.interdc_interface_path % interdc_interface_id,
                        **_params)

    @APIParamsCall
    def create_interdc_interface(self, body=None):
        return self.post(self.interdc_interfaces_path, body=body)

    @APIParamsCall
    def delete_interdc_interface(self, interdc_interface_id):
        return self.delete(self.interdc_interface_path % interdc_interface_id)

    @APIParamsCall
    def update_interdc_interface(self, interdc_interface_id, body=None):
        return self.put(self.interdc_interface_path % interdc_interface_id, body=body)

    @APIParamsCall
    def list_gw_interfaces(self, **_params):
        return self.list('gw_interfaces', self.gw_interfaces_path, **_params)

    @APIParamsCall
    def show_gw_interface(self, gw_interface_id, **_params):
        return self.get(self.gw_interface_path % gw_interface_id, params=_params)

    @APIParamsCall
    def create_gw_interface(self, body=None):
        return self.post(self.gw_interfaces_path, body=body)

    @APIParamsCall
    def update_gw_interface(self, gw_interface_id, body=None):
        return self.put(self.gw_interface_path % gw_interface_id, body=body)

    @APIParamsCall
    def delete_gw_interface(self, gw_interface_id):
        return self.delete(self.gw_interface_path % gw_interface_id)

    @APIParamsCall
    def list_fic_interfaces(self, **_params):
        return self.list('fic_interfaces', self.fic_interfaces_path, **_params)

    @APIParamsCall
    def show_fic_interface(self, fic_interface_id, **_params):
        return self.get(self.fic_interface_path % fic_interface_id,
                        params=_params)

    @APIParamsCall
    def list_static_routes(self, **_params):
        return self.list('static_routes',
                         self.static_routes_path, **_params)

    @APIParamsCall
    def show_static_route(self, static_route_id, **_params):
        return self.get(self.static_route_path % static_route_id, params=_params)

    @APIParamsCall
    def create_static_route(self, body=None):
        return self.post(self.static_routes_path, body=body)

    @APIParamsCall
    def update_static_route(self, static_route_id, body=None):
        return self.put(self.static_route_path % static_route_id, body=body)

    @APIParamsCall
    def delete_static_route(self, static_route_id):
        return self.delete(self.static_route_path % static_route_id)

    @APIParamsCall
    def list_public_ips(self, **_params):
        return self.list('public_ips',
                         self.public_ips_path, **_params)

    @APIParamsCall
    def show_public_ip(self, public_ip_id, **_params):
        return self.get(self.public_ip_path % public_ip_id, params=_params)

    @APIParamsCall
    def create_public_ip(self, body=None):
        return self.post(self.public_ips_path, body=body)

    @APIParamsCall
    def update_public_ip(self, public_ip_id, body=None):
        return self.put(self.public_ip_path % public_ip_id, body=body)

    @APIParamsCall
    def delete_public_ip(self, public_ip_id):
        return self.delete(self.public_ip_path % public_ip_id)

    @APIParamsCall
    def list_internet_services(self, **_params):
        return self.list('internet_services', self.internet_services_path, **_params)

    @APIParamsCall
    def show_internet_service(self, internet_service_id, **_params):
        return self.get(self.internet_service_path % internet_service_id, params=_params)

    @APIParamsCall
    def list_fic_services(self, **_params):
        return self.list('fic_services', self.fic_services_path, **_params)

    @APIParamsCall
    def show_fic_service(self, fic_service_id, **_params):
        return self.get(self.fic_service_path % fic_service_id, params=_params)

    @APIParamsCall
    def list_public_ip_pools(self, **_params):
        return self.list('public_ip_pools',
                         self.public_ip_pools_path, **_params)

    @APIParamsCall
    def show_public_ip_pool(self, public_ip_pool_id, **_params):
        return self.get(self.public_ip_pool_path % public_ip_pool_id, params=_params)

    @APIParamsCall
    def list_qos_options(self, **_params):
        return self.list('qos_options',
                         self.qos_options_path, **_params)

    @APIParamsCall
    def show_qos_option(self, qos_option_id, **_params):
        return self.get(self.qos_option_path % qos_option_id, params=_params)

    @APIParamsCall
    def list_firewalls(self, **_params):
        return self.list('firewalls', self.firewalls_path, **_params)

    @APIParamsCall
    def create_firewall(self, body=None):
        return self.post(self.firewalls_path, body=body)

    @APIParamsCall
    def show_firewall(self, firewall_id, **_params):
        return self.get(self.firewall_path % firewall_id, params=_params)

    @APIParamsCall
    def update_firewall(self, firewall_id, body=None):
        return self.put(self.firewall_path % firewall_id, body=body)

    @APIParamsCall
    def delete_firewall(self, firewall_id):
        return self.delete(self.firewall_path % firewall_id)

    @APIParamsCall
    def reboot_firewall(self, firewall_id, body=None):
        return self.post(self.firewall_path % firewall_id + "/reboot", body=body)

    @APIParamsCall
    def reset_password_firewall(self, firewall_id, body=None):
        return self.post(self.firewall_path % firewall_id + "/reset_password", body=body)

    @APIParamsCall
    def list_firewall_interfaces(self, **_params):
        return self.list('firewall_interfaces', self.firewall_interfaces_path, **_params)

    @APIParamsCall
    def show_firewall_interface(self, firewall_interface_id, **_params):
        return self.get(self.firewall_interface_path % firewall_interface_id, params=_params)

    @APIParamsCall
    def update_firewall_interface(self, firewall_interface_id, body=None):
        return self.put(self.firewall_interface_path % firewall_interface_id, body=body)

    @APIParamsCall
    def list_firewall_plans(self, **_params):
        return self.list('firewall_plans', self.firewall_plans_path, **_params)

    @APIParamsCall
    def show_firewall_plan(self, firewall_plan_id, **_params):
        return self.get(self.firewall_plan_path % firewall_plan_id, params=_params)

    @APIParamsCall
    def list_loadbalancers(self, **_params):
        return self.list('load_balancers', self.loadbalancers_path, **_params)

    @APIParamsCall
    def create_loadbalancer(self, body=None):
        return self.post(self.loadbalancers_path, body=body)

    @APIParamsCall
    def show_loadbalancer(self, loadbalancer_id, **_params):
        return self.get(self.loadbalancer_path % loadbalancer_id, params=_params)

    @APIParamsCall
    def update_loadbalancer(self, loadbalancer_id, body=None):
        return self.put(self.loadbalancer_path % loadbalancer_id, body=body)

    @APIParamsCall
    def delete_loadbalancer(self, loadbalancer_id):
        return self.delete(self.loadbalancer_path % loadbalancer_id)

    @APIParamsCall
    def reboot_loadbalancer(self, loadbalancer_id, body=None):
        response = self.post(self.loadbalancer_path % loadbalancer_id + "/reboot", body=body)

    @APIParamsCall
    def list_loadbalancer_plans(self, **_params):
        return self.list('load_balancer_plans', self.loadbalancer_plans_path, **_params)

    @APIParamsCall
    def create_loadbalancer_plan(self, body=None):
        return self.post(self.loadbalancer_plans_path, body=body)

    @APIParamsCall
    def show_loadbalancer_plan(self, loadbalancerplan_id, **_params):
        return self.get(self.loadbalancer_plan_path % loadbalancerplan_id, params=_params)

    @APIParamsCall
    def update_loadbalancer_plan(self, loadbalancerplan_id, body=None):
        return self.put(self.loadbalancer_plan_path % loadbalancerplan_id, body=body)

    @APIParamsCall
    def delete_loadbalancer_plan(self, loadbalancerplan_id):
        return self.delete(self.loadbalancer_plan_path % loadbalancerplan_id)

    @APIParamsCall
    def list_loadbalancer_interfaces(self, **_params):
        return self.list('load_balancer_interfaces', self.loadbalancer_interfaces_path, **_params)

    @APIParamsCall
    def show_loadbalancer_interface(self, loadbalancer_interface_id, **_params):
        return self.get(self.loadbalancer_interface_path % loadbalancer_interface_id, params=_params)

    @APIParamsCall
    def update_loadbalancer_interface(self, loadbalancer_interface_id, body=None):
        return self.put(self.loadbalancer_interface_path % loadbalancer_interface_id, body=body)

    @APIParamsCall
    def reset_password_loadbalancer(self, loadbalancer_id, body=None):
        return self.post(self.loadbalancer_path % loadbalancer_id + "/reset_password", body=body)

    @APIParamsCall
    def list_loadbalancer_syslog_servers(self, **_params):
        return self.list('load_balancer_syslog_servers', self.loadbalancer_syslog_servers_path, **_params)

    @APIParamsCall
    def show_loadbalancer_syslog_server(self, loadbalancer_syslog_server_id, **_params):
        return self.get(self.loadbalancer_syslog_server_path % loadbalancer_syslog_server_id, params=_params)

    @APIParamsCall
    def create_loadbalancer_syslog_server(self, body=None):
        return self.post(self.loadbalancer_syslog_servers_path, body=body)

    @APIParamsCall
    def delete_loadbalancer_syslog_server(self, loadbalancer_syslog_server_id, body=None):
        return self.delete(self.loadbalancer_syslog_server_path % loadbalancer_syslog_server_id, body=body)

    @APIParamsCall
    def update_loadbalancer_syslog_server(self, loadbalancer_syslog_server_id, body=None):
        return self.put(self.loadbalancer_syslog_server_path % loadbalancer_syslog_server_id, body=body)

    @APIParamsCall
    def list_cfgws(self, **_params):
        return self.list(self._cfgw_plural, self.common_function_gateways_path, **_params)

    @APIParamsCall
    def show_cfgw(self, cfgw_id, **_params):
        return self.get(self.common_function_gateway_path % cfgw_id, params=_params)

    @APIParamsCall
    def create_cfgw(self, body=None):
        return self.post(self.common_function_gateways_path, body=body)

    @APIParamsCall
    def update_cfgw(self, cfgw_id, body=None):
        return self.put(self.common_function_gateway_path % cfgw_id, body=body)

    @APIParamsCall
    def delete_cfgw(self, cfgw_id):
        return self.delete(self.common_function_gateway_path % cfgw_id)

    @APIParamsCall
    def list_common_function_pools(self, **_params):
        return self.list(self._common_function_pool_plural,
                         self.common_function_pools_path, **_params)

    @APIParamsCall
    def show_common_function_pool(self, cfp_id, **_params):
        return self.get(self.common_function_pool_path % cfp_id, params=_params)

    @APIParamsCall
    def list_common_functions(self, **_params):
        return self.list(self._common_function_plural,
                         self.common_functions_path, **_params)

    @APIParamsCall
    def show_common_function(self, cfp_id, **_params):
        return self.get(self.common_function_path % cfp_id, params=_params)

    @APIParamsCall
    def list_reserve_addresses(self, **_params):
        return self.list('reserve_addresses', self.reserve_addresses_path, **_params)

    @APIParamsCall
    def show_reserve_address(self, tenant_id, **_params):
        ra = self.get(self.reserve_address_path % tenant_id, params=_params)
        return ra

    @APIParamsCall
    def list_colo_logical_links(self, **_params):
        return self.list(self._colo_logical_link_plural,
                         self.colocation_logical_links_path, **_params)

    @APIParamsCall
    def show_colo_logical_link(self, colo_logical_link_id, **_params):
        return self.get(
            self.colocation_logical_link_path % colo_logical_link_id,
            params=_params)

    @APIParamsCall
    def create_colo_logical_link(self, body=None):
        return self.post(self.colocation_logical_links_path,
                         body=body)

    @APIParamsCall
    def update_colo_logical_link(self, colo_logical_link_id, body=None):
        return self.put(self.colocation_logical_link_path %
                        colo_logical_link_id, body=body)

    @APIParamsCall
    def delete_colo_logical_link(self, colo_logical_link_id):
        return self.delete(self.colocation_logical_link_path %
                           colo_logical_link_id)

    @APIParamsCall
    def list_colo_physical_links(self, **_params):
        return self.list(self._colo_physical_link_plural,
                         self.colocation_physical_links_path, **_params)

    @APIParamsCall
    def show_colo_physical_link(self, colo_physical_link_id, **_params):
        return self.get(
            self.colocation_physical_link_path % colo_physical_link_id,
            params=_params)

    @APIParamsCall
    def list_colo_spaces(self, **_params):
        return self.list(self._colo_space_plural,
                         self.colocation_spaces_path, **_params)

    @APIParamsCall
    def show_colo_space(self, colo_space_id, **_params):
        return self.get(
            self.colocation_space_path % colo_space_id,
            params=_params)
