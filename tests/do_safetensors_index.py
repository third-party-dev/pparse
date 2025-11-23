#!/usr/bin/env python3

import sys
from pprint import pprint


from importlib import resources
import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lazy.safetensors.index import Parser as LazySafetensorsIndexParser

# Enable running test script without pytest.
from thirdparty.pparse.utils import find_project_root
sys.path.insert(0, str(find_project_root()))


'''
How should we handle a index file that points to other associated files? The associated files are
bound into a single structure. When we parse, we are purely parsing those structures. But the user
will expect to query the parts of the structure as if they were merged.

A safetensors index file is JSON. To keep things more simple for the moment, we'll explicitly 
control what parsers are used from the view object. To handle the situations more gracefully, we'll
likely need a better implementation of multi-level-drill-down and more comprehensive magic detection.

Also ... when we have something like safetensors index parser and JSON parser that will parse everything
equally, how do we prevent JSON from blinding creating unnecessary Extractions or results??

- Maybe each parser can provide a confidence level and then we filter matches with lower than max?

For safetensors index view object, the user should be able to query the tensors without knowledge
of their source. The object should perform querying the metadata for the unique index or unique
shards, but should a merged view of the metadata be considered?
'''


try:

    # Configure parser registry.
    parser_reg = {'safetensors_index': LazySafetensorsIndexParser}

    # Point at initial index file.
    idx_modpath = 'tests.data.models.whisper'
    idx_fname = 'model.safetensors.index.fp32.json'
    idx_fpath = str(resources.files(idx_modpath).joinpath(idx_fname))

    # Process the index file.
    idx_data = pparse.Data(path=idx_fpath)
    idx_range = pparse.Range(idx_data.open(), idx_data.length)
    root = pparse.BytesExtraction(name=idx_fpath, reader=idx_range)
    root.discover_parsers(parser_reg).scan_data()

except pparse.EndOfDataException:
    log.debug(e)
    pass
except Exception as e:
    log.debug(e)
    import traceback
    traceback.print_exc()

print(f'Extractions (Shard Files): {len(root._extractions)}')
print(f'Extraction[0] Result: {root._extractions[0]._result}')
print(f'Extraction[0] Safetensor Result: {root._extractions[0]._result['safetensors']}')
# JSON is at: root._extractions[0]._extractions[0]._result['json'].value.value
# - root's child[0] is safetensors
# - safetensors's child[0] is JSON
# - json's result is NodeInit with value = NodeMap
# - NodeMap's value is a dictionary (with safetensors keys)


# # Dump output for examination.
# print("Dumping root to output.txt")
# with open("output.txt", "w") as fobj:
#     pprint(root, stream=fobj, indent=2)
# print("Dump complete.")

# json_obj = root._result['json']
# # Dump with unloaded things.
# print(json_obj.dumps())
# # Load defered/truncated value.
# json_obj.value.value['description'].load(json_obj.parser)
# # Dump with loaded things.
# print(root._result['json'].dumps())

#tensor_db = root._result['safetensors'].parser.source()._extractions[0]._result['json'].value.value
#for k,v in tensor_db.items():
#    print(f"{k}: {v}")

# TODO: Consider converting each (non-"__metadata__") NodeMap into a NodeTensor. Each Tensor can
# then be "load()"ed on demand.

print("ALL DONE")
breakpoint()

'''

'''
