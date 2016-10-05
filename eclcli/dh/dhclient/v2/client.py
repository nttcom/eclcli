from .. import client
from .. import SERVICE_TYPE
from . import servers
from . import usages
from . import licenses


class Client(object):
    """
    Top-level object to access the OpenStack Compute API.

    Create an instance with your creds::

        >>> client = Client(USERNAME, PASSWORD, PROJECT_ID, AUTH_URL)

    Or, alternatively, you can create a client instance using the
    keystoneclient.session API::

        >>> from keystoneclient.auth.identity import v2
        >>> from keystoneclient import session
        >>> from dhclient.client import Client
        >>> auth = v2.Password(auth_url=AUTH_URL,
                               username=USERNAME,
                               password=PASSWORD,
                               tenant_name=PROJECT_ID)
        >>> sess = session.Session(auth=auth)
        >>> dh = client.Client(VERSION, session=sess)

    Then call methods on its managers::

    It is also possible to use an instance as a context manager in which
    case there will be a session kept alive for the duration of the with
    statement::

    It is also possible to have a permanent (process-long) connection pool,
    by passing a connection_pool=True::
    """

    def __init__(self, username=None, api_key=None, project_id=None,
                 auth_url=None, insecure=False, timeout=None,
                 proxy_tenant_id=None, proxy_token=None, region_name=None,
                 endpoint_type='publicURL', extensions=None,
                 service_type=SERVICE_TYPE, service_name=None,
                 volume_service_name=None, timings=False, bypass_url=None,
                 os_cache=False, no_cache=True, http_log_debug=False,
                 auth_system='keystone', auth_plugin=None, auth_token=None,
                 cacert=None, tenant_id=None, user_id=None,
                 connection_pool=False, session=None, auth=None,
                 **kwargs):
        """
        :param str username: Username
        :param str api_key: API Key
        :param str project_id: Project ID
        :param str auth_url: Auth URL
        :param bool insecure: Allow insecure
        :param float timeout: API timeout, None or 0 disables
        :param str proxy_tenant_id: Tenant ID
        :param str proxy_token: Proxy Token
        :param str region_name: Region Name
        :param str endpoint_type: Endpoint Type
        :param str extensions: Exensions
        :param str service_type: Service Type
        :param str service_name: Service Name
        :param str volume_service_name: Volume Service Name
        :param bool timings: Timings
        :param str bypass_url: Bypass URL
        :param bool os_cache: OS cache
        :param bool no_cache: No cache
        :param bool http_log_debug: Enable debugging for HTTP connections
        :param str auth_system: Auth system
        :param str auth_plugin: Auth plugin
        :param str auth_token: Auth token
        :param str cacert: cacert
        :param str tenant_id: Tenant ID
        :param str user_id: User ID
        :param bool connection_pool: Use a connection pool
        :param str session: Session
        :param str auth: Auth
        """
        # FIXME(comstud): Rename the api_key argument above when we
        # know it's not being used as keyword argument

        # NOTE(cyeoh): In the dhclient context (unlike Dh) the
        # project_id is not the same as the tenant_id. Here project_id
        # is a name (what the Dh API often refers to as a project or
        # tenant name) and tenant_id is a UUID (what the Dh API
        # often refers to as a project_id or tenant_id).

        password = api_key
        self.projectid = project_id
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.servers = servers.ServerManager(self)
        self.usages = usages.UsageManager(self)
        self.licenses = licenses.LicenseManager(self)
        self.os_cache = os_cache or not no_cache

        self.client = client._construct_http_client(
            username=username,
            password=password,
            user_id=user_id,
            project_id=project_id,
            tenant_id=tenant_id,
            auth_url=auth_url,
            auth_token=auth_token,
            insecure=insecure,
            timeout=timeout,
            auth_system=auth_system,
            auth_plugin=auth_plugin,
            proxy_token=proxy_token,
            proxy_tenant_id=proxy_tenant_id,
            region_name=region_name,
            endpoint_type=endpoint_type,
            service_type=service_type,
            service_name=service_name,
            volume_service_name=volume_service_name,
            timings=timings,
            bypass_url=bypass_url,
            os_cache=self.os_cache,
            http_log_debug=http_log_debug,
            cacert=cacert,
            connection_pool=connection_pool,
            session=session,
            auth=auth,
            **kwargs)

    @client._original_only
    def __enter__(self):
        self.client.open_session()
        return self

    @client._original_only
    def __exit__(self, t, v, tb):
        self.client.close_session()

    @client._original_only
    def set_management_url(self, url):
        self.client.set_management_url(url)

    def get_timings(self):
        return self.client.get_timings()

    def reset_timings(self):
        self.client.reset_timings()

    @client._original_only
    def authenticate(self):
        """
        Authenticate against the server.

        Normally this is called automatically when you first access the API,
        but you can call this method to force authentication right now.

        Returns on success; raises :exc:`exceptions.Unauthorized` if the
        credentials are wrong.
        """
        self.client.authenticate()
