#!/usr/bin/env python3

import struct
import logging

log = logging.getLogger(__name__)

from thirdparty.pparse.lib import (
    EndOfDataException,
    EndOfNodeException,
    UnsupportedFormatException,
)


class OmParsingState(object):
    def parse_data(self, parser: "Parser", ctx: "NodeContext"):
        raise NotImplementedError()


class OmParsingComplete(OmParsingState):

    def parse_data(self, parser: "Parser", ctx: "NodeContext"):
        raise EndOfDataException("Complete")


class OmParsingModelDef(OmParsingState):

    def parse_data(self, parser: "Parser", ctx: "NodeContext"):
        parser.current.ctx()._next_state(OmParsingComplete)


class OmParsingPartitionEntry(OmParsingState):

    def parse_data(self, parser: "Parser", ctx: "NodeContext"):
        data = ctx.peek(24)
        if len(data) < 24:
            raise EndOfDataException("Not enough data to parse partition table count")

        entry = parser._new_nodemap(parser.current, ctx.reader())
        edict = entry.value
        edict['type'], edict['offset'], edict['size'] = struct.unpack('<QQQ', data[:24])

        parser.current.value.append(entry)
        ctx.skip(24)

        if parser.current.ctx().parent().value['partition_count'] > len(parser.current.value):
            ctx._next_state(OmParsingPartitionEntry)
        else:
            ctx._next_state(OmParsingModelDef)

        return


class OmParsingPartitionTable(OmParsingState):

    def parse_data(self, parser: "Parser", ctx: "NodeContext"):
        data = ctx.peek(8)
        if len(data) < 8:# obj.tensor('lm_head.weight').get_data_bytes()
            raise EndOfDataException("Not enough data to parse partition table count")

        partition_count = struct.unpack('<Q', data[:8])[0]
        parser.current.value['partition_count'] = partition_count
        ctx.skip(8)

        #ctx.mark_field_start()
        parent = parser.current
        newarr = parser._new_nodearray(parent, ctx.reader())
        parser.current.value['partitions'] = newarr
        parser.current = parser.current.value['partitions']

        if partition_count > 0:
            parser.current.ctx()._next_state(OmParsingPartitionEntry)
        else:
            parser.current.ctx()._next_state(OmParsingComplete)

        return


class OmParsingHeader(OmParsingState):

    def parse_data(self, parser: "Parser", ctx: "NodeContext"):
        data = ctx.peek(0x100)
        if len(data) < 0x100:
            raise EndOfDataException("Not enough data to parse om header")

        parser.current.value['raw_data'] = data
        ctx.skip(0x100)
        ctx._next_state(OmParsingPartitionTable)
        return
