#!/usr/bin/env python3

import sys
import struct
import os
import io

from typing import Optional

from thirdparty.pparse.lib import EndOfDataException, UnsupportedFormatException
import thirdparty.pparse.lib as pparse
#from thirdparty.pparse.lib import Range, Node, Cursor, Data, Parser, Artifact

def unzigzag(v):
    return (v >> 1) ^ -(v & 1)

def zigzag_i32(n):
    return (n << 1) ^ (n >> 31)

def zigzag_i64(n):
    return (n << 1) ^ (n >> 63)


class Protobuf():
    VARINT = 0
    I64 = 1
    LEN = 2
    SGROUP = 3
    EGROUP = 4
    I32 = 5

    FALSE = 0
    TRUE = 1

    wire_type_str = {
        0: "VARINT",
        1: "I64",
        2: "LEN",
        3: "SGROUP",
        4: "EGROUP",
        5: "I32",
    }


class ProtobufParsingState(object):
    def parse_data(self, parser: 'ProtobufParser'):
        raise NotImplementedError()


class ProtobufParsingLen(ProtobufParsingState):

    def parse_data(self, parser: 'ProtobufParser'):

        length = parser.parse_varint()
        print(f'  LEN VALUE {length}')
        # TODO: Is this the point we look up the key in proto to continue?

        data = parser.read(length)
        if not data or len(data) < length:
            msg = "Not enough data to parse Protobuf LEN data. " \
                f"Offset: {parser.tell()} Read: {len(data)} of {length}"
            raise EndOfDataException(msg)

        if len(data) < 16:
            print(f'  DATA: {data}')

        parser._next_state(ProtobufParsingKey)
        return


class ProtobufParsingKey(ProtobufParsingState):

    def parse_data(self, parser: 'ProtobufParser'):

        wire_type, field_num = parser.parse_varint_key()
        print(f'{field_num}:{Protobuf.wire_type_str[wire_type]} ')
        # TODO: Is this the point we look up the key in proto to continue?
        
        if wire_type == Protobuf.LEN:
            parser._next_state(ProtobufParsingLen)
            return

        if wire_type == Protobuf.VARINT:
            value = parser.parse_varint()
            print(f'  VALUE {value}')
            parser._next_state(ProtobufParsingKey)
            return

        # if wire_type == Protobuf.I64:
        #     parser._next_state(ProtobufParsingVarint)
        #     raise NotImplementedError()

        # if wire_type == Protobuf.LEN:
        #     parser._next_state(ProtobufParsingVarint)
        #     raise NotImplementedError()
        
        # if wire_type == Protobuf.SGROUP:
        #     parser._next_state(ProtobufParsingVarint)
        #     raise NotImplementedError()
        
        # if wire_type == Protobuf.EGROUP:
        #     parser._next_state(ProtobufParsingVarint)
        #     raise NotImplementedError()

        # if wire_type == Protobuf.I32:
        #     parser._next_state(ProtobufParsingVarint)
        #     raise NotImplementedError()

        raise UnsupportedFormatException(f"Not a valid Protobuf wire type. Type: {wire_type} ({Protobuf.wire_type_str[wire_type]})")


class ProtobufParser(pparse.Parser):

    @staticmethod
    def match_extension(fname: str):
        if not fname:
            return False
        for ext in ['.onnx']:
            if fname.endswith(ext):
                return True
        return False


    @staticmethod
    def match_magic(cursor: pparse.Cursor):
        return False

    
    def __init__(self, artifact: pparse.Artifact, id: str):
        super().__init__(artifact, id)

        self.state: Optional[ProtobufParsingState] = ProtobufParsingKey()

        # self.num_bytes = []
        # self.str_bytes = [b'"']
        # self.json_ref = None
        # self.current = None
        # self.stack = []
        # self.key_reg = None

    def _next_state(self, state: ProtobufParsingState):
        self.state = state()


    def parse_varint(self):
        value = 0
        shift = 0
        offset = 0

        while True:
            u8 = self.read(1)
            if not u8 or len(u8) < 1:
                raise EndOfDataException(f"Not enough data to parse Protobuf varint. Offset: {self.tell()}")
            u8 = ord(u8)
            value |= (u8 & 0x7F) << shift
            if not (u8 & 0x80):
                break
            shift += 7
        return value

    def parse_varint_key(self):
        value = self.parse_varint()
        return (value & 0x7), (value >> 3)

    def parse_length(self):
        length = self.parse_varint()
        # Is this raw data? # Do we need to key to know?
        data = self.read(length)
        if not data or len(data) < length:
            raise EndOfDataException(f"Not enough data to parse Protobuf LEN data. Offset: {self.tell()}")
        return data

    def parse_i32(self):
        data = self.read(4)
        if not data or len(data) < length:
            raise EndOfDataException(f"Not enough data to parse Protobuf I32 data. Offset: {self.tell()}")
        return struct.unpack("<I", data)[0]

    def parse_i64(self):
        data = self.read(8)
        if not data or len(data) < length:
            raise EndOfDataException(f"Not enough data to parse Protobuf I64 data. Offset: {self.tell()}")
        return struct.unpack("<Q", data)[0]

    







    # def _apply_value(self, value):
    #     if self.key_reg:
    #         self.current[self.key_reg] = value
    #         self.key_reg = None
    #     elif isinstance(self.current, list):
    #         self.current.append(value)
    #     elif isinstance(self.current, dict) and self.key_reg == None:
    #         self.key_reg = value
    #     else:
    #         self.current = value
    #         self._meta['root'] = self.current
    
    # def _start_map(self):
    #     self.stack.append(self.current)
    #     if self.key_reg:
    #         self.current[self.key_reg] = {}
    #         self.current = self.current[self.key_reg]
    #         self.key_reg = None
    #     elif isinstance(self.current, list):
    #         self.current.append({})
    #         self.current = self.current[-1]
    #     else:
    #         self.current = {}
    #         self._meta['root'] = self.current

    # def _start_array(self):
    #     self.stack.append(self.current)
    #     if self.key_reg:
    #         self.current[self.key_reg] = []
    #         self.current = self.current[self.key_reg]
    #         self.key_reg = None
    #     elif isinstance(self.current, list):
    #         self.current.append([])
    #         self.current = self.current[-1]
    #     else:
    #         self.current = []
    #         self._meta['root'] = self.current

    # def _end_container(self):
    #     if len(self.stack) > 1:
    #         self.current = self.stack.pop()
    #         self._meta['root'] = self.current
    
    def eagerly_parse(self):

        exc_store = None
        try:
            #breakpoint()
            #print(f"{self.state}.parse_data()")
            while True:
                self.state.parse_data(self)
        except EndOfDataException as e:
            if not exc_store:
                exc_store = e
        except UnsupportedFormatException:
            raise

        for child in self.children:
            try:
                child.scan_data()
            except EndOfDataException as e:
                if not exc_store:
                    exc_store = e
        
        if exc_store:
            raise exc_store

        return self


    def scan_data(self):
        return self.eagerly_parse()