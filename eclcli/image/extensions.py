# -*- coding: utf-8 -*-

import warlock

from glanceclient.common import utils
from glanceclient.v2 import schemas


SCHEMA_JOBS = {
    u'name': u'job',
    u'properties': {
        u'copy_progress': {u'type': u'integer'},
        u'destination_image_id': {u'type': [u'string', u'null']},
        u'destination_region_id': {u'type': u'string'},
        u'destination_tenant_id': {u'type': u'string'},
        u'job_id': {u'type': u'string'},
        u'source_image_id': {u'type': u'string'},
        u'source_image_name': {u'type': u'string'},
        u'source_region_id': {u'type': u'string'},
        u'source_tenant_id': {u'type': u'string'},
        u'status': {u'type': u'string'},
        u'schema': {u'type': u'string'}
    }
}


class Controller(object):
    def __init__(self, http_client, schema_client):
        self.http_client = http_client
        self.schema_client = schema_client

    @utils.memoized_property
    def model(self):
        schema = SCHEMA_JOBS
        return warlock.model_factory(schema, schemas.SchemaBasedModel)

    def copy(self, image_id, tenant_id_dst):
        url = '/v2/extension/image_replicator/jobs'
        body = {'image_id': image_id, 'tenant_id_dst': tenant_id_dst}
        resp, copied_image = self.http_client.post(url, data=body)
        return self.model(copied_image)

    def cancel_copy(self, job_id):
        url = '/v2/extension/image_replicator/jobs/%s' % job_id
        self.http_client.delete(url)

    def detail(self, job_id):
        url = '/v2/extension/image_replicator/jobs/%s' % job_id
        resp, detail = self.http_client.get(url)
        return self.model(detail)

    def list(self):
        url = '/v2/extension/image_replicator/jobs'
        resp, body = self.http_client.get(url)
        for job in body:
            yield self.model(job)

    def list_license_switch_types(self):
        url = '/v2/extension/license_switch/types'
        resp, body = self.http_client.get(url)
        return body['license_switch_types']
