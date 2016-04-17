import os
import pkg_resources

import gluon.common.ParticleGenerator as ParticleGenerator   

_model_processor = None

# Singleton generator
def mp():
    """Return a particle generator based on the model files in this package"""

    _modelProcessor = ParticleGenerator.ModelProcessor()
    
    if _model_processor == None:
        for f in pkg_resources.resource_listdir(__name__, 'models'):
            with pkg_resources.resource_stream(f) as fd:
                mp.add_model(fd)
    return _model_processor

