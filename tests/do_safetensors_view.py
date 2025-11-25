#!/usr/bin/env python3

import sys
from pprint import pprint


from importlib import resources
import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.view.safetensors import SafeTensors

# Enable running test script without pytest.
from thirdparty.pparse.utils import find_project_root
sys.path.insert(0, str(find_project_root()))


try:
    # Get the full path of the index file
    idx_modpath = 'tests.data.models.whisper'
    idx_fname = 'model.fp32-00001-of-00002.safetensors'
    idx_fpath = str(resources.files(idx_modpath).joinpath(idx_fname))

    # Parse the index and all associated safetensors files.
    st = SafeTensors().open_fpath(idx_fpath)

    # List tensor names:
    tensor_names = st.tensor_names()

    # Get Tensor object:
    tensor = st.tensor('model.encoder.layers.9.self_attn_layer_norm.bias')

except pparse.EndOfDataException:
    log.debug(e)
    pass
except Exception as e:
    log.debug(e)
    import traceback
    traceback.print_exc()


print("ALL DONE")
breakpoint()
