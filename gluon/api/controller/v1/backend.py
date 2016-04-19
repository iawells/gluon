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
import logging as log
log.basicConfig(level=log.DEBUG)

from pecan import rest
from oslo_log import log as logging
import wsmeext.pecan as wsme_pecan
import wsme
from gluon.api import base
from wsme import types as wtypes
from gluon.api.controller.v1 import types
from gluon.objects.backend import Backend as DB_Backend
from gluon.api.controller.v1.port import Port
from gluon.common import exception
from gluon.core.manager import gluon_core_manager

LOG = logging.getLogger(__name__)

class Backend(base.APIBase):
    """API representation of a Backend.

    This class enforces type checking and value constraints, and converts
    between the internal object model and the API representation of a port.
    """

    name = wtypes.StringType()
    service_type = wtypes.StringType()
    url = wtypes.StringType()

    def __init__(self, obj_port):
        real_obj_port_dic = obj_port.as_dict()
        for field in DB_Backend.fields:
            # Skip fields we do not expose.
            if not hasattr(self, field):
                continue
            setattr(self, field, real_obj_port_dic.get(field, wtypes.Unset))


class BackendList(base.APIBase):
    backends = [Backend]

    def __init__(self, backend_list):
        setattr(self, 'backends', [Backend(backend)
                                   for backend in backend_list])


class BackendController(rest.RestController):
    """Version 1 API port controller."""

    @wsme_pecan.wsexpose(BackendList)
    def get_all(self):
        """Returns information about the given port.

        :param uuid: UUID of a port.
        """
        return BackendList(DB_Backend().list())

    @wsme_pecan.wsexpose(Backend, types.uuid)
    def get_one(self, uuid):
        """Returns information about the given port.

        :param uuid: UUID of a port.
        """
        return Backend(DB_Backend().get_by_uuid(uuid))

    #@wsme.signature(Backend, body=Backend,
    #                     status_code=201)
    #def create_backend(self, data):
    #    gluon_core_manager.create_backend(name, service_type, url)

    @wsme_pecan.wsexpose(Port, types.uuid, wtypes.Enum(str, 'ports'), types.uuid)
    def post(self, backend_id, object_type, id):
        """Create a new object of object_type.

        :param backend_id: The backend to create this object.
        :param object_type: Which kind of object shall be created. Possible:
                            [Ports,]
        """
        if object_type == 'ports':
            gluon_core_manager.create_port(backend_id, id)
            # TODO return port
        else:
            raise exception.NotCreateAble(type=object_type,
                                          object='Backends')
