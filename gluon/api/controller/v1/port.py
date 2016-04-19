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


class Port(base.APIBase):
    """API representation of a port.

    This class enforces type checking and value constraints, and converts
    between the internal object model and the API representation of a port.
    """

    id = wtypes.IntegerType(minimum=1)
    uuid = types.uuid

    def __init__(self, obj_port):
        real_obj_port_dic = obj_port.as_dict()
        for field in DB_Port.fields:
            # Skip fields we do not expose.
            if not hasattr(self, field):
                continue
            setattr(self, field, real_obj_port_dic.get(field, wtypes.Unset))


class PortController(rest.RestController):
    """Version 1 API port controller."""

    @wsme_pecan.wsexpose(Port, types.uuid)
    def get(self, uuid):
        """Returns information about the given port.

        :param uuid: UUID of a port.
        """
        return Port(DB_Port().get_by_uuid(uuid))

    @wsme_pecan.wsexpose(Port, body=Port, status_code=201)
    def post(self, port):
        """Create a new Port.

        :param port: a port within the request body.
        """

        DB_Port.from_dict_object(port.as_dict()).create()


class PortList(base.APIBase):

    ports = [Port]

    def __init__(self, port_list):
        setattr(self, 'ports', [Port(port) for port in port_list])


class PortListController(rest.RestController):
    """Version 1 API portCollection controller."""

    @wsme_pecan.wsexpose(PortList)
    def get(self):
        """Retrieve list of all ports.

        :param port_ident: UUID of a port.
        """
        return PortList(DB_Port.list())

