# -*- coding: utf-8 -*-

import six
try:
    from urllib import urlencode
except ImportError:
    from six.moves.urllib.parse import urlencode

from .. import base


# Valid sort directions and client sort keys
SORT_DIR_VALUES = ('asc', 'desc')
SORT_KEY_VALUES = ('id', 'status', 'size', 'availability_zone', 'name',
                   'bootable', 'created_at')
# Mapping of client keys to actual sort keys
SORT_KEY_MAPPINGS = {'name': 'display_name'}


class Volume(base.Resource):
    """A volume is an extra block level storage to the OpenStack instances."""
    def __repr__(self):
        return "<Volume: %s>" % self.id

    def delete(self):
        """Delete this volume."""
        self.manager.delete(self)

    def update(self, **kwargs):
        """Update the name or description for this volume."""
        self.manager.update(self, **kwargs)


class VolumeManager(base.ManagerWithFind):
    """Manage :class:`Volume` resources."""
    resource_class = Volume

    def create(self,
               size,
               # network,
               # volume_type_id,
               name=None,
               description=None,
               iops_per_gb=None,
               initiator_iqns=None,
               throughput=None,
               metadata=None,
               virtual_storage_id=None,
               availability_zone=None):
        """Creates a volume.

        :param size: Size of volume in GB
        :param name: Name of the volume
        :param description: Description of the volume
        :param volume_type: Type of volume
        :param project_id: Project id derived from context
        :param availability_zone: Availability Zone to use
        :rtype: :class:`Volume`
       """
        if metadata is None:
            volume_metadata = {}
        else:
            volume_metadata = metadata

        body_volume = {
            'name': name,
            'description': description,
            'size': size,
            'iops_per_gb': iops_per_gb,
            'initiator_iqns': initiator_iqns,
            # 'metadata': volume_metadata,
            # 'volume_type_id': volume_type_id,
            'availability_zone': availability_zone,
            'throughput': throughput,
            'virtual_storage_id': virtual_storage_id,
            # 'network': network
        }

        body = {'volume': {}}

        for k, v in body_volume.items():
            if v is None:
                continue
            if v == {}:
                continue

            body['volume'].update({k: v})

        return self._create('/volumes', body, 'volume')

    def get(self, volume_id):
        """Get a volume.

        :param volume_id: The ID of the volume to get.
        :rtype: :class:`Volume`
        """
        # # TODO SG-822 WA
        # _vol_data = self._list("/volumes/%s" % volume_id, "volume")
        # if isinstance(_vol_data, list):
        #     return _vol_data[0]
        # else:
        #     return _vol_data
        # TODO SG-822 ORIG
        # return self._get("/volumes/%s" % volume_id, "volume")
        #
        # SG-1015 リスト/オブジェクト双方適合バージョン
        try:
            return self._get("/volumes/%s" % volume_id, "volume")
        except Exception:
            vl = self._list("/volumes/%s" % volume_id, "volume")
            if len(vl) > 0:
                return vl[0]
            else:
                return

    def _format_sort_param(self, sort):
        """Formats the sort information into the sort query string parameter.

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
        """
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
        """Lists all volumes.

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

        return self._list("/volumes%s%s" % (detail, query_string),
                          "volumes", limit=limit)

    def delete(self, volume):
        """Delete a volume.

        :param volume: The :class:`Volume` to delete.
        """
        return self._delete("/volumes/%s" % base.getid(volume))

    def update(self, volume, **kwargs):
        """Update the name or description for a volume.

        :param volume: The :class:`Volume` to update.
        """
        if not kwargs:
            return
        if kwargs.get("initiator_iqns"):
            iqns = kwargs.get("initiator_iqns")
            kwargs["initiator_iqns"] = [iqn for iqn in iqns if iqn != '']

        body = {"volume": kwargs}

        return self._update("/volumes/%s" % base.getid(volume), body, "volume")

    def _action(self, action, volume, info=None, **kwargs):
        """Perform a volume "action."
        """
        body = {action: info}
        self.run_hooks('modify_body_for_action', body, **kwargs)
        url = '/volumes/%s/action' % base.getid(volume)
        return self.api.client.post(url, body=body)
