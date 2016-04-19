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
from oslo_log import log as logging
from gluon.objects import base
from gluon.db import api as dbapi

LOG = logging.getLogger(__name__)


@base.GluonObjectRegistry.register
class Port(base.GlounObject, base.GluonObjectDictCompat):

    VERSION = '1.0'
    model = dbapi.get_models().Backend

    fields = {
              'id': fields.IntegerField(),
              'uuid': fields.UUIDField(nullable=False),
              }