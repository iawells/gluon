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

import pecan
from pecan import rest
import wsmeext.pecan as wsme_pecan
from wsme import types as wtypes
from gluon.api import link
from gluon.api.base import APIBase
from gluon.api.controller.v1 import port as portAPI
from gluon.api.controller.v1 import backend as backendAPI

class V1(APIBase):
    """The representation of the version 1 of the API."""

    id = wtypes.text
    """The ID of the version, also acts as the release number"""

    links = [link.Link]

    @staticmethod
    def convert():
        v1 = V1()
        v1.id = "v1"
        v1.links = [link.Link.make_link('self', pecan.request.host_url,
                                        'v1', '', bookmark=True),
                    link.Link.make_link('describedby',
                                        'TODO',
                                        bookmark=True, type='text/html')
                    ]
#        v1.cpulse = [link.Link.make_link('self', pecan.request.host_url,
#                                         'cpulse', ''),
#                     link.Link.make_link('bookmark',
#                                         pecan.request.host_url,
#                                         'cpulse', '',
#                                         bookmark=True)
#                     ]
        return v1


class API(rest.RestController):
    """Version 1 API controller root."""

    port = portAPI.PortController()
    ports = portAPI.PortListController()
    backend = backendAPI.BackendController()

    @wsme_pecan.wsexpose(V1)
    def get(self):
        # NOTE: The reason why convert() it's being called for every
        #       request is because we need to get the host url from
        #       the request object to make the links.
        return V1.convert()

__all__ = (API)
