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

from oslo_versionedobjects import exception
from oslo_versionedobjects import base as ovoo_base
from oslo_log._i18n import _LI
from gluon.db import api as dbapi
from oslo_log import log as logging

LOG = logging.getLogger(__name__)


class GluonObject(ovoo_base.VersionedObject):
    """Base class and object factory.

    This forms the base of all objects that can be remoted or instantiated
    via RPC. Simply defining a class that inherits from this base class
    will make it remotely instantiatable. Objects should implement the
    necessary "get" classmethod routines as well as "save" object methods
    as appropriate.
    """

    VERSION = '1.0'

    db_instance = dbapi.get_instance()

    def as_dict(self):
        return dict((k, getattr(self, k))
                    for k in self.fields
                    if hasattr(self, k))

    @classmethod
    def list(cls, limit=None, marker=None, sort_key=None,
             sort_dir=None, filters=None, failed=None, period=None):
        db_list = cls.db_instance.get_list(cls.model,
                                           limit=limit, marker=marker,
                                           sort_key=sort_key,
                                           sort_dir=sort_dir,
                                           failed=failed,
                                           period=period)
        return cls._from_db_object_list(cls, db_list)

    @classmethod
    def get_by_filter(cls, filter):
        return cls.list(filters=filter)

    @classmethod
    def get_by_uuid(cls, uuid):
        return cls.get_by_filter({'uuid': uuid})

    @classmethod
    def get_by_name(cls, name):
        return cls.get_by_filter({'name': name})

    @staticmethod
    def from_dict_object(cls, dict):
        """Converts a database entity to a formal object."""
        for field in cls.fields:
            cls[field] = dict[field]

        cls.obj_reset_changes()
        return cls

    @staticmethod
    def _from_db_object_list(cls, db_objects):
        return [cls.from_dict_object(cls(), obj) for obj in db_objects]

    def create(self):
        """Create a Object in the DB.
        """
        values = self.obj_get_changes()
        LOG.info(_LI('Dumping CREATE port datastructure  %s') % str(values))
        db_object = self.db_instance.create(self.model, values)
        self.from_dict_object(self, db_object)


class GluonObjectDictCompat(ovoo_base.VersionedObjectDictCompat):
    pass


class GluonObjectRegistry(ovoo_base.VersionedObjectRegistry):
    pass
