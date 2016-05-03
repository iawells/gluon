import os
import pkg_resources
import yaml

DataBaseModelGeneratorInstance = None
APIGeneratorInstance = None
model = None
sql_model_build = False
queued_build_api = False


# Singleton generator
def load_model():
        if not model:
            # for f in pkg_resources.resource_listdir(__name__, 'models'):
            #    with pkg_resources.resource_stream(f) as fd:
            with open('/home/enikher/workspace/gluon-dev/models/gluon_model.yaml',
                      'r') as fd:
                    global model
                    model = yaml.safe_load(fd)


def build_sql_models(base):
    from gluon.common.particleGenerator.DataBaseModelGenerator import DataBaseModelProcessor
    load_model()
    global DataBaseModelGeneratorInstance
    if not DataBaseModelGeneratorInstance:
        DataBaseModelGeneratorInstance = DataBaseModelProcessor()
        DataBaseModelGeneratorInstance.add_model(model)
        DataBaseModelGeneratorInstance.build_sqla_models(base)


def build_api(root):
    from gluon.common.particleGenerator.ApiGenerator import APIGenerator
    global DataBaseModelGeneratorInstance
    global APIGeneratorInstance
    load_model()
    if not APIGeneratorInstance:
        APIGeneratorInstance = APIGenerator(DataBaseModelGeneratorInstance.db_models)
        APIGeneratorInstance.add_model(model)
        APIGeneratorInstance.create_api(root)
