#!/usr/bin/env python3

import logging

log = logging.getLogger(__name__)

# from thirdparty.pparse.lazy.protobuf import ProtobufParsingState, ProtobufParsingKey
import io
import sys
import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lazy.pickle.calls import ReduceCall, PersistentCall, NewCall
from thirdparty.pparse.dump import Dumper, _print_cb


# class NodeContext(pparse.NodeContext):
#     def __init__(self, node: "Node", parent: "Node", reader: pparse.Range):
#         if type(reader).__name__ != "Range":
#             raise Exception("protobuf NodeContext reader must be a pparse.Range")
#         super().__init__(node, parent, reader)


class NodeVmContext(pparse.NodeContext):
    def __init__(self, parent: "Node", reader: pparse.Range, parser: pparse.Parser):
        if type(reader).__name__ != "Range":
            raise Exception("protobuf NodeContext reader must be a pparse.Range")
        super().__init__(parent, reader, parser)

        self.proto = None
        self.current_op = None
        self.stack = []
        self.memo = {}
        self.next_memo = 0

        # Note: Save the history to the node, forever allocating that memory.
        self.history = []

    def vmstate(self):
        return self._vmstate


class Node(pparse.Node):
    def dump(self, depth=0, step=2, dumper=None):
        if not dumper:
            dumper = PickleDumper()
        # TODO: Consider the ReduceCall dict AND _value.
        dumper.dump("Node", self._value, '', depth=depth, step=step)


class PickleDumper(Dumper):
    def __init__(self, dumpers=None, cb=_print_cb, dst=sys.stdout):
        import numbers
        from thirdparty.pparse.lib import Node
        from collections.abc import Iterable

        self.dumpers = dumpers
        if self.dumpers is None:
            self.dumpers = [
                [NewCall, self._dump_newcall_wrapper],
                [ReduceCall, self._dump_reducecall_wrapper],
                [PersistentCall, self._dump_persidcall_wrapper],
                [Node, self._dump_node_wrapper],
                [dict, self._dump_dict_wrapper],
                [bytes, self._dump_bytes_wrapper],
                [str, self._dump_str_wrapper],
                [int, self._dump_misc_wrapper],
                [float, self._dump_misc_wrapper],
                [numbers.Number, self._dump_misc_wrapper],
                [bool, self._dump_misc_wrapper],
                [type(None), self._dump_misc_wrapper],
                [io.BytesIO, self._dump_bytesio_wrapper],
                [Iterable, self._dump_iter_wrapper],
            ]
        super().__init__(dumpers=self.dumpers, cb=cb, dst=dst)


    def _dump_newcall_wrapper(self, elem_name="NewCall", obj=None, attrs='', depth=0, step=2):
        spacer = " " * depth
        attrs = ' '.join([
            f'mod="{obj.module_call[0].decode("utf-8").strip()}"',
            f'func="{obj.module_call[1].decode("utf-8").strip()}"',
        ])
        self.cb(self.dst, f'{spacer}<NewCall {attrs}>')
        
        if obj.arg is None or len(obj.arg) == 0:
            self.cb(self.dst, f'{spacer}{" " * step}<args is_empty="y" />')
        else:
            self.cb(self.dst, f'{spacer}{" " * step}<args count="{len(obj.arg)}">')
            self._dump_list(obj.arg, depth + (step * 2))
            self.cb(self.dst, f'{spacer}{" " * step}</args>')

        if obj.state is None:
            self.cb(self.dst, f'{spacer}{" " * step}<state is_empty="y" />')
        else:
            self.cb(self.dst, f'{spacer}{" " * step}<state key_count="{len(obj.state)}">')
            self._dump_dict(obj.state, depth + (step * 2))
            self.cb(self.dst, f'{spacer}{" " * step}</state>')

        if len(obj) == 0:
            self.cb(self.dst, f'{spacer}{" " * step}<dict is_empty="y">')
        else:
            self.cb(self.dst, f'{spacer}{" " * step}<dict key_count="{len(dict(obj))}">')
            self._dump_dict(dict(obj), depth + (step * 2))
            self.cb(self.dst, f'{spacer}{" " * step}</dict>')

        self.cb(self.dst, f'{spacer}</NewCall>')


    def _dump_reducecall_wrapper(self, elem_name="ReduceCall", obj=None, attrs='', depth=0, step=2):
        spacer = " " * depth
        attrs = ' '.join([
            f'mod="{obj.module_call[0].decode("utf-8").strip()}"',
            f'func="{obj.module_call[1].decode("utf-8").strip()}"',
        ])
        self.cb(self.dst, f'{spacer}<ReduceCall {attrs}>')
        
        if obj.arg is None or len(obj.arg) == 0:
            self.cb(self.dst, f'{spacer}{" " * step}<args is_empty="y" />')
        else:
            self.cb(self.dst, f'{spacer}{" " * step}<args count="{len(obj.arg)}">')
            self._dump_list(obj.arg, depth + (step * 2))
            self.cb(self.dst, f'{spacer}{" " * step}</args>')

        if obj.state is None:
            self.cb(self.dst, f'{spacer}{" " * step}<state is_empty="y" />')
        else:
            self.cb(self.dst, f'{spacer}{" " * step}<state key_count="{len(obj.state)}">')
            self._dump_dict(obj.state, depth + (step * 2))
            self.cb(self.dst, f'{spacer}{" " * step}</state>')

        if len(dict(obj)) == 0:
            self.cb(self.dst, f'{spacer}{" " * step}<dict is_empty="y" />')
        else:
            self.cb(self.dst, f'{spacer}{" " * step}<dict key_count="{len(dict(obj))}">')
            self._dump_dict(dict(obj), depth + (step * 2))
            self.cb(self.dst, f'{spacer}{" " * step}</dict>')

        self.cb(self.dst, f'{spacer}</ReduceCall>')
    
    def _dump_persidcall_wrapper(self, elem_name="PersistentCall", obj=None, attrs='', depth=0, step=2):
        spacer = " " * depth
        attrs = ' '.join([
            f'id="{obj.id}"',
        ])
        self.cb(self.dst, f'{spacer}<PersistentCall {attrs}>')
        
        self.cb(self.dst, f'{spacer}{" " * step}<args>')
        #self.cb(self.dst, f'{spacer}{" " * step}{obj.arg}')
        self._dump_list(obj.arg, depth + (step * 2))
        self.cb(self.dst, f'{spacer}{" " * step}</args>')

        self.cb(self.dst, f'{spacer}</PersistentCall>')







# def pparse_repr(obj, depth=0, step="  "):
#     res = []

#     if hasattr(obj, "pparse_repr"):
#         res.append(obj.pparse_repr(depth, step))

#     elif isinstance(obj, dict):
#         dict_spacer = depth * step
#         res.append("{\n")

#         # Assuming key is always string or scalar
#         key_spacer = (depth + 1) * step
#         for k, v in obj.items():
#             if hasattr(v, "pparse_repr"):
#                 res.append(f"{key_spacer}{k}: {v.pparse_repr(depth + 1, step)}\n")
#             else:
#                 res.append(f"{key_spacer}{k}: {pparse_repr(v, depth + 1, step)}")

#         res.append(dict_spacer + "}\n")

#     elif isinstance(obj, (list, tuple, set)):
#         itr_spacer = depth * step
#         res.append("[\n")

#         elem_spacer = (depth + 1) * step
#         for elem in obj:
#             if hasattr(elem, "pparse_repr"):
#                 res.append(f"{elem_spacer}{elem.pparse_repr(depth + 1, step)}\n")
#             else:
#                 res.append(f"{elem_spacer}{pparse_repr(elem, depth + 1, step)}")

#         res.append(itr_spacer + "]\n")

#     else:
#         res.append(f"{obj}\n")

#     return "".join(res)



















# # An array of NodePickle objects.
# class NodePickleArray(pparse.Node):
#     def __init__(self, parent: pparse.Node, reader: pparse.Reader):
#         super().__init__(parent, reader, NodeContext(self, parent, reader.dup()))
#         self.value = []


# class NodePickle(pparse.Node):
#     """
#     A single pickle stream.
#     There are 2 processes interlaced in the processing of a single pickle stream.
#     - The parsing of the opcodes.
#     - The interpretation of the opcodes into a node tree.

#     Opcodes are parsed into a running stack.

#     As opcodes (results) are consumed by other opcodes, they are relocated to
#     the objects that have consumed them. In this way, we should be able to
#     completely reconstruct the original listing by recursives traversing the
#     final object node tree.
#     """

#     def __init__(self, parent: pparse.Node, reader: pparse.Reader):
#         super().__init__(parent, reader, NodeVmContext(self, parent, reader.dup()))

#         self.proto = None
#         self.value = []
