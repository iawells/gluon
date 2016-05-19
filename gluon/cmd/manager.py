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


class GluonManager(ApiManager):
    def __init__(self):
        # TODO
        # backend_manager = BackendBase.Manager(app.config)
        self.gluon_objects = {}
        super(GluonManager, self).__init__()

    def create_ports(self, port):
        owner = port.owner
        LOG.debug('Creating a new port for backend %s' % owner)
        backend_class = self.get_gluon_object('GluonServiceBackend')
        backend = backend_class.get_by_name(owner)
        if not backend:
            raise exception.BackendDoesNotExsist(name=owner)
        port.create()
        return port

    def create_backends(self, backend):
        backend.create()
        return backend

    def destroy_backends(self, backend_name):
        raise NotImplementedError

    def _get_backend_of_port(self, uuid):
        return self.get_gluon_object('GluonInternalPort').get_by_uuid(uuid).owner

    def bind_ports(self, uuid, args):
        binding_profile = {
            'pci_profile': args['pci_profile'],
            'rxtx_factor': args['rxtx_factor']
            # TODO add negotiation here on binding types that are valid
            # (requires work in Nova)
        }
        backend = self._get_backend_of_port(uuid)
        accepted_binding_type = \
            self._do_backend_bind(backend, uuid,
                                  args['device_owner'], args['zone'],
                                  args['device_id'], args['host'],
                                  binding_profile)
        # TODO accepted binding type should be returned to the caller

    def _do_backend_bind(self, backend, port_id, device_owner, zone, device_id,
                         host, binding_profile):
        """Helper function to get a port bound by the backend.

        Once bound, the port is owned by the network service and cannot be
        rebound by that service or any other without unbinding first.

        Binding consists of the compute and network services agreeing a
        drop point; the compute service has previously set binding
        requirements on the port, and at this point says where the port
        must be bound (the host); the network service will work out what
        it can achieve and set information on the port indicating the drop
        point it has chosen.

        Typically there is some prior knowledge on both sides of what
        binding types will be acceptable, so this process could be
        improved.
        """

        logger.debug('Binding port %s on backend %s: compute: %s/%s/%s location %s'
                     % (port_id, backend['name'], device_owner,
                        zone, device_id, host))
        driver = self.backend_manager.get_backend_driver(backend)
        # TODO these are not thoroughly documented or validated and are a
        # part of the API.  Write down what the values must be, must mean
        # and how the backend can use them.
        driver.bind(port_id,
                    device_owner, zone, device_id,
                    host, binding_profile)

        # TODO required?  Do we trust the backend to set this?
        ports[port_id]['zone'] = zone

    def unbind_ports(self, uuid):
        backend = self._get_backend_of_port(uuid)
        # Not very distributed-fault-tolerant, but no retries yet
        self._do_backend_unbind(backend, uuid)

    def _do_backend_unbind(self, backend, port_id):
        """Helper function to get a port unbound from the backend.

        Once unbound, the port becomes ownerless and can be bound by
        another service.  When unbound, the compute and network services
        have mutually agreed to stop exchanging packets at their drop
        point.

        """

        driver = self.backend_manager.get_backend_driver(backend)
        driver.unbind(port_id)


