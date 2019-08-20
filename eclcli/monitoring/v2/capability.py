#   Copyright 2013 OpenStack Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

from eclcli.common import command
from .. import monitoring_utils
import six


class ListCapability(command.ShowOne):
    """Lists information for API and storage capabilities of the ECL2.0 Monitoring service."""
    def get_parser(self, prog_name):
        parser = super(ListCapability, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        monitoring_client = self.app.client_manager.monitoring

        data = monitoring_client.capabilities.get()
        info = monitoring_utils._tidy_data_info(data._info)
        return zip(*sorted(six.iteritems(info)))
