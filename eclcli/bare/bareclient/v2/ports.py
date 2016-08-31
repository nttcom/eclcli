from .. import base


class NicPhysicalPort(base.Resource):
    NAME_ATTR = 'display_name'

    def __repr__(self):
        return "<NicPhysicalPort: %s>" % self.id


class NicPhysicalPortManager(base.Manager):
    resource_class = NicPhysicalPort

    def get(self, server_id, port_id):
        url = "/servers/%s/nic_physical_ports/%s" % (server_id,port_id)
        return self._get(url, "nic_physical_port")

    def list(self, server_id):
        url = "/servers/%s/nic_physical_ports" % server_id
        return self._list(url, "nic_physical_ports")
