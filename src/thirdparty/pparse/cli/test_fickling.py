#!/usr/bin/env python3

import pickle

from thirdparty.pparse.external.fickling.fickle import StackedPickle

with open('models/data.pkl', 'rb') as pkl_fobj:
    spkl = StackedPickle.load(pkl_fobj)

'''
All the pickle operations seen in a PyTorch are:
PROTO - Pickle Version
EMPTY_DICT = stack.push({})
BINPUT = memo[arg] = stack[-1]
MARK
BINUNICODE - stack.push(arg)
GLOBAL = import arg1, stack.push(arg2)
BININT - 32bit signed int
TUPLE = while not MARK: tuple.push(stack.pop());
BINPERSID = do something unpickler specific
BININT1 - 8bit unsigned int
BININT2 - 16bit unsigned int
TUPLE3 = (stack.pop(), stack.pop(), stack.pop())
NEWFALSE = stack.push(False)
EMPTY_TUPLE = (,)
REDUCE = stack.pop()(stack.pop()) # Call thing on stack with arg on stack
BINGET = stack.push(memo[arg])
TUPLE1 = (stack.pop(),)
TUPLE2 = (stack.pop(),stack.pop(),)
LONG_BINPUT = memo[arg] = stack[-1]
SETITEMS - stack before: [dict_obj, MARK, key1, val1, key2, val2, key3, val3, ...]
STOP - end of stream

Unused:
SETITEM - value = stack.pop(); key = stack.pop(); dict = stack.pop(); dict[key] = value
'''

# Dump fickling opcode objects
with open("ptpklout.txt", "w") as pklout:
    opcodes = []
    uniq_ops = {}
    i = 0
    depth = 0
    step = '  '
    for opcode in spkl.pickled[0].opcodes:
        #print(f'{i}: {opcode}')
        uniq_ops[opcode.name] = True
        opcodes.append(opcode)
        if True: #i < 100:
            if opcode.name in ['TUPLE', 'LIST', 'DICT', 'SET', 'FROZENSET', 'SETITEMS', 'OBJ']:
                depth -= 1

            # Print the output
            if opcode.arg is not None:
                pklout.write(f'{step*depth}{opcode.name} {opcode.arg}\n')
            else:
                pklout.write(f'{step*depth}{opcode.name}\n')
            if opcode.name in ['BINPUT', 'LONG_BINPUT', 'PROTO']:
                pklout.write('\n')

            if opcode.name in ['MARK']:
                depth += 1

        i+=1

# i = 0
# for opcode in spkl.pickled[0].opcodes:
#     if 'UNICODE' in opcode.name:
#         print(f'{i}: {opcode}')
#         print(f'  ARG: {opcode.arg}')
#     i+=1
#     if i > 300:
#         exit()


breakpoint()

'''
NodeVmState
  memo = {}
  proto = 2
  value = NodeList [
    NodeObject:
      value = {}
    parser.first().vm_state.memo[0] = parser.last()

    # Note: This 2nd level NodeList is the data for the above DICT
    NodeList [
      # Note: First key for the top DICT.
      NodeObject:
        value = 'model.encoder.conv1.weight'
      parser.first().vm_state.memo[1] = parser.last()
      NodeImport:
        value = (torch._utils, _rebuild_tensor_v2)
      parser.first().vm_state.memo[2] = parser.last()

      NodeList [
        NodeList [
          NodeObject:
            value = 'storage'
          parser.first().vm_state.memo[3] = parser.last()
          NodeImport:
            value = (torch, FloatStorage)
          parser.first().vm_state.memo[4] = parser.last()
          NodeObject:
            value = '0'
          parser.first().vm_state.memo[5] = parser.last()
          NodeObject:
            value = 'cpu'
          parser.first().vm_state.memo[6] = parser.last()
          NodeObject:
            value = 184320
        ]
        NodeTuple:
          # replace previous NodeList with self
          value = NodeListRef
        parser.first().vm_state.memo[7] = parser.last()

        # ** Load tensor data from external file (i.e. archive/data/ folder).
        NodeExternal:
          id = 0
          value = UNLOADED

        NodeObject:
          value = 768
        NodeObject:
          value = 80
        NodeObject:
          value = 3
        NodeTuple3:
          # replace previous 3 references with self
          value = NodeList(Node(768), Node(80), Node(3))
        parser.first().vm_state.memo[8] = parser.last()

        NodeObject:
          value = 240
        NodeObject:
          value = 3
        NodeObject:
          value = 1
        NodeTuple3:
          # replace previous 3 references with self
          value = NodeList(Node(240), Node(3), Node(1))
        parser.first().vm_state.memo[9] = parser.last()
          
        NodeObject:
          value = False

        NodeImport:
            value = (collections, OrderedDict)
        parser.first().vm_state.memo[10] = parser.last()

        NodeObject:
          value = tuple()

        NodeCall:
          # replace previous with self
          arg = NodeObjectRef
          # replace new previous with self
          callable = NodeImportRef
          value = UNLOADED_VALUE
        parser.first().vm_state.memo[11] = parser.last()

      ]
      NodeTuple:
          # replace previous NodeList with self
          value = NodeListRef
      parser.first().vm_state.memo[12] = parser.last()

      # (Return Value) First value for top DICT (key: model.encoder.conv1.weight)
      NodeCall:
          # replace previous (tuple) with self
          arg = NodeTupleRef
          # replace new previous with self
          callable = NodeImportRef(torch._utils, _rebuild_tensor_v2)
          value = UNLOADED_VALUE
        parser.first().vm_state.memo[13] = parser.last()

      # Second key for the top level DICT (key: model.encoder.conv1.weight).
      NodeObject:
        value = 'model.encoder.conv1.weight'
      parser.first().vm_state.memo[14] = parser.last()
      
      parser.push(parser.first().vm_state.memo[2])
        NodeImport:
          value = (torch._utils, _rebuild_tensor_v2)

      ... and it sort of loops from here.
        
    ]
  ]

PROTO 2

EMPTY_DICT         stack
BINPUT 0           

MARK
  BINUNICODE model.encoder.conv1.weight
  BINPUT 1

  GLOBAL torch._utils _rebuild_tensor_v2
  BINPUT 2

  MARK
    MARK
      BINUNICODE storage
      BINPUT 3

      GLOBAL torch FloatStorage
      BINPUT 4

      BINUNICODE 0
      BINPUT 5

      BINUNICODE cpu
      BINPUT 6

      BININT 184320
    TUPLE
    BINPUT 7

    BINPERSID
    BININT1 0

    BININT2 768
    BININT1 80
    BININT1 3
    TUPLE3
    BINPUT 8

    BININT1 240
    BININT1 3
    BININT1 1
    TUPLE3
    BINPUT 9

    NEWFALSE
    GLOBAL collections OrderedDict
    BINPUT 10

    EMPTY_TUPLE
    REDUCE
    BINPUT 11

  TUPLE
  BINPUT 12

  REDUCE
  BINPUT 13

  BINUNICODE model.encoder.conv1.bias
  BINPUT 14

  BINGET 2
  MARK
    MARK
      BINGET 3
      BINGET 4
      BINUNICODE 1
      BINPUT 15

      BINGET 6
      BININT2 768
    TUPLE
    BINPUT 16

    BINPERSID
    BININT1 0
    BININT2 768
    TUPLE1
    BINPUT 17
'''