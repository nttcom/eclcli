from .. import base


class UEFI(base.Resource):
    NAME_ATTR = 'display_name'

    def __repr__(self):
        return "<UEFI: %s>" % self.updated


class UEFIManager(base.Manager):
    resource_class = UEFI

    def get(self, server_id, ):
        url = "/servers/%s/uefi" % server_id
        return self._get(url, "uefi")

    def update(self, server_id, body):
        url = "/servers/%s/uefi" % server_id
        return self._update(url, body, "uefi")
