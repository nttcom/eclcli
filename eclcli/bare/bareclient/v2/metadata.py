from .. import base


class Metadata(base.Resource):
    NAME_ATTR = 'display_name'

    def __repr__(self):
        return "<Metadata>"


class MetadataManager(base.Manager):
    resource_class = Metadata

    def get(self, server_id,key):
        url = "/servers/%s/metadata/%s" % (server_id,key)
        return self._get(url, "metadata")

    def delete(self, server_id,key):
        url = "/servers/%s/metadata/%s" % (server_id,key)
        return self._delete(url)

    def list(self, server_id):
        url = "/servers/%s/metadata" % server_id
        return self._get(url, "metadata")

    def update(self, server_id, key, body):
        url = "/servers/%s/metadata/%s" % (server_id,key)
        return self._update(url, body, "metadata")

# Temporary bug fix , Currently update is replacing the metadata and create is merging the data
    def replace(self, server_id, body):
        url = "/servers/%s/metadata" % server_id
        return self._update(url, body, "metadata")

    def merge(self, server_id, body):
        url = "/servers/%s/metadata" % server_id
        return self._create(url, body, "metadata")
