#!/usr/bin/env python3

import struct

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lazy.pickle.meta import PklOp
from thirdparty.pparse.lazy.pickle.opnodes import NodePickleArray, NodePickle


def trace(*args, **kwargs):
    print(*args, **kwargs)
    pass


class PickleParsingState():
    def parse_data(self, parser: 'Parser', ctx: 'NodeContext'):
        raise NotImplementedError()


class PickleParsingReadlineParam(PickleParsingState):
    def parse_data(self, parser: 'Parser', ctx: 'NodeContext'):
        op = ctx.node().value[-1]
        data = ctx.peek(0x4000)
        if not data or len(data) < 1:
            raise pparse.EndOfDataException("Not enough data to parse readline delimited pickle opcode")
        
        # Do we have a newline?
        # TODO: We *should* be more tolerant of very large parameters here.
        offset = data.find(b'\n')
        if offset == -1:
            raise pparse.EndOfDataException("Not enough data to find end of readline delimited pickle opcode")

        if op.opcode == PklOp.GLOBAL and op.param != None:
            op.param2 = data[0:offset+1]
            ctx.skip(offset+1)
            ctx._next_state(PickleParsingOpCode)
            return

        op.param = data[0:offset+1]
        ctx.skip(offset+1)
        if op.opcode == PklOp.GLOBAL:
            # Keep going.    
            return
        ctx._next_state(PickleParsingOpCode)


class PickleParsingSimpleParam(PickleParsingState):
    def parse_data(self, parser: 'Parser', ctx: 'NodeContext'):
        op = ctx.node().value[-1]
        data = ctx.peek(op.pbytes)
        if not data or len(data) < op.pbytes:
            raise pparse.EndOfDataException("Not enough data to parse simple pickle opcode")

        op.param = struct.unpack(op.fmt, data)[0]
        ctx.skip(op.pbytes)
        ctx._next_state(PickleParsingOpCode)


class PickleParsingLengthParam(PickleParsingState):
    def parse_data(self, parser: 'Parser', ctx: 'NodeContext'):
        op = ctx.node().value[-1]
        data = ctx.peek(op.byte_len)
        if not data or len(data) < op.byte_len:
            raise pparse.EndOfDataException("Not enough data to parse simple pickle opcode")

        op.param = data[0:op.byte_len]
        ctx.skip(op.byte_len)
        ctx._next_state(PickleParsingOpCode)


class PickleParsingLengthPrefix(PickleParsingState):
    def parse_data(self, parser: 'Parser', ctx: 'NodeContext'):
        op = ctx.node().value[-1]
        data = ctx.peek(op.lbytes)
        if len(data) < op.lbytes:
            raise pparse.EndOfDataException("Not enough data to parse simple pickle opcode")

        op.byte_len = struct.unpack(op.fmt, data[0:op.lbytes])[0]
        ctx.skip(op.lbytes)
        ctx._next_state(PickleParsingLengthParam)


class PickleParsingOpCode(PickleParsingState):
    def parse_data(self, parser: 'Parser', ctx: 'NodeContext'):
        data = ctx.read(1)
        if not data or len(data) < 1:
            raise pparse.EndOfDataException("Not enough data to parse pickle opcode")

        op = PklOp(data[0])
        ctx.node().value.append(op)

        if PklOp.no_params(data[0]):
            return

        if PklOp.is_simple(data[0]):
            ctx._next_state(PickleParsingSimpleParam)
            return

        if PklOp.has_length(data[0]):
            ctx._next_state(PickleParsingLengthPrefix)
            return

        if PklOp.is_readline(data[0]):
            ctx._next_state(PickleParsingReadlineParam)
            return

        if op.opcode == PklOp.STOP:
            parser._end_container_node(ctx)
            parser.current.ctx()._next_state(PickleParsingPickleStream)
            return

        raise UnsupportedFormatException(f"Invalid pickle opcode: {hex(data[0])}")


# State where we switch pickle streams, delimited by STOP.
class PickleParsingPickleStream(PickleParsingState):
    def parse_data(self, parser: 'Parser', ctx: 'NodeContext'):
        data = ctx.peek(1)
        if not data or len(data) < 1:
            raise pparse.EndOfDataException("Not enough data to parse pickle opcode")

        parent = parser.current
        newpkl = NodePickle(parent, ctx.reader())
        newpkl.ctx()._next_state(PickleParsingOpCode)
        parent.value.append(newpkl)
        parser.current = newpkl
        trace("Starting new pkl stream.")


