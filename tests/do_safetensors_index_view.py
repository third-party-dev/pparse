#!/usr/bin/env python3

import sys
from pprint import pprint


from importlib import resources
import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.view.safetensors import SafeTensorsIndex

# Enable running test script without pytest.
from thirdparty.pparse.utils import find_project_root
sys.path.insert(0, str(find_project_root()))


try:
    # Get the full path of the index file
    idx_modpath = 'tests.data.models.whisper'
    idx_fname = 'model.safetensors.index.fp32.json'
    idx_fpath = str(resources.files(idx_modpath).joinpath(idx_fname))

    # Parse the index and all associated safetensors files.
    sti = SafeTensorsIndex().open_fpath(idx_fpath)

    # List safetensors files:
    safetensors_names = sti.safetensors_names()

    # Get single SafeTensors object (based on index name):
    safetensor_obj = sti.safetensors('model.fp32-00001-of-00002.safetensors')

    # List tensor names:
    tensor_names = sti.tensor_names()

    # Get single Tensor object:
    tensor = sti.tensor('model.encoder.layers.9.self_attn_layer_norm.weight')

except pparse.EndOfDataException:
    log.debug(e)
    pass
except Exception as e:
    log.debug(e)
    import traceback
    traceback.print_exc()


print("ALL DONE")
breakpoint()
