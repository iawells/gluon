#    Copyright 2015, Ericsson AB
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

from pecan import rest
import wsmeext.pecan as wsme_pecan
from wsme import types as wtypes

from gluon.api import base
from gluon.api.controller.v1 import types
from gluon.objects.port import Port as DB_Port
from gluon.core.manager import gluon_core_manager


class Port(base.APIBaseObject):
    """API representation of a port.

    This class enforces type checking and value constraints, and converts
    between the internal object model and the API representation of a port.
    """

    uuid = types.uuid
    _DB_object_class = DB_Port


class PortList(base.APIBaseList):

    ports = [Port]

    @classmethod
    def build(cls, db_obj_list):
        obj = cls()
        setattr(obj, 'ports',
                [Port.build(db_obj)
                 for db_obj in db_obj_list])
        return obj


class PortController(rest.RestController):
    """Version 1 API port controller."""

    @wsme_pecan.wsexpose(PortList)
    def get_all(self):
        """Retrieve list of all ports.

        :param port_ident: UUID of a port.
        """
        return PortList(DB_Port.list())

    @wsme_pecan.wsexpose(Port, types.uuid)
    def get_one(self, uuid):
        """Returns information about the given port.

        :param uuid: UUID of a port.
        """
        return Port(DB_Port().get_by_uuid(uuid))

    @wsme_pecan.wsexpose(Port, unicode,
                         body=Port, template='json',
                         status_code=201)
    def post(self, backend_name, body):
        """Create a new object of port.

        :param backend_name: The backend to create this port.
        """
        return Port.build(gluon_core_manager.create_port(backend_name,
                                                         body.to_db_object()))
