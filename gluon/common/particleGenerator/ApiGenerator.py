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

import yaml
import sys
from oslo_versionedobjects import fields
from gluon.api.baseObject import RootObjectController
from gluon.api.baseObject import SubObjectController
from gluon.api.baseObject import APIBaseObject
from gluon.common.particleGenerator.DataBaseModelGenerator import DataBaseModelProcessor
from gluon.api import types
from gluon.objects import base as obj_base


class APIGenerator(object):

    def __init__(self, db_models):
        self.db_models = db_models
        self.objects = []

    def add_model(self, model):
        self.data = model

    def create_api(self, root):
        sub_controllers = {}
        if not self.data:
            raise Exception('Cannot create API from empty model.')
        for table_name, table_data in self.data.iteritems():
            try:
                # For every entry build a (sub_)api_controller
                # an APIObject, an APIObject and an APIListObject
                # and a real object is created
                real_object = obj_base.GluonObject.class_builder(
                    table_name, self.db_models[table_name])
                api_object_class = APIBaseObject.class_builder(
                    table_name, real_object)
                real_object_fields = {}
                for attribute, attr_value in\
                        table_data['attributes'].iteritems():
                    api_type = self.translate_model_to_api_type(
                        attr_value['type'])
                    setattr(api_object_class, attribute, api_type)
                    real_object_fields[attribute] = self.translate_model_to_real_obj_type(
                        attr_value['type'])

                setattr(real_object, 'fields', real_object_fields)
                # api_name
                api_name = table_data['api']['name']

                # primary_key_type
                primary_key_type = self.translate_model_to_api_type(
                    self.get_primary_key_type(table_data))

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

                new_controller = new_controller_class()
                if parent == 'root':
                    setattr(root, api_name, new_controller)
                else:
                    if 'childs' not in self.data[parent]:
                        self.data[parent]['childs'] = []
                    self.data[parent]['childs'].append(
                        {'name': api_name,
                         'object': new_controller})
                sub_controllers[table_name] = new_controller
            except:
                print('During processing of table ' + table_name)
                raise

        # Now add all childs since the roots are there now
        for table_name, table_data in self.data.iteritems():
            controller = sub_controllers[table_name]
            for child in table_data.get('childs', []):
                setattr(controller, child['name'], child['object'])

    def get_primary_key_type(self, table_data):
        primary_key = DataBaseModelProcessor.get_primary_key(
            table_data)
        return table_data['attributes'][primary_key]['type']

    def translate_model_to_real_obj_type(self, model_type):
        # first make sure it is not a foreign key
        if model_type in self.data:
            # if it is we point to the primary key type type of this key
            model_type = self.get_primary_key_type(
                self.data[model_type])

        if model_type == 'uuid':
            return fields.UUIDField(nullable=False)
        if model_type == 'string':
            return fields.StringField()
        raise Exception("Type %s not known." % model_type)

    def translate_model_to_api_type(self, model_type):
        # first make sure it is not a foreign key
        if model_type in self.data:
            # if it is we point to the primary key type type of this key
            model_type = self.get_primary_key_type(
                self.data[model_type])

        if model_type == 'uuid':
            return types.uuid
        if model_type == 'string':
            return unicode
        raise Exception("Type %s not known." % model_type)
