#
# Copyright 2013 Red Hat, Inc
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from .. import base
from ..v2 import options


class Meter(base.Resource):
    def __repr__(self):
        return "<Meter %s>" % self._info


class MeterManager(base.Manager):
    resource_class = Meter

    def list(self, q=None, page=None, per_page=None, unique=False):
        path = '/v2/meters'
        params = []

        if page:
            params.append('page=%s' % str(page))

        if per_page:
            params.append('per_page=%s' % str(per_page))

        if unique:
            params.append('unique=%s' % str(unique))
        path = options.build_url(path, q, params)
        return self._list(path)

    def create(self,
               custom_meter_name,
               project_id,
               namespace,
               resource_id,
               counter_name,
               counter_type,
               counter_unit,
               display_name,
               timestamp,
               counter_volume,
               recorded_at):
        path = '/v2/meters'
        path += '/' + str(custom_meter_name)
        body = {
            "counter_name": counter_name,
            "resource_id": resource_id,
        }
        if project_id:
            body.update({"project_id": project_id})
        if counter_type:
            body.update({"counter_type": counter_type})
        if counter_unit:
            body.update({"counter_unit": counter_unit})
        if display_name:
            body.update({"resource_metadata": {"display_name": display_name}})
        if display_name:
            body.update({"timestamp": timestamp})
        if counter_volume:
            body.update({"counter_volume": counter_volume})
        if recorded_at:
            body.update({"recorded_at": recorded_at})
        if namespace:
            body.update({"namespace": namespace})
        body = [body]

        return self._create(path, body)
