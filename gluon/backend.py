# Copyright (c) 2015 Cisco Systems, Inc.
# All Rights Reserved
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

import abc
import six
import stevedore

import logging

logger = logging.getLogger('gluon')

@six.add_metaclass(abc.ABCMeta)
class Provider(object):

    @abc.abstractmethod
    def driver_for(self, config, backend):
	return None

class Driver(object):
    @abc.abstractmethod
    def bind(self, port):
        pass

    @abc.abstractmethod
    def unbind(self, port):
        pass


class Manager(object):
    """Class used to manage backend drivers in Gluon.

    Drivers know how to talk to particular network services.  It
    doesn't have to be a 1:1 mapping; the service registers with
    Neutron and can declare which comms driver to use.

    """

    def __init__(self, app_config):
	self._app_config = app_config

	def upset(manager, entrypoint, exception):
	    logger.error('Failed to load %s: %s' % (entrypoint, exception))

        # Sort out the client drivers
        # TODO should probably be NamedExtensionManager
        self._mgr = stevedore.ExtensionManager(
            namespace='gluon.backends',
	    on_load_failure_callback=upset,
	    invoke_on_load=True,
	    invoke_args=[logger],
        )
	for f in self._mgr:
	    logger.debug('Got backend %s' % f.name)
	logger.debug('Backend management enabled')

    def get_backend_driver(self, backend):

        for f in self._mgr:
            x = f.obj.driver_for(self._app_config, backend)
            if x is not None:
                return x

        logger.error('No backend driver for backend %s', backend)
        return None


