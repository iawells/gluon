import os
import pkg_resources

import gluon.common.particleGenerator.ParticleGenerator as ParticleGenerator

_model_processor = None


# Singleton generator
def build_model_processor():
    """Return a particle generator based on the model files in this package"""

    _modelProcessor = ParticleGenerator.ModelProcessor()

    if not _model_processor:
        for f in pkg_resources.resource_listdir(__name__, 'models'):
            with pkg_resources.resource_stream(f) as fd:
                _modelProcessor.add_model(fd)
    return _model_processor
