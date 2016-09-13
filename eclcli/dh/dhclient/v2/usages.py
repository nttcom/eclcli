# -*- encoding: utf-8 -*-

from .. import base
import six
from six.moves.urllib import parse


def getid(obj):
    try:
        return obj.id
    except AttributeError:
        return obj


class Usage(base.Resource):
    HUMAN_ID = True

    def __repr__(self):
        return '<Usage: %s>' % getattr(self, 'name', 'unknown-name')


class UsageManager(base.BootingManagerWithFind):
    resource_class = Usage

    def get_histories(self,usage,search_opts=None):

        if search_opts is None:
           search_opts = {}

        qparams = {}

        for opt, val in six.iteritems(search_opts):
            if val:
                qparams[opt] = val

        # Transform the dict to a sequence of two-element tuples in fixed
        # order, then the encoded string will be consistent in Python 2&3.
        if qparams:
            items = list(qparams.items())
            new_qparams = sorted(items, key=lambda x: x[0])
            query_string = "?%s" % parse.urlencode(new_qparams)
        else:
            query_string = ""
        
        return self._get_histories("/usages/%s/histories%s" % (usage ,query_string), "histories")

    def list(self,search_opts=None):

        if search_opts is None:
            search_opts = {}
        
        qparams = {}

        for opt, val in six.iteritems(search_opts):
            if val:
                qparams[opt] = val

        # Transform the dict to a sequence of two-element tuples in fixed
        # order, then the encoded string will be consistent in Python 2&3.
        if qparams:
            items = list(qparams.items())
            new_qparams = sorted(items, key=lambda x: x[0])
            query_string = "?%s" % parse.urlencode(new_qparams)
        else:
            query_string = ""
 
        return self._list("/usages%s" % (query_string), "usages")
