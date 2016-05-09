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
# This has to be dne to get the Database Models
# build before the API is build.
# It should be done in a better way.
from gluon.db.sqlalchemy import models

LOG = logging.getLogger(__name__)


class Manager():

    def __init__(self):
        self.gluon_objects = {}

    def get_gluon_object(self, name):
        return self.gluon_objects[name]

    def create_ports(self, port):
        owner = port.owner
        LOG.debug('Creating a new port for backend %s' % owner)
        backend_class = self.get_gluon_object('GluonServiceBackend')
        backend = backend_class.get_by_name(owner)
        if not backend:
            raise exception.BackendDoesNotExsist(name=owner)
        port.create()
        return port

    def destroy_ports(self, uuid):
        raise NotImplementedError

    def update_ports(self, port_update):
        print("Yeah")

    def create_backends(self, backend):
        backend.create()
        return backend

    def destroy_backends(self, backend_name):
        raise NotImplementedError

gluon_core_manager = Manager()
