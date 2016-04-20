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
from oslo_log import log as logging
import wsmeext.pecan as wsme_pecan
import wsme
from gluon.api import base
from wsme import types as wtypes
from gluon.api.controller.v1 import types
from gluon.objects.backend import Backend as DB_Backend
from gluon.api.controller.v1.port import Port, PortController
from gluon.common import exception
from gluon.core.manager import gluon_core_manager

LOG = logging.getLogger(__name__)


class Backend(base.APIBaseObject):
    """API representation of a Backend.

    This class enforces type checking and value constraints, and converts
    between the internal object model and the API representation of a Backend.
    """

    name = wtypes.StringType()
    service_type = wtypes.StringType()
    url = wtypes.StringType()

    _DB_object_class = DB_Backend


class BackendList(base.APIBaseList):

    backends = [Backend]

    @classmethod
    def build(cls, db_obj_list):
        obj = cls()
        setattr(obj, 'backends',
                [Backend.build(db_obj)
                 for db_obj in db_obj_list])
        return obj


class BackendController(rest.RestController):
    """Version 1 API Backend controller."""

    ports = PortController()

    @wsme_pecan.wsexpose(BackendList)
    def get_all(self):
        """Returns information about the given port.

        :param uuid: UUID of a port.
        """
        return BackendList.build(DB_Backend().list())

    @wsme_pecan.wsexpose(Backend, types.uuid)
    def get_one(self, uuid):
        """Returns information about the given port.

        :param uuid: UUID of a port.
        """
        return Backend(DB_Backend().get_by_uuid(uuid))

    @wsme_pecan.wsexpose(Backend, body=Backend, template='json',
                         status_code=201)
    def post(self, body):
        # Create a backend
        return Backend.build(gluon_core_manager.create_backend(body.to_db_object())
