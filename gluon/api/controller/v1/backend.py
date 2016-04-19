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
from gluon.api import base
from wsme import types as wtypes


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
        for field in DB_Port.fields:
            # Skip fields we do not expose.
            if not hasattr(self, field):
                continue
            setattr(self, field, real_obj_port_dic.get(field, wtypes.Unset))
