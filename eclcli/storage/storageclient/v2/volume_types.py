from .. import base


class VolumeType(base.Resource):
    """A Volume Type is the type of volume to be created."""
    def __repr__(self):
        return "<VolumeType: %s>" % self.name


class VolumeTypeManager(base.ManagerWithFind):
    """Manage :class:`VolumeType` resources."""
    resource_class = VolumeType

    def list(self, search_opts=None, is_public=True):
        """Lists all volume types.

        :param search_opts
        :param is_public
        :rtype: list of :class:`VolumeType`.
        """
        query_string = ''
        if not is_public:
            query_string = '?is_public=%s' % is_public
        return self._list("/volume_types%s" % (query_string), "volume_types")

    def get(self, volume_type):
        """Get a specific volume type.

        :param volume_type: The ID of the :class:`VolumeType` to get.
        :rtype: :class:`VolumeType`
        """
        return self._get("/volume_types/%s" % base.getid(volume_type), "volume_type")

