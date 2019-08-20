"""
Server interface.
"""

from .. import base
import six
from six.moves.urllib import parse


def getname(obj):
    """
    Abstracts the common pattern of allowing both an object or an object's NAME
    as a parameter when dealing with relationships.
    """
    try:
        return obj.name
    except AttributeError:
        return obj


class Server(base.Resource):
    HUMAN_ID = True

    def __repr__(self):
        return '<Server: %s>' % getattr(self, 'name', 'unknown-name')

    def delete(self):
        """
        Delete (i.e. shut down and delete the image) this server.
        """
        self.manager.delete(self)

    def update(self, name=None):
        """
        Update the name for this server.

        :param name: Update the server's name.
        """
        self.manager.update(self, name=name)


class ServerManager(base.BootingManagerWithFind):
    resource_class = Server

    def get(self, server_id):
        """
        Get a server.

        :param server_id: ID of the :class:`Server` to get.
        :rtype: :class:`Server`
        """
        return self._get("/servers/%s" % server_id, "server")

    def list(self, detailed=True, search_opts=None, marker=None, limit=None,
             sort_keys=None, sort_dirs=None):
        """
        Get a list of servers.
        :param detailed: Whether to return detailed server info (optional).
        :param search_opts: Search options to filter out servers (optional).
        :param marker: Begin returning servers that appear later in the server
                       list than that represented by this server id (optional).
        :param limit: Maximum number of servers to return (optional).
        :param sort_keys: List of sort keys
        :param sort_dirs: List of sort directions
        :rtype: list of :class:`Server`
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

        # Transform the dict to a sequence of two-element tuples in fixed
        # order, then the encoded string will be consistent in Python 2&3.
        if qparams or sort_keys or sort_dirs:
            # sort keys and directions are unique since the same parameter
            # key is repeated for each associated value
            # (ie, &sort_key=key1&sort_key=key2&sort_key=key3)
            items = list(qparams.items())
            if sort_keys:
                items.extend(('sort_key', sort_key) for sort_key in sort_keys)
            if sort_dirs:
                items.extend(('sort_dir', sort_dir) for sort_dir in sort_dirs)
            new_qparams = sorted(items, key=lambda x: x[0])
            query_string = "?%s" % parse.urlencode(new_qparams)
        else:
            query_string = ""

        detail = ""
        if detailed:
            detail = "/detail"
        return self._list("/servers%s%s" % (detail, query_string), "servers")

    def create(self, name, networks, image_id, flavor_id,
               admin_pass=None, metadata=None, availability_zone=None,
               description=None, **kwargs):
        """
        Create a new server.

        :param name: Something to servername.
        :param password: Something to password for server(option)
        """
        body = {
            "server": {
                'name': name,
                'networks': networks,
                'imageRef': image_id,
                'flavorRef': flavor_id
            }
        }

        if admin_pass:
            body["server"]["adminPass"] = admin_pass

        if metadata:
            body["server"]["metadata"] = metadata

        if availability_zone:
            body["server"]["availability_zone"] = availability_zone

        if description:
            body["server"]["description"] = description

        return self._create("/servers", body, "server")

    def delete(self, server_id):
        """
        Delete (i.e. shut down and delete the image) this server.
        """
        return self._delete("/servers/%s" % server_id)
