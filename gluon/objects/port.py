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

from oslo_versionedobjects import fields
from oslo_versionedobjects import exception
from oslo_log import log as logging
from oslo_log._i18n import _LI

from gluon.objects import base
from gluon.db import api as dbapi

LOG = logging.getLogger(__name__)


@base.GluonObjectRegistry.register
class Port(base.GlounObject, base.GluonObjectDictCompat):

    VERSION = '1.0'

    dbapi = dbapi.get_instance()

    fields = {
              'id': fields.IntegerField(),
              'uuid': fields.UUIDField(nullable=False),
              }

    def __init__(self, *args, **kwargs):
        super(Port, self).__init__(*args, **kwargs)

    def create(self):
        """Create a Port in the DB.
        """
        if self.obj_attr_is_set('id'):
            raise exception.ObjectActionError(action='create',
                                              reason='already created')

        values = self.obj_get_changes()
        LOG.info(_LI('Dumping CREATE port datastructure  %s') % str(values))
        db = self.dbapi.create_port(values)
        self._from_db_object(self, db)

    @staticmethod
    def _from_db_object(port, db):
        """Converts a database entity to a formal object."""
        for field in port.fields:
            port[field] = db[field]

        port.obj_reset_changes()
        return port
