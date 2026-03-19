#!/usr/bin/env python3

from pprint import pprint
from thirdparty.pparse.view.om import Om
from thirdparty.pparse.utils import pparse_repr

om = Om().open_fpath('modeldef.pb')

# graph.op.input.attr.

graph = om._extraction._result['protobuf'].value['graph'].value[0]
first_packed = graph.value['op'].value[0].value['attr'].value[2].value['value'].value['list'].value['i'].value

'''
graph_list = om._extraction._result['protobuf'].value['graph']
graph = graph_list.value[0]

# int64 data_offset = 18; ... if it has parameters
tensor_desc = graph.value['op'].value[0].value['input_desc'].value[0].value

some_shape = graph.value['op'].value[0].value['input_desc'].value[0].value['shape'].value['dim']


for i in range(0, 12):
    graph.value['attr'].value[2].value['value'].value


'''


#parser = om._extraction._parser['protobuf']
# model = om._extraction._result['protobuf'].value
# graph = model['graph'].value
# nodes = graph['node'].value
# node0 = nodes[0].value
# input_ids = node0['input'].value
# output_ids = node0['output'].value
# name = node0['name']

# print('')

# print(f'Nodes Found: {len(nodes)}')

# ops = {}
# for node in nodes:
#     if 'op_type' in node.value:
#         ops[node.value['op_type']] = True
# print("Operations Found:")
# for op in ops:
#     print(f'- {op}')

breakpoint()

#for key in obj._extraction._parser['protobuf'].tensors.keys():
#    breakpoint()

'''


'''
