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
from gluon.objects.port import Port as DB_Port
from gluon.objects.backend import Backend as DB_Backend
from gluon.common import exception
from oslo_log import log as logging

LOG = logging.getLogger(__name__)


class Manager():

    def __init__(self):
        pass

    def get_port(self, backend=None, service=None, uuid=None):
        port = DB_Port.get_by_uuid(uuid)

        # Update the backend information for this port.  We are
        # not a cache, so we always re-fetch.  TODO though
        # arguably we shouldn't be storing, and we should be
        # verifying that the backend has provided exactly the
        # expected information.
        backend_port_info = \
            do_backend_get_port(backends[port['backend']], id)
        port.update(backend_port_info)

        if backend is not None and port['backend'] == backend:
            return port
        if service is not None and port.get('device_owner') == service:
            return port
        if backend is None and service is None:
            return port

    def create_port(self, backend_name, port):
        LOG.debug('Creating a new port for backend %s' % backend_name)
        backend = DB_Backend.get_by_name(backend_name)
        if not backend:
            raise exception.BackendDoesNotExsist(name=backend_name)
        port.backend_name = backend_name
        port.create()
        return port

    def create_backend(self, backend):
        backend.create()
        return backend

gluon_core_manager = Manager()
