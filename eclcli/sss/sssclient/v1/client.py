import logging
import time

import requests
import six.moves.urllib.parse as urlparse

from .. import SSS_VERSION
from .. import SSS_FORMAT
from .. import ACTION_PREFIX
from .. import client
from ..common import constants
from ..common import exceptions
from ..common import serializer
from ..common import utils
from ..i18n import _

_logger = logging.getLogger(__name__)


def exception_handler_v10(status_code, error_content):
    """Exception handler for API v1.0 client.

    This routine generates the appropriate SSS exception according to
    the contents of the response body.

    :param status_code: HTTP error status code
    :param error_content: deserialized body of error response
    """
    error_dict = None
    if isinstance(error_content, dict):
        error_dict = error_content.get('SSSError')
    # Find real error type
    bad_err_error_flag = False
    if error_dict:
        # If SSS key is found, it will definitely contain
        # a 'message' and 'type' keys?
        try:
            error_type = error_dict['type']
            error_message = error_dict['message']
            if error_dict['detail']:
                error_message += "\n" + error_dict['detail']
        except Exception:
            bad_err_error_flag = True
        if not bad_err_error_flag:
            # If corresponding exception is defined, use it.
            client_exc = getattr(exceptions, '%sClient' % error_type, None)
            # Otherwise look up per status-code client exception
            if not client_exc:
                client_exc = exceptions.HTTP_EXCEPTION_MAP.get(status_code)
            if client_exc:
                raise client_exc(message=error_message,
                                 status_code=status_code)
            else:
                raise exceptions.SSSClientException(
                    status_code=status_code, message=error_message)
        else:
            raise exceptions.SSSClientException(status_code=status_code,
                                                message=error_dict)
    else:
        message = None
        if isinstance(error_content, dict):
            message = error_content.get('message')
        if message:
            raise exceptions.SSSClientException(status_code=status_code,
                                                message=message)

    # If we end up here the exception was not a neutron error
    msg = "%s-%s" % (status_code, error_content)
    raise exceptions.SSSClientException(status_code=status_code,
                                        message=msg)


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
    """Client for the OpenStack SSS v1.0 API.

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
                            requests to SSS server should be retried if
                            they fail (default: 0).
    :param bool raise_errors: If True then exceptions caused by connection
                              failure are propagated to the caller.
                              (default: True)
    :param session: Keystone client auth session to use. (optional)
    :param auth: Keystone auth plugin to use. (optional)

    Example::

        from sssclient.v1_0 import client
        sss = client.Client(username=USER,
                                password=PASS,
                                tenant_name=TENANT_NAME,
                                auth_url=KEYSTONE_URL)

        nets = sss.list_networks()
        ...

    """

    # API has no way to report plurals, so we have to hard code them
    # This variable should be overridden by a child class.
    EXTED_PLURALS = {}

    def __init__(self, **kwargs):
        """Initialize a new client for the SSS v1.0 API."""
        super(ClientBase, self).__init__()
        self.retries = kwargs.pop('retries', 0)
        self.raise_errors = kwargs.pop('raise_errors', True)
        self.httpclient = client.construct_http_client(**kwargs)
        self.version = SSS_VERSION
        self.format = SSS_FORMAT
        self.action_prefix = ACTION_PREFIX
        self.retry_interval = 1

    def _handle_fault_response(self, status_code, response_body):
        # Create exception with HTTP status code and message
        _logger.debug("Error message: %s", response_body)
        # Add deserialized error message to exception arguments
        try:
            des_error_body = self.deserialize(response_body, status_code)
        except Exception:
            # If unable to deserialized body it is probably not a
            # SSS error
            des_error_body = {'message': response_body}
        # Raise the appropriate exception
        exception_handler_v10(status_code, des_error_body)

    def do_request(self, method, action, body=None, headers=None, params=None):
        # Add format and tenant_id
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
            return self.deserialize(replybody, status_code)
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
        exts = self.list_extensions()['extensions']
        self.format = old_request_format
        ns = dict([(ext['alias'], ext['namespace']) for ext in exts])
        self.EXTED_PLURALS.update(constants.PLURALS)
        return {'plurals': self.EXTED_PLURALS,
                'xmlns': constants.XML_NS_V20,
                constants.EXT_NS: ns}

    def content_type(self, _format=None):
        """Returns the mime-type for either 'xml' or 'json'.

        Defaults to the currently set format.
        """
        _format = _format or self.format
        return "application/%s" % _format

    def retry_request(self, method, action, body=None,
                      headers=None, params=None):
        """Call do_request with the default retry configuration.

        Only idempotent requests should retry failed connection attempts.
        :raises: ConnectionFailed if the maximum # of retries is exceeded
        """
        max_attempts = self.retries + 1
        for i in range(max_attempts):
            try:
                return self.do_request(method, action, body=body,
                                       headers=headers, params=params)
            except exceptions.ConnectionFailed:
                # Exception has already been logged by do_request()
                if i < self.retries:
                    _logger.debug('Retrying connection to BHEC and Colocation service')
                    time.sleep(self.retry_interval)
                elif self.raise_errors:
                    raise

        if self.retries:
            msg = (_("Failed to connect to SSS server after %d attempts")
                   % max_attempts)
        else:
            msg = _("Failed to connect SSS server")

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
    #
    # Users
    #
    user_singular_path = "/users/%s"  # {user_id} for Show, Update and Delete
    user_list_path = "/users"  # for List
    user_create_path = "/users"  # for Create

    @APIParamsCall
    def list_users(self, **_params):
        """Fetches a list of all Users of a certain contract_id in SSS."""
        return self.get(self.user_list_path, params=_params)

    @APIParamsCall
    def show_user(self, user_id, **_params):
        """Fetche information of a certain user_id in SSS."""
        return self.get(self.user_singular_path % user_id, params=_params)

    # @APIParamsCall
    # def update_user(self, body=None, user_id="", *args, **_params):
    #     """Update information of a certain user_id in SSS."""
    #     return self.put(self.user_singular_path % (user_id), body=body)

    @APIParamsCall
    def delete_user(self, user_id, **_params):
        """Deletes a certain user in SSS."""
        return self.delete(self.user_singular_path % user_id, params=_params)

    @APIParamsCall
    def create_user(self, body=None, *args, **_params):
        """Creates a certain user in SSS.."""
        return self.post(self.user_create_path, body=body)

    #
    # Tenants
    #
    tenant_singular_path = "/tenants/%s"  # {user_id} for Show, Update and Delete
    tenant_list_path = "/tenants"  # for List
    tenant_create_path = "/tenants"  # for Create

    @APIParamsCall
    def list_tenants(self, **_params):
        """Fetches a list of all Tenants of a certain contract_id in SSS."""
        return self.get(self.tenant_list_path, params=_params)

    @APIParamsCall
    def show_tenant(self, tenant_id, **_params):
        """Fetche information of a certain tenant_id in SSS."""
        return self.get(self.tenant_singular_path % tenant_id, params=_params)

    @APIParamsCall
    def delete_tenant(self, tenant_id, **_params):
        """Deletes a certain tenant in SSS."""
        return self.delete(self.tenant_singular_path % tenant_id, params=_params)

    @APIParamsCall
    def create_tenant(self, body=None, *args, **_params):
        """Creates a certain tenant in SSS.."""
        return self.post(self.tenant_create_path, body=body)

    #
    # Roles
    #
    role_create_path = "/roles"  # for Create
    role_delete_path = "/roles/tenants/%s/users/%s"  # {tenant_id}, {user_id} for Delete

    @APIParamsCall
    def delete_role(self, tenant_id, user_id, **params):
        """Deletes a certain role in SSS."""
        return self.delete(self.role_delete_path % (tenant_id, user_id))

    @APIParamsCall
    def create_role(self, body=None, *args, **_params):
        """Creates a certain role in SSS.."""
        return self.post(self.role_create_path, body=body)

    #
    # API Keypair
    #
    api_keypair_path = "/keys/%s"  # {user_id} for Update

    @APIParamsCall
    def set_api_keypair(self, user_id, *args, **_params):
        """Sets a certain API keypair in SSS."""
        return self.put(self.api_keypair_path % user_id)

    #
    # Channel
    #
    channel_path = "/channels?get_contracts=%s"  # {user_id} for Update

    @APIParamsCall
    def list_channels(self, get_contracts, *args, **_params):
        """List channels in SSS."""
        return self.get(self.channel_path % get_contracts)

    #
    # Contract
    #
    contract_show_path = "/contracts/%s"  # {contract_id} for Show, Delete
    contract_list_path = "/contracts?channel_id=%s"  # {channel_id}  for List
    contract_create_path = "/contracts"  # for Create
    billing_show_path = "/contracts/%s/billing/%s"  # for Show
    with_target_contract = "%s/target_contract/%s"  # for Show billing of each contract

    @APIParamsCall
    def list_contracts(self, channel_id, **_params):
        """Fetches a list of all contracts of a certain channel_id in SSS."""
        return self.get(self.contract_list_path % channel_id, params=_params)

    @APIParamsCall
    def show_contract(self, contract_id, **_params):
        """Fetches information of a certain contract_id in SSS."""
        return self.get(self.contract_show_path % contract_id, params=_params)

    @APIParamsCall
    def delete_contract(self, contract_id, **params):
        """Deletes a certain contract in SSS."""
        return self.delete(self.contract_show_path % contract_id)

    @APIParamsCall
    def create_contract(self, body=None, *args, **_params):
        """Creates a certain contract in SSS.."""
        return self.post(self.contract_create_path, body=body)

    @APIParamsCall
    def show_billing(self, contract_id, target_month, **_params):
        """Fetches information of a certain contract_id in SSS."""
        billing_action = self.billing_show_path % (contract_id, target_month)
        return self.get(billing_action, params=_params)

    #
    # IAM Endpoints
    #
    iam_group_list_path = "/iam/groups"
    iam_group_create_path = "/iam/groups"
    iam_group_delete_path = "/iam/groups/%s"
    iam_group_attach_role_path = "/iam/groups/%s/roles/%s"
    iam_group_attach_user_path = "/iam/groups/%s/users/%s"
    iam_group_detach_role_path = "/iam/groups/%s/roles/%s"
    iam_group_detach_user_path = "/iam/groups/%s/users/%s"
    iam_role_list_path = "/iam/roles"
    iam_role_create_path = "/iam/roles"
    iam_role_show_path = "/iam/roles/%s"
    iam_role_delete_path = "/iam/roles/%s"
    iam_user_list_path = "/iam/groups/%s/users"

    @APIParamsCall
    def iam_group_list(self, contract_id=None):
        url = self.iam_group_list_path
        if contract_id:
            url += "?contract_id=" + contract_id
        return self.get(url)

    @APIParamsCall
    def iam_group_create(self, iam_group_name=None, contract_id=None, description=None):
        body = {"iam_group_name": iam_group_name,
                "contract_id": contract_id,
                "description": description}
        return self.post(self.iam_group_create_path, body=body)

    @APIParamsCall
    def iam_group_delete(self, iam_group_id=None):
        return self.delete(self.iam_group_delete_path % iam_group_id)

    @APIParamsCall
    def iam_group_attach_user(self, iam_group_id=None, iam_user_id=None):
        return self.put(self.iam_group_attach_user_path % (iam_group_id, iam_user_id))

    @APIParamsCall
    def iam_group_detach_user(self, iam_group_id=None, iam_user_id=None):
        return self.delete(self.iam_group_detach_user_path % (iam_group_id, iam_user_id))

    @APIParamsCall
    def iam_group_attach_role(self, iam_group_id=None, iam_role_id=None):
        return self.put(self.iam_group_attach_role_path % (iam_group_id, iam_role_id))

    @APIParamsCall
    def iam_group_detach_role(self, iam_group_id=None, iam_role_id=None):
        return self.delete(self.iam_group_attach_role_path % (iam_group_id, iam_role_id))

    @APIParamsCall
    def iam_role_list(self, contract_id=None):
        url = self.iam_role_list_path
        if contract_id:
            url += "?contract_id=" + contract_id
        return self.get(url)

    def iam_role_show(self, iam_role_id=None):
        return self.get(self.iam_role_show_path % iam_role_id)

    @APIParamsCall
    def iam_role_create(self, iam_role_name=None, contract_id=None,
                        description=None, resources=None):
        body = {"iam_role_name": iam_role_name,
                "contract_id": contract_id,
                "description": description,
                "resources": resources}
        return self.post(self.iam_role_create_path, body=body)

    @APIParamsCall
    def iam_role_delete(self, iam_role_id=None):
        return self.delete(self.iam_role_delete_path % iam_role_id)

    @APIParamsCall
    def iam_user_list(self, iam_group_id=None):
        return self.get(self.iam_user_list_path % iam_group_id)
