#    Copyright 2016, Ericsson AB
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
from gluon.common import exception
from oslo_log import log as logging
from gluon.core.manager import ApiManager

from gluon.backends import base as BackendBase
# This has to be dne to get the Database Models
# build before the API is build.
# It should be done in a better way.
from gluon.db.sqlalchemy import models

LOG = logging.getLogger(__name__)
logger = LOG


class ProtonManager(ApiManager):
    def __init__(self):
        self.gluon_objects = {}
        super(ProtonManager, self).__init__()

    def create_vpnports(self, obj_class, port):
        port.create()
        return port

    def update_vpnports(self, obj_class, key, new_values):
        return obj_class.update(key, new_values)

    def delete_vpnports(self, obj_class, key):
        return obj_class.delete(key)

    def create_baseports(self, obj_class, port):
        port.create()
        return port

    def update_baseports(self, obj_class, key, new_values):
        return obj_class.update(key, new_values)

    def delete_baseports(self, obj_class, key):
        return obj_class.delete(key)

    def create_vpns(self, obj_class, vpn):
        vpn.create()
        return vpn

    def update_vpns(self, obj_class, key, new_values):
        return obj_class.update(key, new_values)

    def delete_vpns(self, obj_class, key):
        return obj_class.delete(key)

    def create_vpnafconfigs(self, obj_class, vpnafconfig):
        vpnafconfig.create()
        return vpnafconfig

    def update_vpnafconfigs(self, obj_class, key, new_values):
        return obj_class.update(key, new_values)

    def delete_vpnafconfigs(self, obj_class, key):
        return obj_class.delete(key)





