from .. import client
from . import availability_zones
from . import flavors
from . import images
from . import keypairs
from . import limits
from . import servers
from . import stocks
from . import uefis
from . import versions
from . import metadata
from . import ports
from .. import SERVICE_TYPE


class Client(object):
    """
    Top-level object to access the NTT Com Cloud Baremetal API.

    Create an instance with your creds::
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
        :param str extensions: Extensions
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

        # NOTE(cyeoh): In the bearclient context (unlike Bear) the
        # project_id is not the same as the tenant_id. Here project_id
        # is a name (what the Bear API often refers to as a project or
        # tenant name) and tenant_id is a UUID (what the Bear API
        # often refers to as a project_id or tenant_id).

        password = api_key
        self.projectid = project_id
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.flavors = flavors.FlavorManager(self)
        # self.flavor_access = flavor_access.FlavorAccessManager(self)
        self.images = images.ImageManager(self)
        self.limits = limits.LimitsManager(self)
        self.servers = servers.ServerManager(self)
        self.metadata = metadata.MetadataManager(self)
        self.versions = versions.VersionManager(self)
        self.ports = ports.NicPhysicalPortManager(self)

        # extensions
        # self.agents = agents.AgentsManager(self)
        # self.dns_domains = floating_ip_dns.FloatingIPDNSDomainManager(self)
        # self.dns_entries = floating_ip_dns.FloatingIPDNSEntryManager(self)
        # self.cloudpipe = cloudpipe.CloudpipeManager(self)
        # self.certs = certs.CertificateManager(self)
        # self.floating_ips = floating_ips.FloatingIPManager(self)
        # self.floating_ip_pools = floating_ip_pools.FloatingIPPoolManager(self)
        # self.fping = fping.FpingManager(self)
        # self.volumes = volumes.VolumeManager(self)
        # self.volume_snapshots = volume_snapshots.SnapshotManager(self)
        # self.volume_types = volume_types.VolumeTypeManager(self)
        self.keypairs = keypairs.KeypairManager(self)
        # self.networks = networks.NetworkManager(self)
        # self.quota_classes = quota_classes.QuotaClassSetManager(self)
        # self.quotas = quotas.QuotaSetManager(self)
        # self.security_groups = security_groups.SecurityGroupManager(self)
        # self.security_group_rules = \
        #     security_group_rules.SecurityGroupRuleManager(self)
        # self.security_group_default_rules = \
        #     security_group_default_rules.SecurityGroupDefaultRuleManager(self)
        # self.usage = usage.UsageManager(self)
        # self.virtual_interfaces = \
        #     virtual_interfaces.VirtualInterfaceManager(self)
        # self.aggregates = aggregates.AggregateManager(self)
        # self.hosts = hosts.HostManager(self)
        # self.hypervisors = hypervisors.HypervisorManager(self)
        # self.hypervisor_stats = hypervisors.HypervisorStatsManager(self)
        # self.services = services.ServiceManager(self)
        # self.fixed_ips = fixed_ips.FixedIPsManager(self)
        # self.floating_ips_bulk = floating_ips_bulk.FloatingIPBulkManager(self)
        self.os_cache = os_cache or not no_cache
        self.availability_zones = availability_zones.AvailabilityZoneManager(self)
        self.stocks = stocks.StockManager(self)
        self.uefis = uefis.UEFIManager(self)
        # self.server_groups = server_groups.ServerGroupsManager(self)

        # Add in any extensions...
        if extensions:
            for extension in extensions:
                if extension.manager_class:
                    setattr(self, extension.name,
                            extension.manager_class(self))

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
