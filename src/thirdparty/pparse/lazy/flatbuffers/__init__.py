import logging
import os
import sys
import struct

log = logging.getLogger(__name__)

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lazy.flatbuffers.node import Node, NodeVector, NodeTable
from thirdparty.pparse.lazy.flatbuffers.meta import tflite3_json_schema, FlatbuffersSchema

#proto = OnnxPb()

# make_protobuf_parser(ext_list=['.onnx'], init_msgtype='tflite.Model')
def make_tflite_parser(ext_list=['.tflite'], schema=tflite3_json_schema): #, init_msgtype="tflite.Model"):
    class Parser(pparse.Parser):
        @staticmethod
        def match_extension(fname: str):
            if not fname:
                return False
            # for ext in ['.onnx']:
            for ext in ext_list:
                if fname.endswith(ext):
                    return True
            return False

        @staticmethod
        def match_magic(cursor: pparse.Cursor):
            # TODO: Look for TFL3 after root_table offset.
            return False

        def __init__(self, source: pparse.Extraction, id: str):
            super().__init__(source, id)

            '''
            The top_reader is from the top of the file (req'd for flatbuffers).
            The Node's reader is from the start of the node.
            '''

            self.top_reader = source.open()
            self.schema = FlatbuffersSchema(schema_obj=tflite3_json_schema)
            self.current = Node(None, source.open(), 0)
            source._result[id] = self.current

        # TODO: parse_table, parse_vtable, parse_field,
        #       parse_scalar, parse_vector, parse_union

        def read_u32(self, ctx, peek=False):
            data = ctx.peek(4) if peek else ctx.read(4)
            if len(data) < 4:
                raise pparse.EndOfDataException("Not enough data in parse_u32()")
            return struct.unpack('<I', data)[0]

        def read_i32(self, ctx, peek=False):
            # Get 32bit signed int (mostly for vtable offsets)
            data = ctx.peek(4) if peek else ctx.read(4)
            if len(data) < 4:
                raise pparse.EndOfDataException("Not enough data in parse_i32()")
            return struct.unpack('<i', data)[0]

        def peek_u32(self, ctx):
            return self.read_u32(ctx, peek=True)

        def peek_i32(self, ctx):
            return self.read_i32(ctx, peek=True)


        def read_u16(self, ctx, peek=False):
            data = ctx.peek(2) if peek else ctx.read(2)
            if len(data) < 2:
                raise pparse.EndOfDataException("Not enough data in parse_u16()")
            return struct.unpack('<H', data)[0]

        def peek_u16(self, ctx):
            return self.read_u16(ctx, peek=True)


        def read_string(self, ctx) -> str:
            length = self.read_u32(ctx)
            data = ctx.read(length)
            if len(data) < length:
                raise pparse.EndOfDataException("Not enough data in read_string()")
            return data.decode('utf-8')

        def read_scalar(self, ctx, base_type: str):
            if base_type not in self.schema.TYPE_FORMATS:
                raise ValueError(f"Unsupported scalar type: {base_type}")
            size = self.schema.TYPE_SIZES[base_type]
            fmt = self.schema.TYPE_FORMATS[base_type]
            data = ctx.peek(size)
            if len(data) < size:
                raise pparse.EndOfDataException("Not enough data in read_scalar()")
            return struct.unpack(fmt, data)[0]

        def _parse_thing(self, ctx, peek=False):
            value = 0
            start = ctx.tell()

            # Do stuff

            end = ctx.tell()
            if peek:
                ctx.seek(start)
            return value, end - start

        def parse_thing(self, ctx):
            return self._parse_varint(ctx, False)[0]

        def peek_thing(self, ctx):
            return self._parse_varint(ctx, True)


        def _apply_value(self, ctx, field, value):
            if isinstance(self.current, NodeArray):
                log.debug(
                    f"apply_value (off:{ctx.tell()}): Inside {self.current}. Append value."
                )
                self.current.value.append(value)
                return

            elif isinstance(self.current, NodeMap):
                # TODO: Is this a good place to determine if we Node-ify a value?

                log.debug(
                    f"apply_value (off:{ctx.tell()}): Inside {self.current}. Set value to key {field.name}."
                )
                ctx.just_set_node = isinstance(value, Node)
                ctx.just_set_field = field
                self.current.value[field.name] = value
                return

            log.debug(
                f"UNLIKELY!! apply_value (off:{ctx.tell()}): Create arr as top level object."
            )
            breakpoint()

        def _start_map_node(self, ctx, field):
            ctx.mark_field_start()
            parent = self.current
            newmap = NodeMap(parent, ctx.reader())#, proto.by_type_name(field.type_name))

            if isinstance(self.current, NodeArray):
                log.debug(
                    f"start_map (off:{ctx.tell()}): Inside Array. Append new map to current array."
                )
                self.current.value.append(newmap)
                self.current = newmap
            elif isinstance(self.current, NodeMap):
                log.debug(
                    f"start_map (off:{ctx.tell()}): Inside Map. Add new map to current map as {field.name}."
                )
                parent.value[field.name] = newmap
                self.current = parent.value[field.name]
            else:
                log.debug(
                    f"start_map (off:{ctx.tell()}): Create map as top level object."
                )
                parent.value = newmap
                self.current = newmap

        def _end_container_node(self, ctx):
            parent = ctx._parent
            if parent:
                log.debug(
                    f"end_container (off:{ctx.tell()}): Backtracking to parent {parent}."
                )

                # Set the end pointer to advance parent past field.
                ctx.mark_end()

                # In parent, fast forward past the bit we just parsed.
                parent.ctx().seek(ctx._end)

                # Kill ctx (hopefully reclaiming memory).
                ctx.node().clear_ctx()

                # Set current node to parent.
                self.current = parent

        def scan_data(self):
            try:
                while True:
                    # While not end of data, keep parsing via states.
                    self.current.ctx().state().parse_data(self, self.current.ctx())
            except pparse.EndOfNodeException as e:
                pass
            except pparse.EndOfDataException as e:
                pass
            except pparse.UnsupportedFormatException:
                raise

            # TODO: Do all the children.

            return self

    return Parser
