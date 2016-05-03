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
import yaml
import sys
from gluon.api.baseObject import RootObjectController
from gluon.api.baseObject import SubObjectController
from gluon.api.baseObject import APIBaseObject
from gluon.common.particleGenerator.DataBaseModelGenerator import DataBaseModelProcessor
from gluon.api import types


class APIGenerator(object):

    def __init__(self, db_models):
        self.db_models = db_models

    def add_model(self, model):
            self.data = model

    def create_api(self, root):
        sub_controllers = {}
        if not self.data:
            raise Exception('Cannot create API from empty model.')
        for table_name, table_data in self.data.iteritems():
            try:
                # For every entry build a sub_api_controller
                # an APIObject, an APIObject and an APIListObject
                api_object_class = APIBaseObject.class_builder(
                     table_name, self.db_models[table_name])
                for attribute, attr_value in\
                        table_data['attributes'].iteritems():
                    api_type = self.translate_model_to_api_type(attr_value['type'])
                    setattr(api_object_class, attribute, api_type)

                # api_name
                api_name = table_data['api']['name']

                # primary_key_type
                primary_key = DataBaseModelProcessor.get_primary_key(table_data)
                if primary_key == 'uuid':
                    primary_key_type = 'uuid'
                else:
                    primary_key_type =\
                        table_data['attributes'][primary_key]['type']
                primary_key_type = self.translate_model_to_api_type(
                     primary_key_type)

                # parent_identifier_type
                parent = table_data['api']['parent']
                parent_identifier_type = None
                if parent != 'root':
                    parent_identifier_type = self.data[parent]['api']['name']
                    new_controller_class = SubObjectController.class_builder(
                         api_name, api_object_class, primary_key_type,
                         parent_identifier_type)
                else:
                    new_controller_class = RootObjectController.class_builder(
                         api_name, api_object_class, primary_key_type)

                if parent == 'root':
                    setattr(root, api_name, new_controller_class)
                else:
                    if 'childs' not in self.data[parent]:
                        self.data[parent]['childs'] = []
                    self.data[parent]['childs'].append(
                         {'name': api_name,
                          'class': new_controller_class})
                sub_controllers[table_name] = new_controller_class
            except:
                print('During processing of table ' + table_name)
                raise

        # Now add all childs since the roots are there now
        for table_name, table_data in self.data.iteritems():
            controller = sub_controllers[table_name]
            for child in table_data.get('childs', []):
                setattr(controller, child['name'], child['class'])

    def translate_model_to_api_type(self, model_type):
        if model_type == 'uuid':
            return types.uuid
        if model_type == 'string':
            return unicode
        if model_type in self.db_models:
            return self.db_models[model_type]
        raise Exception("Type %s not known." % model_type)
