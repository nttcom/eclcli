from .. import base


class AvailabilityZone(base.Resource):
    NAME_ATTR = 'display_name'

    def __repr__(self):
        return "<AvailabilityZone: %s>" % self.zoneName


class AvailabilityZoneManager(base.ManagerWithFind):
    """Manage :class:`AvailabilityZone` resources."""
    resource_class = AvailabilityZone

    def list(self, detailed=False):
        """Lists all availability zones.

        :rtype: list of :class:`AvailabilityZone`
        """
        if detailed is True:
            return self._list("/availability_zone/detail",
                              "availabilityZoneInfo")
        else:
            return self._list("/availability_zone", "availabilityZoneInfo")
