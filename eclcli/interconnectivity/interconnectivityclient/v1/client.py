# -*- coding: utf-8 -*-

#  Copyright 2012 OpenStack Foundation.
# Copyright 2015 Hewlett-Packard Development Company, L.P.
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#

import logging
import time

import requests
import six
import six.moves.urllib.parse as urlparse

from .. import ECC_VERSION
from .. import ECC_FORMAT
from .. import ACTION_PREFIX
from .. import client
from ..common import constants
from ..common import exceptions
from ..common import serializer
from ..common import utils
from ..i18n import _

from datetime import datetime

_logger = logging.getLogger(__name__)


def exception_handler_v10(status_code, error_content):
    """Exception handler for API v2.0 client.

    This routine generates the appropriate Ecc exception according to
    the contents of the response body.

    Errorパターンは以下のとおり。

    {
        "cause": "Internal Server Error"
    }

    {
        "errors":[{
            "errorCode":"E9999",
            "errorMessage":"System error occurred."
        }]
    }

    :param status_code: HTTP error status code
    :param error_content: deserialized body of error response
    """
    error_message = 'Some error has occured.'
    try:
        if isinstance(error_content, dict):
            if error_content['cause']:
                error_body = error_content['cause']
            elif error_content.get('errors'):
                error_body = error_content['error']

        if isinstance(error_body, six.text_type) or isinstance(error_body, str):
            error_message = error_body
        elif isinstance(error_body, dict):
            error_message = error_body.get['errorCode'] + ' ' + \
                            error_body.get['errorMessage']

        client_exc = exceptions.HTTP_EXCEPTION_MAP.get(status_code)
        if client_exc:
            raise client_exc(status_code=status_code,
                             message=error_message)
        else:
            raise  # -> Go to except section below.
    except Exception:
        raise exceptions.EccClientException(status_code=status_code,
                                            message=error_message)

    ####################################
    # Original Logic
    ####################################
    #
    # error_dict = None
    # if isinstance(error_content, dict):
    #     error_dict = error_content.get('EccError')
    # # # Find real error type
    # bad_err_error_flag = False
    # if error_dict:
    #     # If Ecc key is found, it will definitely contain
    #     # a 'message' and 'type' keys?
    #     try:
    #         error_type = error_dict['type']
    #         error_message = error_dict['message']
    #         if error_dict['detail']:
    #             error_message += "\n" + error_dict['detail']
    #     except Exception:
    #         bad_err_error_flag = True
    #     if not bad_err_error_flag:
    #         # If corresponding exception is defined, use it.
    #         client_exc = getattr(exceptions, '%sClient' % error_type, None)
    #         # Otherwise look up per status-code client exception
    #         if not client_exc:
    #             client_exc = exceptions.HTTP_EXCEPTION_MAP.get(status_code)
    #         if client_exc:
    #             raise client_exc(message=error_message,
    #                              status_code=status_code)
    #         else:
    #             raise exceptions.EccClientException(
    #                 status_code=status_code, message=error_message)
    #     else:
    #         raise exceptions.EccClientException(status_code=status_code,
    #                                                 message=error_dict)
    # else:
    #     message = None
    #     if isinstance(error_content, dict):
    #         message = error_content.get('message')
    #     if message:
    #         raise exceptions.EccClientException(status_code=status_code,
    #                                                 message=message)
    #
    # # If we end up here the exception was not a neutron error
    # msg = "%s-%s" % (status_code, error_content)
    # raise exceptions.EccClientException(status_code=status_code,
    #                                         message=msg)


class APIParamsCall(object):
    """A Decorator to add support for format and tenant overriding and filters.
    """
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
    """Client for the OpenStack Ecc v2.0 API.

    :param string username: Username for authentication. (optional)
    :param string user_id: User ID for authentication. (optional)
    :param string password: Password for authentication. (optional)
    :param string token: Token for authentication. (optional)
    :param string tenant_name: Tenant name. (optional)
    :param string tenant_id: Tenant id. (optional)
    :param string auth_strategy: 'keystone' by default, 'noauth' for no
                                 authentication against keystone. (optional)
    :param string auth_url: Keystone service endpoint for authorization.
    :param string service_type: Network service type to pull from the
                                keystone catalog (e.g. 'network') (optional)
    :param string endpoint_type: Network service endpoint type to pull from the
                                 keystone catalog (e.g. 'publicURL',
                                 'internalURL', or 'adminURL') (optional)
    :param string region_name: Name of a region to select when choosing an
                               endpoint from the service catalog.
    :param string endpoint_url: A user-supplied endpoint URL for the neutron
                            service.  Lazy-authentication is possible for API
                            service calls if endpoint is set at
                            instantiation.(optional)
    :param integer timeout: Allows customization of the timeout for client
                            http requests. (optional)
    :param bool insecure: SSL certificate validation. (optional)
    :param bool log_credentials: Allow for logging of passwords or not.
                                 Defaults to False. (optional)
    :param string ca_cert: SSL CA bundle file to use. (optional)
    :param integer retries: How many times idempotent (GET, PUT, DELETE)
                            requests to Ecc server should be retried if
                            they fail (default: 0).
    :param bool raise_errors: If True then exceptions caused by connection
                              failure are propagated to the caller.
                              (default: True)
    :param session: Keystone client auth session to use. (optional)
    :param auth: Keystone auth plugin to use. (optional)

    Example::

        from eccclient.v1_0 import client
        ecc = client.Client(username=USER,
                                password=PASS,
                                tenant_name=TENANT_NAME,
                                auth_url=KEYSTONE_URL)

        nets = ecc.list_networks()
        ...

    """

    # API has no way to report plurals, so we have to hard code them
    # This variable should be overridden by a child class.
    EXTED_PLURALS = {}

    def __init__(self, **kwargs):
        """Initialize a new client for the Ecc v2.0 API."""
        super(ClientBase, self).__init__()
        self.retries = kwargs.pop('retries', 0)
        self.raise_errors = kwargs.pop('raise_errors', True)
        self.httpclient = client.construct_http_client(**kwargs)
        self.version = ECC_VERSION  # '2.0'
        self.format = 'json'
        self.action_prefix = ACTION_PREFIX  # "/v%s" % (self.version)
        self.retry_interval = 1

    def _handle_fault_response(self, status_code, response_body):
        # Create exception with HTTP status code and message
        _logger.debug("Error message: %s", response_body)
        # Add deserialized error message to exception arguments
        try:
            des_error_body = self.deserialize(response_body, status_code)
        except Exception:
            # If unable to deserialized body it is probably not a
            # Ecc error
            des_error_body = {'message': response_body}
        # Raise the appropriate exception
        exception_handler_v10(status_code, des_error_body)

    def do_request(self, method, action, body=None, headers=None, params=None, no_body=False):
        # Add format and tenant_id
        if ECC_FORMAT:
            action += ".%s" % ECC_FORMAT
        # action += ".%s" % self.format
        if ACTION_PREFIX:
            action = self.action_prefix + action
        # action = self.action_prefix + action

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
            # SG-430対応
            # CICののPUTにおいてレスポンスが返らない仕様となっているためその処理を追加
            if not no_body:
                return self.deserialize(replybody, status_code)
            else:
                return self.deserialize('{}', status_code)
        else:
            if not replybody:
                replybody = resp.reason
            self._handle_fault_response(status_code, replybody)

    def get_auth_info(self):
        return self.httpclient.get_auth_info()

    def serialize(self, data):
        """Serializes a dictionary into either XML or JSON.

        A dictionary with a single key can be passed and it can contain any
        structure.
        """
        if data is None:
            return None
        elif type(data) is dict:
            return serializer.Serializer(
                self.get_attr_metadata()).serialize(data, self.content_type())
        else:
            raise Exception(_("Unable to serialize object of type = '%s'") %
                            type(data))

    def deserialize(self, data, status_code):
        """Deserializes an XML or JSON string into a dictionary."""
        if status_code == 204:
            return data
        return serializer.Serializer(self.get_attr_metadata()).deserialize(
            data, self.content_type())['body']

    def get_attr_metadata(self):
        if self.format == 'json':
            return {}
        old_request_format = self.format
        self.format = 'json'
        self.EXTED_PLURALS.update(constants.PLURALS)
        return {'plurals': self.EXTED_PLURALS,
                'xmlns': constants.XML_NS_V20}

    def content_type(self, _format=None):
        """Returns the mime-type for either 'xml' or 'json'.

        Defaults to the currently set format.
        """
        _format = _format or self.format
        return "application/%s" % _format

    def retry_request(self, method, action, body=None,
                      headers=None, params=None, no_body=False):
        """Call do_request with the default retry configuration.

        Only idempotent requests should retry failed connection attempts.
        :raises: ConnectionFailed if the maximum # of retries is exceeded
        """
        max_attempts = self.retries + 1
        for i in range(max_attempts):
            try:
                return self.do_request(method, action, body=body,
                                       headers=headers, params=params, no_body=no_body)
            except exceptions.ConnectionFailed:
                # Exception has already been logged by do_request()
                if i < self.retries:
                    _logger.debug('Retrying connection to BHEC and Colocation service')
                    time.sleep(self.retry_interval)
                elif self.raise_errors:
                    raise

        if self.retries:
            msg = (_("Failed to connect to Ecc server after %d attempts")
                   % max_attempts)
        else:
            msg = _("Failed to connect Ecc server")

        raise exceptions.ConnectionFailed(reason=msg)

    def delete(self, action, body=None, headers=None, params=None):
        return self.retry_request("DELETE", action, body=body,
                                  headers=headers, params=params)

    def get(self, action, body=None, headers=None, params=None):
        return self.retry_request("GET", action, body=body,
                                  headers=headers, params=params)

    def post(self, action, body=None, headers=None, params=None):
        # Do not retry POST requests to avoid the orphan objects problem.
        return self.do_request("POST", action, body=body,
                               headers=headers, params=params)

    def put(self, action, body=None, headers=None, params=None, no_body=False):
        return self.retry_request("PUT", action, body=body,
                                  headers=headers, params=params, no_body=no_body)

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


def convert_value_to_integer(body):
    new_body = dict()
    for k, v in body.items():
        if k in ['server_segment_nbr', 'colo_vlan']:
            new_body.update({k: int(v)})
        else:
            new_body.update({k: v})
    return new_body


class Client(ClientBase):

    # Operations
    # order_status_path = "/operations/%s" # {operation_id} for Show
    operations_path = "/operations"  # for List
    operation_singular_path = "/operations/%s"

    # NGC_Datacenters(to get dc tag, name pair)
    ngc_datacenters_private_path = "/private/ngc_datacenters"  # for List

    # NGC_Datacenters(to get MCLAG Info)
    datacenters_path = "/datacenters"  # {cic_domain_id} for List

    # EC_Services
    ec_services_path = "/ec_services/%s"  # {service_id} for Show
    ec_service_path = "/ec_services/%s/server_segments"  # {service_id} for List

    # ESI_Networks
    esi_networks_path = "/esi_networks?tenant_id=%s"  # {tenant_id} for List

    # mCIC
    mcic_list_path = "/mCICs?tenant_id=%s"  # {tenant_id}  for List
    mcic_create_path = "/mCICs"  # for Create
    mcic_singular_path = "/mCICs/%s"  # {mcic_id} for Show, Update and Delete

    # CIC
    cic_plural_path = "/mCICs/%s/CICs"  # {mcic_id} for List and Create
    cic_singular_path = "/mCICs/%s/CICs/%s"  # {mcic_id} {cic_id} for Show,Update and Delete

    mcic_operation_path = "/operations?mcic_id=%s"
    cic_operation_path = "/operations?cic_id=%s"

    # API has no way to report plurals, so we have to hard code them
    EXTED_PLURALS = {}
    extensions_path = "/extensions"
    extension_path = "/extensions/%s"

    #
    # Operations
    #

    @APIParamsCall
    def list_operations(self, **_params):
        query = ""
        if 'mcic_id' in _params:
            query = "mcic_id=%s" % _params["mcic_id"]

        if 'cic_id' in _params:
            query = "cic_id=%s" % _params["cic_id"]

        query_url = "%s?%s" % (self.operations_path, query)
        operations = self.get(query_url)
        return operations

    @APIParamsCall
    def show_operation(self, operation_id, **_params):
        return self.get(self.operation_singular_path % operation_id, params=_params)

    @APIParamsCall
    def show_latest_task(self, **_params):
        """Fetche information of a certain Order Status."""
        kwargs = dict()
        if 'mcic_id' in _params:
            kwargs.update({'mcic_id': _params['mcic_id']})

        if 'cic_id' in _params:
            kwargs.update({'cic_id': _params['cic_id']})

        operations = self.get(self.operations_path, params=_params)

        # 配列内要素の、receipt_date属性をstrptimeした値(つまりdatetime Obj)
        # でソートし、その冒頭要素(=最新タスク)の状態を返却
        s_operations = sorted(
            operations,
            key=lambda x: datetime.strptime(x['receipt_date'],
                                            '%Y-%m-%d %H:%M:%S'),
            reverse=True
        )

        # CICの場合
        if 'cic_id' in _params.keys():
            id_type = 'cic_id'
            result_ops = [s_op for s_op in s_operations
                          if s_op.get('cic_id') == _params['cic_id']]

        # mCICの場合
        if 'cic_id' not in _params.keys() and 'mcic_id' in _params.keys():
            id_type = 'mcic_id'
            result_ops = [s_op for s_op in s_operations
                          if s_op.get('mcic_id') == _params['mcic_id']]

        # Example of operation response
        # [{u'cic_id': u'CIC-JP-A0000000-0001',
        #   u'user_id': u'9053b0fc-7107-47d6-b719-0b6b783031bb',
        #   u'operation_body': {},
        #   u'error_messages': [],
        #   u'receipt_date': u'2015-07-01 00:00:00',
        #   u'operation_status': u'success',
        #   u'operation_type': u'mCIC Create',
        #   u'operation_id': u'OP-mCIC-CIC-JP-A0000000-0001-00001',
        #   u'user_name': u'USER-0001'}]
        try:
            return result_ops[0]
        except Exception:
            # オペレーションが存在しない場合
            d = {id_type: _params[id_type],
                 'operation_status': u'success', }
            return d

    #
    # NGC Datacenters
    #

    # get private info(tag and name pair)
    @APIParamsCall
    def list_ngc_datacenters_private_info(self, **_params):
        """Fetches all NGC Data-Centers."""
        return self.get(self.ngc_datacenters_private_path, params=_params)

    @APIParamsCall
    def list_datacenters(self, **_params):
        """Fetches a list of all datacenters in EC Data-Centers."""
        dc_type = _params.get('dc_type')
        dcs = self.get(self.datacenters_path, params=_params)
        return dcs.get('dc_info').get(dc_type.lower())

    #
    # EC Service
    #
    @APIParamsCall
    # Original name is show_ec_datacenter
    # def show_ec_datacenter(self, service_id, **_params):
    def show_ec_service(self, service_id, **_params):
        """Fetche information of a certain service_id in EC Data-Services."""
        return self.get(self.ec_services_path % service_id, params=_params)

    @APIParamsCall
    def list_server_segments(self, service_id, **_params):
        """Fetches a list of all server segments by service_id in EC Data-Services."""
        return self.get(self.ec_service_path % service_id, params=_params)

    #
    # ESI networks
    #
    @APIParamsCall
    def list_esi_networks(self, tenant_id, **_params):
        """Fetches a list of all esi networks in ESI Controller."""
        return self.get(self.esi_networks_path % tenant_id, params=_params)

    #
    # mCIC
    #
    @APIParamsCall
    def list_mcics(self, tenant_id, **_params):
        """Fetches a list of all MCICs in a certen tenant."""
        return self.get(self.mcic_list_path % tenant_id, params=_params)

    @APIParamsCall
    def create_mcic(self, body=None, *args, **_params):
        """Creates a new MCIC."""
        return self.post(self.mcic_create_path, body=body)

    @APIParamsCall
    def show_mcic(self, mcic_id, **_params):
        """Fetche information of a certain mcic_id in MCIC."""
        return self.get(self.mcic_singular_path % mcic_id, params=_params)

    @APIParamsCall
    def update_mcic(self, body=None, mcic_id="", *args, **_params):
        """Updates a mcic."""
        return self.put(self.mcic_singular_path % mcic_id, body=body)

    @APIParamsCall
    def delete_mcic(self, mcic_id, **params):
        """Deletes a mcic."""
        return self.delete(self.mcic_singular_path % mcic_id)

    #
    # CIC
    #
    @APIParamsCall
    def list_cics(self, mcic_id, **_params):
        """Fetches a list of all CICs in a certen MCIC."""
        return self.get(self.cic_plural_path % mcic_id, params=_params)

    @APIParamsCall
    def create_cic(self, body=None, mcic_id="", *args, **_params):
        """Creates a new CIC in a certain MCIC."""
        return self.post(self.cic_plural_path % mcic_id, body=convert_value_to_integer(body))

    @APIParamsCall
    def show_cic(self, mcic_id, cic_id, **_params):
        """Fetche information of a certain cic_id in a certain MCIC."""
        return self.get(self.cic_singular_path % (mcic_id, cic_id), params=_params)

    @APIParamsCall
    def update_cic(self, body=None, mcic_id="", cic_id="", *args, **_params):
        """Updates a cic in a certain MCIC."""
        # return self.put(self.cic_singular_path % (mcic_id, cic_id), body=body)
        return self.put(self.cic_singular_path % (mcic_id, cic_id), body=body, no_body=True)

    @APIParamsCall
    def delete_cic(self, mcic_id, cic_id, **_params):
        """Deletes a cic in a certain MCIC."""
        return self.delete(self.cic_singular_path % (mcic_id, cic_id))

    @APIParamsCall
    def list_operations(self, **_params):
        return self.get(self.operations_path, params=_params)

    @APIParamsCall
    def show_mcic_operation(self, mcic_id="", **_params):
        return self.get(self.mcic_operation_path % mcic_id, params=_params)

    @APIParamsCall
    def show_cic_operation(self, cic_id="", **_params):
        return self.get(self.cic_operation_path % cic_id, params=_params)

    @APIParamsCall
    def list_extensions(self, **_params):
        """Fetch a list of all exts on server side."""
        return self.get(self.extensions_path, params=_params)
