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

from oslo_utils import uuidutils
from oslo_db import exception as db_exc
from oslo_db.sqlalchemy import session as db_session
from oslo_config import cfg

from gluon.db import api
from gluon.db.sqlalchemy import models
from gluon.common import exception
CONF = cfg.CONF

_FACADE = None


def _create_facade_lazily():
    global _FACADE
    if _FACADE is None:
        _FACADE = db_session.EngineFacade.from_config(CONF)
    return _FACADE


def get_engine():
    facade = _create_facade_lazily()
    return facade.get_engine()


def get_session(**kwargs):
    facade = _create_facade_lazily()
    return facade.get_session(**kwargs)


def get_backend():
    """The backend is this module itself."""
    return Connection()


class Connection(api.Connection):

    """SqlAlchemy connection."""

    def __init__(self):
        pass

    def create_port(self, values):

        # ensure defaults are present for new tests
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()

        port = models.Port()
        port.update(values)
        try:
            port.save()
        except db_exc.DBDuplicateEntry:
            raise exception.PortAlreadyExists(uuid=values['uuid'])
        return port
