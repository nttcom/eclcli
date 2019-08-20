from .. import base
from six.moves import urllib


class Version(base.Resource):
    NAME_ATTR = 'display_name'

    def __repr__(self):
        return "<Version: %s>" % self.id


class VersionManager(base.Manager):
    resource_class = Version

    def get(self, version, ):
        version_url = None
        # NOTE: "show version" API needs to be accessed without base
        endpoint = self.api.client.get_endpoint()
        url = urllib.parse.urlparse(endpoint)
        version_url = '%s://%s/%s' % (url.scheme, url.netloc, version)
        return self._get(version_url, "version")

    def list(self):
        """List all versions."""

        version_url = None
        # NOTE: "list versions" API needs to be accessed without base
        endpoint = self.api.client.get_endpoint()
        url = urllib.parse.urlparse(endpoint)
        version_url = '%s://%s/' % (url.scheme, url.netloc)
        return self._list(version_url, "versions")
