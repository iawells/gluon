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


# This is a simple Flask application that provides REST APIs by which
# compute and network services can communicate, plus a REST API for
# debugging using a CLI client.

# Note that it does *NOT* at this point have a persistent database, so
# restarting this process will make Gluon forget about every port it's
# learned, which will not do your system much good (the data is in the
# global 'backends' and 'ports' objects).  This is for simplicity of
# demonstration; we have a second codebase already defined that is
# written to OpenStack endpoint principles and includes its ORM, so
# that work was not repeated here where the aim was to get the APIs
# worked out.  The two codebases will merge in the future.

from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
import os
import logging
import logging.handlers
import gluon.backend as backend
from keystoneauth1 import loading
from keystoneauth1 import session
from novaclient import client as nova_client

# Basic log config
logger = logging.getLogger('gluon')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
logger.addHandler(ch)
logger.debug('Debug logging enabled')

# Basic Flask RESTful app setup
app = Flask('gluon')
app.config.from_object('gluon.settings.Default')
if 'GLUON_SETTINGS' in os.environ:
    app.config.from_envvar('GLUON_SETTINGS')

api = Api(app)

# Make a backend manager through which we can discover backend
# drivers.
backend_manager = backend.Manager(app.config)

######################################################################

# This object is an ID-indexed dict containing all the ports that our
# backends have told us about.
ports = {}

# This should contain a list of mandatory port arguments.  I'm not
# sure it's complete at the moment, because Nova requires more than
# this when binding comes around.
port_parser = reqparse.RequestParser()
port_parser.add_argument('id')

def abort_if_port_doesnt_exist(id, backend=None):
    if id not in ports:
        abort(404, message="Port {} doesn't exist".format(id))
    if backend is not None and ports[id]['backend'] != backend:
        abort(404, message="Port {} doesn't exist".format(id))

# Port
# shows a single port item and lets you delete a port item
class Port(Resource):
    """Resource for one port."""

    def get(self, backend=None, service=None, id=None):
        if id in ports:
	    port = ports[id]

            # Update the backend information for this port.  We are
            # not a cache, so we always re-fetch.  TODO though
            # arguably we shouldn't be storing, and we should be
            # verifying that the backend has provided exactly the
            # expected information.
            backend_port_info = \
                do_backend_get_port(backends[port['backend']], id)
            port.update(backend_port_info)

	    if backend is not None and port['backend'] == backend:
		return port
	    if service is not None and port.get('device_owner') == service:
		return port
	    if backend is None and service is None:
		return port
        abort(404, message="Port {} doesn't exist".format(id))

    def delete(self, backend, id):
        abort_if_port_doesnt_exist(id, backend=backend)

        del ports[id]
        return '', 204

class PortList(Resource):
    """Resource for the .../ports URLs that list ports in a domain.

    Includes the POST to register a new port.
    """

    def get(self, backend=None, service=None, device=None):
	if backend is None:
	    # shortcut
	    if service is None:
		return ports

	    backend_ports=ports.values()
	else:
	    abort_if_backend_doesnt_exist(backend)
	    backend_ports=[v for v in ports.values() 
                           if v['backend'] == backend]

	if service is not None:
	    backend_ports = [v for v in backend_ports 
                             if v.get('device_owner') == service]
	    if device is not None:
		backend_ports = [v for v in backend_ports 
		    if v.get('device_id') == device]

	return { v['id']: v for v in backend_ports }
			

        return backend_ports

    def post(self, backend):
	abort_if_backend_doesnt_exist(backend)

        args = port_parser.parse_args()
	args['backend'] = backend
	
	id=args['id']
	# TODO check ID uniqueness

        ports[id] = args

        return args, 201


def do_backend_bind(backend, port_id, device_owner, zone, device_id,
                    host, binding_profile):
    """Helper function to get a port bound by the backend.

    Once bound, the port is owned by the network service and cannot be
    rebound by that service or any other without unbinding first.

    Binding consists of the compute and network services agreeing a
    drop point; the compute service has previously set binding
    requirements on the port, and at this point says where the port
    must be bound (the host); the network service will work out what
    it can achieve and set information on the port indicating the drop
    point it has chosen.

    Typically there is some prior knowledge on both sides of what
    binding types will be acceptable, so this process could be
    improved.
    """

    logger.debug('Binding port %s on backend %s: compute: %s/%s/%s location %s' 
                 % (port_id, backend['name'], device_owner, 
                    zone, device_id, host))
    driver = backend_manager.get_backend_driver(backend)
    # TODO these are not thoroughly documented or validated and are a
    # part of the API.  Write down what the values must be, must mean
    # and how the backend can use them.
    driver.bind(port_id, 
	device_owner, zone, device_id,
	host, binding_profile)

    # TODO required?  Do we trust the backend to set this?
    ports[port_id]['zone'] = zone

def do_backend_unbind(backend, port_id):
    """Helper function to get a port unbound from the backend.

    Once unbound, the port becomes ownerless and can be bound by
    another service.  When unbound, the compute and network services
    have mutually agreed to stop exchanging packets at their drop
    point.

    """

    driver = backend_manager.get_backend_driver(backend)
    driver.unbind(port_id)

def do_backend_get_port(backend, port_id):
    """Helper function to get a port's information from the backend.

    This returns the information as a dict.  TODO the spec is
    unwritten as to what information is required, but this should
    validate that information is present (and no additional infomation
    is also passed) to enforce the API contract.

    """
    driver = backend_manager.get_backend_driver(backend)
    return driver.port(port_id)

def nova_notify(device_id, port_id, event):
    """Notify Nova of a port update.

    Neutron tells Nova about certain port status changes by using a
    REST URL to hand those events over.  (Question: does Nova work if
    Neutron fails to get the message over?)  In a multi-service
    environment, a backend service should tell Gluon and Gluon should
    notify relevant compute services (and this should be in a driver
    and shouldn't have credentials hardcoded in it, obviously...).

    TODO untested; unused as yet.

    """
    # This model of authentication is technically antiquated by
    # Keystone standards; there are newer patterns.
    VERSION = '2.1'
    loader = loading.get_plugin_loader('password')
    auth = loader.Password(auth_url='http://127.0.0.1:35357',
                           username='nova',
                           password='iheartksl',
                           project_id='service')

    sess = session.Session(auth=auth)
    nova = nova_client.Client(VERSION, session=sess)

    # Send the event over.  TODO no retries here.  If we returned a
    # 500 to the network service would it do the retries?
    nova.server_external_events.create(
        { events: 
          [{'server_uuid': device_id,
            'name': event,
            'status': "completed",
            'tag': port_id}]})

class PortBind(Resource):
    """The resource providing the specific PUT operations to bind and
    unbind a port.

    The previous interface relied on setting of certain properties at
    a given momnt in time to indicate a bind.  We're implementing
    something more like a method for those operations.
    """

    def __init__(self):
	self.bind_args = parser = reqparse.RequestParser()
        self.bind_args.add_argument('host')
        self.bind_args.add_argument('device_owner')
        self.bind_args.add_argument('zone')
        self.bind_args.add_argument('device_id')
        self.bind_args.add_argument('pci_profile')
        self.bind_args.add_argument('rxtx_factor')

	self.notify_args = parser = reqparse.RequestParser()
        self.bind_args.add_argument('event')
        self.bind_args.add_argument('device_id')
        self.bind_args.add_argument('device_owner')

    def _bind(self, id):
	args = self.bind_args.parse_args()
	binding_profile={
	    'pci_profile': args['pci_profile'],
	    'rxtx_factor': args['rxtx_factor']
	    # TODO add negotiation here on binding types that are valid
            # (requires work in Nova)
	}
	accepted_binding_type = \
            do_backend_bind(backends[ports[id]['backend']], id,
                            args['device_owner'], args['zone'], 
                            args['device_id'], args['host'],
                            binding_profile)
	# TODO accepted binding type should be returned to the caller

    def _unbind(self, id):
	# Not very distributed-fault-tolerant, but no retries yet
	do_backend_unbind(backends[ports[id]['backend']], id)

    # Called by the backend
    # Also needs to be a bunch of drivers; we might not only have Nova
    # as the service.  TODO too incomplete to test at this point.
    def notify(self, device_id, id):
	args = self.notify_args.parse_args()
        # TODO: notify only the device owner (?)
        nova_notify(id, args['device_owner'], args['event'])

    def put(self, id, op):
	abort_if_port_doesnt_exist(id)
	if op == 'bind':
	    self._bind(id)
	elif op == 'unbind':
	    self._unbind(id)
	elif op == 'notify':
	    self._notify(id)
	else:
	    return 'Invalid operation on port', 404

# Backend endpoints

backend_parser = reqparse.RequestParser()
backend_parser.add_argument('name')
backend_parser.add_argument('service_type')
backend_parser.add_argument('url')

# This object is an ID-indexed dict containing all the backends that
# have registered.
backends = {}

def abort_if_backend_doesnt_exist(name):
    if name is None:
        abort(404, message="Backend must be given")
    if name not in backends:
        abort(404, message="Backend {} doesn't exist".format(name))

# Backend
# shows a single backend item and lets you delete a backend item
class Backend(Resource):
    def get(self, name):
        abort_if_backend_doesnt_exist(name)
        return backends[name]

    def delete(self, name):
        abort_if_backend_doesnt_exist(name)
        del backends[name]
        return '', 204


# BackendList
# shows a list of all backends, and lets you POST to add new tasks
class BackendList(Resource):
    def get(self):
        return backends

    def post(self):
        args = backend_parser.parse_args()
	
        backends[args['name']] = args
	return args, 201

##
## Actually setup the Api resource routing here
##
api.add_resource(PortList, 
		 '/backends/<backend>/ports', 
		 '/services/<service>/ports', 
		 '/services/<service>/devices/<device>/ports', 
		 '/ports')
api.add_resource(Port, 
		 '/backends/<backend>/ports/<id>',
		 '/services/<service>/ports/<id>', 
		 '/ports/<id>')
api.add_resource(PortBind, '/ports/<id>/<op>')

api.add_resource(BackendList, '/backends')
api.add_resource(Backend, '/backends/<name>')


# TODO port should probably be configurable.
def main():
    app.run(debug=True, port=2704)

if __name__ == '__main__':
    main()
