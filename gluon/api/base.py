# All Rights Reserved.
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

import datetime

import wsme
from wsme import types as wtypes


class APIBase(wtypes.Base):

    # TBD
    created_at = wsme.wsattr(datetime.datetime, readonly=True)
    """The time in UTC at which the object is created"""

    # #TBD
    updated_at = wsme.wsattr(datetime.datetime, readonly=True)
    """The time in UTC at which the object is updated"""

    def as_dict(self):
        """Render this object as a dict of its fields."""
        return dict((k, getattr(self, k))
                    for k in self.fields
                    if hasattr(self, k) and
                    getattr(self, k) != wsme.Unset)

    def unset_fields_except(self, except_list=None):
        """Unset fields so they don't appear in the message body.

        :param except_list: A list of fields that won't be touched.

        """
        if except_list is None:
            except_list = []

        for k in self.as_dict():
            if k not in except_list:
                setattr(self, k, wsme.Unset)


class APIBaseObject(APIBase):
    @classmethod
    def build(cls, db_obj):
        obj = cls()
        db_obj_dict = db_obj.as_dict()
        for field in cls._DB_object_class.fields:
            # Skip fields we do not expose.
            if not hasattr(obj, field):
                continue
            setattr(obj, field, db_obj_dict.get(field, wtypes.Unset))
        return obj

    def to_db_object(self):
        new_DB_obj = self._DB_object_class()
        for field in self._DB_object_class.fields:
            if not hasattr(self, field):
                continue
            setattr(new_DB_obj, field, getattr(self, field))
        return new_DB_obj


class APIBaseList(APIBase):
    pass

