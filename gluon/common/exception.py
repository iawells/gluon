# Copyright 2015, Ericsson AB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Gluon base exception handling.

Includes decorator for re-raising Cloudpulse-type exceptions.

"""

from oslo_log import log as logging
from oslo_config import cfg
from oslo_log._i18n import _LE
from oslo_log._i18n import _

import six

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


class GluonException(Exception):

    """Base Gluon Exception

    To correctly use this class, inherit from it and define
    a 'message' property. That message will get printf'd
    with the keyword arguments provided to the constructor.

    """
    message = _("An unknown exception occurred.")
    code = 500

    def __init__(self, message=None, **kwargs):
        self.kwargs = kwargs

        if 'code' not in self.kwargs:
            try:
                self.kwargs['code'] = self.code
            except AttributeError:
                pass

        if message:
            self.message = message

        try:
            self.message = self.message % kwargs
        except Exception as e:
            # kwargs doesn't match a variable in the message
            # log the issue and the kwargs
            LOG.exception(_LE('Exception in string format operation'))
            for name, value in kwargs.iteritems():
                LOG.error(_LE("%(name)s: %(value)s") %
                          {'name': name, 'value': value})
            try:
                if CONF.fatal_exception_format_errors:
                    raise e
            except cfg.NoSuchOptError:
                # Note: work around for Bug: #1447873
                if CONF.oslo_versionedobjects.fatal_exception_format_errors:
                    raise e

        super(GluonException, self).__init__(self.message)

    def __str__(self):
        if six.PY3:
            return self.message
        return self.message.encode('utf-8')

    def __unicode__(self):
        return self.message

    def format_message(self):
        if self.__class__.__name__.endswith('_Remote'):
            return self.args[0]
        else:
            return six.text_type(self)


class Conflict(GluonException):
    message = _('Conflict.')
    code = 409


class AlreadyExists(Conflict):
    message = _("Object of %(cls)s with UUID %(uuid)s already exists.")


class NotFound(GluonException):
    code = 404
    message = _("Object of %(cls)s with UUID %(uuid)s not found.")


class NotCreateAble(GluonException):
    code = 409
    message = _("An object of type %(type)s cannot be created for %(object)s")
