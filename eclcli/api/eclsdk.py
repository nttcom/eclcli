# -*- coding: utf-8 -*-

import logging
from ecl import connection


LOG = logging.getLogger(__name__)


class ConnectionManager(object):

    def __init__(self, cli_options=None, verify=True):
        self._verify = verify
        self._cacert = None
        if isinstance(verify, bool):
            self._insecure = not verify
        else:
            self._cacert = verify
            self._insecure = False
        self.conn = connection.Connection(
            verify=self._verify,
            cert=self._cacert,
            auth_url=cli_options.auth.get("auth_url"),
            project_id=cli_options.auth.get("project_id"),
            username=cli_options.auth.get("username"),
            password=cli_options.auth.get("password"),
            user_domain_id="default",
            project_domain_id="default")

        root_logger = logging.getLogger('')
        LOG.setLevel(root_logger.getEffectiveLevel())
