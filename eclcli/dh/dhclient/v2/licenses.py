# -*- encoding: utf-8 -*-

from .. import base
import six

try:
    from urllib import urlencode
except ImportError:
    from six.moves.urllib.parse import urlencode


def getid(obj):
    try:
        return obj.id
    except AttributeError:
        return obj


class License(base.Resource):
    HUMAN_ID = True

    def __repr__(self):
        return '<License: %s>' % getattr(self, 'license', 'unknown-name')

    def delete(self):
        self.manager.delete(self)


class LicenseManager(base.BootingManagerWithFind):
    resource_class = License

    def list_license_types(self):
        return self._list("/license_types", "license_types")

    def list(self, search_opts=None):

        if search_opts is None:
            search_opts = {}

        qparams = {}

        for opt, val in six.iteritems(search_opts):
            if val:
                qparams[opt] = val

        # Transform the dict to a sequence of two-element tuples in fixed
        # order, then the encoded string will be consistent in Python 2&3.
        if qparams:
            new_qparams = sorted(qparams.items(), key=lambda x: x[0])
            query_string = "?%s" % urlencode(new_qparams)
        else:
            query_string = ""

        return self._list("/licenses%s" % query_string, "licenses")

    # def get(self, license):
    #     return self._get("/licenses/%s" % getid(license), "license")

    def create(self, license_type):

        body_license_type = {
            "license_type": license_type
        }

        return self._create("/licenses", body_license_type, "license")

    def delete(self, license_id):
        return self._delete("/licenses/%s" % license_id)
