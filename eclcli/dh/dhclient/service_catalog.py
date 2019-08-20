from . import exceptions
from . import SERVICE_TYPE


class ServiceCatalog(object):
    """Helper methods for dealing with a Keystone Service Catalog."""

    def __init__(self, resource_dict):
        self.catalog = resource_dict

    def get_token(self):
        return self.catalog['access']['token']['id']

    def get_tenant_id(self):
        return self.catalog['access']['token']['tenant']['id']

    def url_for(self, attr=None, filter_value=None,
                service_type=None, endpoint_type='publicURL',
                service_name=None, volume_service_name=None):
        """Fetch the public URL from the Compute service for
        a particular endpoint attribute. If none given, return
        the first. See tests for sample service catalog.
        """
        matching_endpoints = []
        if 'endpoints' in self.catalog:
            # We have a bastardized service catalog. Treat it special. :/
            for endpoint in self.catalog['endpoints']:
                if not filter_value or endpoint[attr] == filter_value:
                    # Ignore 1.0 compute endpoints
                    if endpoint.get("type") == SERVICE_TYPE and \
                            endpoint.get('versionId') in (None, '1.1', '2'):
                        matching_endpoints.append(endpoint)
            if not matching_endpoints:
                raise exceptions.EndpointNotFound()

        # We don't always get a service catalog back ...
        if 'serviceCatalog' not in self.catalog['access']:
            return None

        # Full catalog ...
        catalog = self.catalog['access']['serviceCatalog']

        for service in catalog:
            if service.get("type") != service_type:
                continue

            if (service_name and service_type == SERVICE_TYPE and
                    service.get('name') != service_name):
                continue

            if (volume_service_name and service_type == 'volume' and
                    service.get('name') != volume_service_name):
                continue

            endpoints = service['endpoints']
            for endpoint in endpoints:
                # Ignore 1.0 compute endpoints
                if (service.get("type") == SERVICE_TYPE and
                        endpoint.get('versionId', '2') not in ('1.1', '2')):
                    continue
                if (not filter_value or
                        endpoint.get(attr).lower() == filter_value.lower()):
                    endpoint["serviceName"] = service.get("name")
                    matching_endpoints.append(endpoint)

        if not matching_endpoints:
            raise exceptions.EndpointNotFound()
        elif len(matching_endpoints) > 1:
            raise exceptions.AmbiguousEndpoints(
                endpoints=matching_endpoints)
        else:
            return matching_endpoints[0][endpoint_type]
