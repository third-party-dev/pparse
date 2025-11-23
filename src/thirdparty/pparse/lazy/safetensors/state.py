#!/usr/bin/env python3

import struct
import logging
log = logging.getLogger(__name__)

from thirdparty.pparse.lib import (
    EndOfDataException,
    UnsupportedFormatException,
    EndOfNodeException,
    Extraction,
    Range,
)

class SafetensorsParsingState(object):
    def parse_data(self, parser: 'Parser', ctx: 'NodeContext'):
        raise NotImplementedError()


# class SafetensorsParsingTensors(SafetensorsParsingState):

#     def parse_data(self, parser: 'Parser', ctx: 'NodeContext'):
#         '''
#           The tensor data isn't parsed. Its referenced using the header. All
#           tensor references in the header can become Safetensor nodes that permit
#           defered parsing and data _extraction_.

#           We should keep the start and end of the tensor data. Possibly keep
#           bookkeeping on every byte that is actually referenced. An array of
#           ranges and then find the holes?
#         '''

#         # data = ctx.peek(0x400)
#         # if len(data) < 1:
#         #     raise EndOfDataException("Not enough data to parse JSON whitespace")


class SafetensorsParsingTensors(SafetensorsParsingState):

    def parse_data(self, parser: 'Parser', ctx: 'NodeContext'):
        # Keep it going forward.
        data = ctx.read(4096*4096)
        if not data or len(data) < 1:
            ctx.node().tensor_data_end = ctx.tell()
            raise EndOfDataException("No more Safetensors tensor data.")


class SafetensorsParsingLength(SafetensorsParsingState):

    def parse_data(self, parser: 'Parser', ctx: 'NodeContext'):
        data = ctx.peek(8)
        if len(data) < 8:
            raise EndOfDataException("Not enough data to parse Safetensors Header Length")

        # Store header length in NodeInit
        header_length = struct.unpack('<Q', data)[0]
        ctx.node().header_length = header_length
        log.debug(f"Safetensors Header Length: {ctx.node().header_length}")
        ctx.skip(8)
            
        # TODO: Add extraction for json parser
        # Given name to attract parser only.
        header_json = Extraction(reader=Range(ctx.reader(), header_length), name='.json')
        parser.source()._extractions.append(header_json)
        ctx.skip(header_length)

        # TODO: If we add extraction, do children, and then add more extractions ... 
        # what happens to the extractions that were already complete? What if we need to
        # keep appending data to an extraction that has already been partially completed?

        ctx._next_state(SafetensorsParsingTensors)


