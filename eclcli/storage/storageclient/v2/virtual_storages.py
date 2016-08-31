import six
try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

from .. import base


# Valid sort directions and client sort keys
SORT_DIR_VALUES = ('asc', 'desc')
SORT_KEY_VALUES = ('id', 'status', 'name', 'created_at')
# Mapping of client keys to actual sort keys
SORT_KEY_MAPPINGS = {'name': 'display_name'}


class VirtualStorage(base.Resource):
    def __repr__(self):
        return "<VirtualStorage: %s>" % self.id

    def delete(self):
        """Delete this volume."""
        self.manager.delete(self)

    def update(self, **kwargs):
        """Update the name or description for this volume."""
        self.manager.update(self, **kwargs)


class VirtualStorageManager(base.ManagerWithFind):
    """Manage :class:`VirtualStorage` resources."""
    resource_class = VirtualStorage

    def create(self, **kwargs):
        """
        Creates a virtual storage.
        :rtype: :class:`VirtualStorage`
        """
        body = {'virtual_storage': kwargs}

        return self._create('/virtual_storages', body, 'virtual_storage')

    def get(self, virtual_storage_id):
        """
        Get a Virtual Storage.

        :param virtual_storage_id: The ID of the virtual storage to get.
        :rtype: :class:`Volume`
        """
        return self._get("/virtual_storages/%s" % virtual_storage_id, "virtual_storage")

    def _format_sort_param(self, sort):
        '''Formats the sort information into the sort query string parameter.

        The input sort information can be any of the following:
        - Comma-separated string in the form of <key[:dir]>
        - List of strings in the form of <key[:dir]>
        - List of either string keys, or tuples of (key, dir)

        For example, the following import sort values are valid:
        - 'key1:dir1,key2,key3:dir3'
        - ['key1:dir1', 'key2', 'key3:dir3']
        - [('key1', 'dir1'), 'key2', ('key3', dir3')]

        :param sort: Input sort information
        :returns: Formatted query string parameter or None
        :raise ValueError: If an invalid sort direction or invalid sort key is
                           given
        '''
        if not sort:
            return None

        if isinstance(sort, six.string_types):
            # Convert the string into a list for consistent validation
            sort = [s for s in sort.split(',') if s]

        sort_array = []
        for sort_item in sort:
            if isinstance(sort_item, tuple):
                sort_key = sort_item[0]
                sort_dir = sort_item[1]
            else:
                sort_key, _sep, sort_dir = sort_item.partition(':')
            sort_key = sort_key.strip()
            if sort_key in SORT_KEY_VALUES:
                sort_key = SORT_KEY_MAPPINGS.get(sort_key, sort_key)
            else:
                raise ValueError('sort_key must be one of the following: %s.'
                                 % ', '.join(SORT_KEY_VALUES))
            if sort_dir:
                sort_dir = sort_dir.strip()
                if sort_dir not in SORT_DIR_VALUES:
                    msg = ('sort_dir must be one of the following: %s.'
                           % ', '.join(SORT_DIR_VALUES))
                    raise ValueError(msg)
                sort_array.append('%s:%s' % (sort_key, sort_dir))
            else:
                sort_array.append(sort_key)
        return ','.join(sort_array)

    def list(self, detailed=True, search_opts=None, marker=None, limit=None,
             sort_key=None, sort_dir=None, sort=None):
        """
        Lists all virtual storages.

        :param detailed: Whether to return detailed volume info.
        :param search_opts: Search options to filter out volumes.
        :param marker: Begin returning volumes that appear later in the volume
                       list than that represented by this volume id.
        :param limit: Maximum number of volumes to return.
        :param sort_key: Key to be sorted; deprecated in kilo
        :param sort_dir: Sort direction, should be 'desc' or 'asc'; deprecated
                         in kilo
        :param sort: Sort information
        :rtype: list of :class:`Volume`
        """
        if search_opts is None:
            search_opts = {}

        qparams = {}

        for opt, val in six.iteritems(search_opts):
            if val:
                qparams[opt] = val

        if marker:
            qparams['marker'] = marker

        if limit:
            qparams['limit'] = limit

        # sort_key and sort_dir deprecated in kilo, prefer sort
        if sort:
            qparams['sort'] = self._format_sort_param(sort)
        else:
            if sort_key is not None:
                if sort_key in SORT_KEY_VALUES:
                    qparams['sort_key'] = SORT_KEY_MAPPINGS.get(sort_key,
                                                                sort_key)
                else:
                    msg = ('sort_key must be one of the following: %s.'
                           % ', '.join(SORT_KEY_VALUES))
                    raise ValueError(msg)
            if sort_dir is not None:
                if sort_dir in SORT_DIR_VALUES:
                    qparams['sort_dir'] = sort_dir
                else:
                    msg = ('sort_dir must be one of the following: %s.'
                           % ', '.join(SORT_DIR_VALUES))
                    raise ValueError(msg)

        # Transform the dict to a sequence of two-element tuples in fixed
        # order, then the encoded string will be consistent in Python 2&3.
        if qparams:
            new_qparams = sorted(qparams.items(), key=lambda x: x[0])
            query_string = "?%s" % urlencode(new_qparams)
        else:
            query_string = ""

        detail = ""
        if detailed:
            detail = "/detail"

        return self._list("/virtual_storages%s%s" % (detail, query_string),
                          "virtual_storages", limit=limit)

    def delete(self, virtual_storage):
        """
        Delete a virtual storage.

        :param volume: The :class:`VirtualStorage` to delete.
        """
        return self._delete("/virtual_storages/%s" % base.getid(virtual_storage))

    def update(self, virtual_storage, **kwargs):
        """Update the name or description for a volume.

        :param volume: The :class:`Volume` to update.
        """
        if not kwargs:
            return

        body = {"virtual_storage": kwargs}

        return self._update("/virtual_storages/%s" % base.getid(virtual_storage), body, "virtual_storage")
