from .. import base


class Stock(base.Resource):
    NAME_ATTR = 'display_name'

    def __repr__(self):
        return "<Stock: %s>" % self.name


class StockManager(base.Manager):
    resource_class = Stock

    def get(self, flavor_id, availability_zone=None):
        if availability_zone is not None:
            return self._get("/stock?flavor_id=%s&availability_zone=%s" %
                             (flavor_id, availability_zone), "stock")
        return self._get("/stock?flavor_id=%s" %
                         (flavor_id), "stock")
