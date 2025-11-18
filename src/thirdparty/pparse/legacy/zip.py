#!/usr/bin/env python3

import sys
import struct
import zlib
import os
import urllib.parse
import io
from typing import Optional

import argparse

ZIP_SIGNATURE = b'PK\x03\x04'
ZIP_DIR_SIG = b'PK\x05\x06'
DATA_DESC_SIG = b'PK\x07\x08'
LOCAL_FILE_HEADER = b'PK\x01\x02'

class ZipParsingState():
    def parse_data(self, context: PObjParser):
        raise NotImplementedError()


class ZipParsingComplete(ZipParsingState):
    def parse_data(self, context: PObjParser):
        context._next_state(ZipParsingComplete)
    
class ZipParsingFinishDecompress(ZipParsingState):
    def parse_data(self, context: PObjParser):
        context._next_state(ZipParsingMagic)

class ZipParsingDataDescFooter(ZipParsingState):
    def parse_data(self, context: PObjParser):
        data = context.buffer.peek(16)
        if len(data) < 16:
            return EndOfDataException("Not enough data to parse data desc footer")
        
        desc = {}
        (desc['sig'], desc['crc32'], desc['comp_size'], desc['uncomp_size']) \
            = struct.unpack("<IIII", data[:16])
        meta = context.zip_entry.meta['zip_meta']

        if meta['crc32'] != 0 and meta['crc32'] != desc['crc32']:
            context._next_state(ZipParsingFinishDecompress)
            return

        context.buffer.read(16)
        context.zip_entry.meta['zip_desc'] = desc
        context._next_state(ZipParsingFinishDecompress)

class ZipParsingContinueDecompress(ZipParsingState):
    def __init__(self):
        self.decompressor = zlib.decompressobj(-zlib.MAX_WBITS)
        self._has_desc = False

    def _found_desc(self, context):
        return context.buffer.peek(4).find(DATA_DESC_SIG) != -1

    def _compare_crc32(self, given, data):
        return zlib.crc32(data) & 0xFFFFFFFF == given

    def parse_data(self, context: PObjParser):
        if len(context.buffer.peek(4)) < 4:
            raise EndOfDataException("Not enough data to continue decompression")
        
        # TODO: This should be able to handle anything between 4-N bytes, but
        # TODO: we should consider how we will chunk out very large buffers.

        meta = context.zip_entry.meta['zip_meta']
        data = context.buffer.peek(context.buffer.left())
        (used, unused, eof) = self.decompress_data(context, data)

        context.buffer.read(used)

        if eof:
            if meta['compression'] == 8:
                dedata = self.decompressor.flush()
                context.zip_entry.add_data(dedata)

            # flags & 0x08 == true means we explicitly have a data desc
            # it is possible for a data desc to show up without the flags too
            if self._has_desc or self._found_desc(context):
                context._next_state(ZipParsingDataDescFooter)
            else:
                context._next_state(ZipParsingFinishDecompress)

    def _decompress_data(self, context: PObjParser, comp_data):
        eof = False
        dedata = self.decompressor.decompress(comp_data)
        context.zip_entry.add_data(dedata)
        unused = len(self.decompressor.unused_data)
        used = len(comp_data) - unused
        return (used, unused, self.decompressor.eof)

    def decompress_data(self, context: PObjParser, compressed_data):
        meta = context.zip_entry.meta['zip_meta']
        # Be pesimistic
        used = 0
        unused = len(compressed_data)

        if meta['flags'] & 0x08:
            self._has_desc = True

        if meta['compression'] == 0:
            if context.zip_entry.meta['fname'].endswith('/'):
                return (0, 0, True)
            
            if meta['uncomp_size'] != 0:
                ze = context.zip_entry
                whats_left = meta['uncomp_size'] - ze.length()
                if whats_left > 0:
                    if whats_left > len(compressed_data):
                        whats_left = len(compressed_data)
                    ze.add_data(compressed_data[:whats_left])
                return (whats_left, len(compresed_data)-whats_left, ze.length() == meta['uncomp_size'])
            
            else:
                # Dumb search for DATA_DESC_SIG
                if len(compressed_data) - 3 < 1:
                    raise EndOfDataException("Not enough data for data copy with desc.")
                desc_off = compressed_data.find(DATA_DESC_SIG)
                if desc_off <= -1
                    # Not found, consume everything but last 3 bytes.
                    context.zip_entry.add_data(compressed_data[:-3])
                    return (len(compressed_data) - 3, 3, False)
                else:
                    # Verify the CRC32 to verify no collision.
                    buffer = context.zip_entry.buffer
                    bdata = buffer.byte_array[:buffer.length]
                    eof = self._compare_crc32(meta['crc32'], bdata)
                    if not eof:
                        desc_off += 4
                    context.zip_entry.add_data(compressed_data[:desc_off])
                    return (desc_off, len(compressed_data) - desc_off, eof)
        
        elif meta['compressed'] == 8:
            if not self._has_desc and meta['uncomp_size'] == context.zip_entry.length():
                return (meta['comp_size'], 0, True)
            return self._decompress_data(context, compressed_data)
        else:
            raise Exception(f"Compression not supported. {meta['compression']}")

        return (used, unused, False)

class ZipParsingStartDecompress(ZipParsingState):
    def parse_data(self, context: PObjParser):
        context._next_state(ZipParsingContinueDecompress)


class ZipParsingEntryExtra(ZipParsingState):
    def parse_data(self, context: PObjParser):
        extra_len = context.zip_entry.meta['zip_meta']['extra_len']
        if len(context.buffer.peek(extra_len)) < extra_len:
            raise EndOfDataException("Not enough data to parse entry extra.")
        
        data = context.buffer.read(extra_len)
        context.zip_entry.meta['zip_meta']['extra'] = data[:extra_len]

        context._next_state(ZipParsingStartDecompress)

class ZipParsingEntryFilename(ZipParsingState):
    def parse_data(self, context: PObjParser):
        fname_len = context.zip_entry.meta['zip_meta']['fname_len']
        if len(context.buffer.peek(fname_len)) < fname_len:
            raise EndOfDataException("Not enough data to parse file name")
        
        data = context.buffer.read(fname_len)
        context.zip_entry.meta['fname'] = data[:fname_len].decode('utf-8')

        context._next_state(ZipParsingEntryExtra)

class ZipParsingEntryHeader(ZipParsingState):
    def parse_data(self, context: PObjParser):
        if len(context.buffer.peek(26)) < 26:
            raise EndOfDataException("Not enough data to parse header.")

        context.zip_entry.meta['zip_meta'] = {}
        meta = context.zip_entry.meta['zip_meta']

        data = context.buffer.read(26)
        ( meta['version'], meta['flags'], meta['compression'], meta['mod_time'],
          meta['mod_date'], meta['crc32'], meta['comp_size'], meta['uncomp_size'],
          meta['fname_len'], meta['extra_len'],
        ) = struct.unpack('<HHHHHIIIHH', data[:26])

        context._next_state(ZipParsingEntryFilename)

class ZipParsingMagic(ZipParsingState):
    def parse_data(self, context: PObjParser):
        if len(context.buffer.peek(4)) < 4:
            raise EndOfDataException("Not enough data to detect zip magic")
        
        data = context.buffer.read(4)
        if data[0:4] == ZIP_DIR_SIG:
            context._next_state(ZipParsingComplete)
        elif data[0:4] == LOCAL_FILE_HEADER:
            context._next_state(ZipParsingComplete)
        elif data[0:4] == ZIP_SIGNATURE:
            context.zip_entry = PObjBuffer(context)
            context.children.append(context.zip_entry)
            context._next_state(ZipParsingEntryHeader)
        else:
            breakpoint()
            raise UnsupportedFormatException(f"Invalid Zip Magic Bytes: {data}")

class PartialUnzip(PObjParser):

    @staticmethod
    def match_extension(fname: str):
        if not fname:
            return False
        #for ext in ['.onnx']:
        for ext in ['.zip']:
            if fname.endswith(ext):
                return True
        return False


    @staticmethod
    def match_magic(cursor: pparse.Cursor):
        return False

    def __init__(self, parent: PObjBuffer, id: str):
        super.__init__(parent, id)
        self.state = ZipParsingMagic()
        self.zip_entry = None

    def _next_state(self, state):
        self.state = state

    def process_data(self):
        pass

    