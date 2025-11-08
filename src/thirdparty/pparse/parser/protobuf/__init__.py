#!/usr/bin/env python3

import sys
import struct
import os
import io

from typing import Optional

from thirdparty.pparse.lib import EndOfDataException, UnsupportedFormatException, Range
import thirdparty.pparse.lib as pparse
#from thirdparty.pparse.lib import Range, Node, Cursor, Data, Parser, Artifact

from thirdparty.pparse.parser.protobuf.meta import OnnxPb, Field, Protobuf
proto = OnnxPb()


def unzigzag(v):
    return (v >> 1) ^ -(v & 1)

def zigzag_i32(n):
    return (n << 1) ^ (n >> 31)

def zigzag_i64(n):
    return (n << 1) ^ (n >> 63)


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


class ProtobufParsingMessage(ProtobufParsingState):

    def parse_data(self, parser: 'ProtobufParser'):

        # Get the key data.
        wire_type, field_num = parser.parse_varint_key()
        field = parser.current_type_field(field_num)

        # Length follows VARINT and LEN wire types.
        length = parser.parse_varint()

        # Is this message repeated?
        if parser.current_type_repeated(field):



        # Register new message as current type in parser.
        parser.push_type(field, length)

        


        #


class ProtobufParsingKey(ProtobufParsingState):

    def parse_data(self, parser: 'ProtobufParser'):

        # Get the key data.
        wire_type, field_num, key_length = parser.peek_varint_key()
        field = parser.current_type_field(field_num)

        if field.type == Field.TYPE_MESSAGE:
            print(self.dbg_geninfo_str(parser, field_num, wire_type))
            print(self.dbg_proto_str(parser, field_num, wire_type))
            print(f"--- ProtobufParsingMessage: {field.type_name} ---")
            parser._next_state(ProtobufParsingMessage)
            return       

        # String or Scalar Follows, lets move past the key.
        parser.skip(key_length)
        
        if wire_type == Protobuf.VARINT:
            # Output everything to prove we can scan.
            print(self.dbg_geninfo_str(parser, field_num, wire_type))
            print(self.dbg_proto_str(parser, field_num, wire_type))
            value = parser.parse_varint()
            print(f'  VALUE: {value}')

            if field.name == 'node':
                breakpoint()

            parser._next_state(ProtobufParsingKey)
            return

        if wire_type == Protobuf.I64:
            # Output everything to prove we can scan.
            print(self.dbg_geninfo_str(parser, field_num, wire_type))
            print(self.dbg_proto_str(parser, field_num, wire_type))
            value = parser.parse_i64()
            print(f'  VALUE: {value}')
            parser._next_state(ProtobufParsingKey)

        if wire_type == Protobuf.I32:
            # Output everything to prove we can scan.
            print(self.dbg_geninfo_str(parser, field_num, wire_type))
            print(self.dbg_proto_str(parser, field_num, wire_type))
            value = parser.parse_i32()
            print(f'  VALUE: {value}')
            parser._next_state(ProtobufParsingKey)
    
        if wire_type == Protobuf.LEN:
            # As a LEN, this can be a SubMessage, String, Bytes, Repeated, or Packed

            # Output everything to prove we can scan.
            print(self.dbg_geninfo_str(parser, field_num, wire_type))
            print(self.dbg_proto_str(parser, field_num, wire_type))

            length = parser.parse_varint()
            print(f'  LENGTH: {length}')

            if field.type == Field.TYPE_STRING:
                data = parser.read(length)
                if not data or len(data) < length:
                    msg = "Not enough data to parse Protobuf LEN data. " \
                        f"Offset: {parser.tell()} Read: {len(data)} of {length}"
                    raise EndOfDataException(msg)

                if len(data) < 100:
                    try:
                        print(f'  DATA: "{data.decode('utf-8')}"')
                    except UnicodeDecodeError:
                        print(f'  rDATA: {data}')
                
                parser._next_state(ProtobufParsingKey)
                return
    
            else:
                print("-- skipping non-submessage LEN entry for now --")

                skipped = parser.skip(length)
                if skipped < length:
                    msg = "Not enough data to parse Protobuf LEN data. " \
                        f"Offset: {parser.tell()} Read: {len(data)} of {length}"
                    raise EndOfDataException(msg)

                parser._next_state(ProtobufParsingKey)
                return

            

        # if wire_type == Protobuf.SGROUP:
        #     parser._next_state(ProtobufParsingVarint)
        #     raise NotImplementedError()
        
        # if wire_type == Protobuf.EGROUP:
        #     parser._next_state(ProtobufParsingVarint)
        #     raise NotImplementedError()

        raise UnsupportedFormatException(f"Not a valid Protobuf wire type. Type: {wire_type} ({Protobuf.wire_type_str[wire_type]})")


    def dbg_geninfo_str(self, parser, field_num, wire_type):
        return f'{field_num} (FIELD)\n  TYPE: {Protobuf.wire_type_str[wire_type]}'


    def dbg_proto_str(self, parser, field_num, wire_type):
        type_entry = parser.current_type()
        field = proto.by_type_name(type_entry.type_name).by_id(field_num)
        out = [
            f'  CONTAINER: {type_entry.type_name}',
            f'  FIELD_NAME: {field.name}',
            f'  FIELD_TYPE: {field.type_str()}',
        ]
        if field.type == 11:
            out.append(f'  FIELD_MSG_TYPE: {field.type_name}')
        return '\n'.join(out)


class TypeStackEntry():
    def __init__(self, parser, field, length=-1):
        self.field = field
        self.type_name = field.type_name

        if length == -1:
            self.range = parser.reader().dup()
        else:
            self.range = Range(parser.reader(), length)


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

        self._type_stack = [TypeStackEntry(self, '.onnx.ModelProto', -1)]


    def _next_state(self, state: ProtobufParsingState):
        self.state = state()


    def current_type(self):
        return self._type_stack[-1]


    def push_type(self, type_name, length):
        self._type_stack.append(TypeStackEntry(self, type_name, length))
        return self.current_type()

    
    def pop_type(self):
        return self._type_stack.pop()


    def current_type_field(self, field_num):
        return proto.by_type_name(self.current_type().type_name).by_id(field_num)


    def current_type_matches(self, field):
        cur_field = self.current_type().field
        return cur_field == field


    def current_type_repeated(self, field):
        cur_field = self.current_type().field
        return cur_field == field and cur_field.label == Field.LABEL_REPEATED


    # Convienence Aliases
    def tell(self):
        return self.current_type().range.tell()
    def seek(self, offset):
        return self.current_type().range.seek(offset)
    def skip(self, length):
        return self.current_type().range.skip(length)
    def peek(self, length):
        return self.current_type().range.peek(length)
    def read(self, length, mode=None):
        return self.current_type().range.read(length, mode=mode)


    def parse_varint(self, peek=False):
        value = 0
        shift = 0
        offset = 0
        start = self.tell()

        while True:
            u8 = self.read(1)
            if not u8 or len(u8) < 1:
                raise EndOfDataException(f"Not enough data to parse Protobuf varint. Offset: {self.tell()}")
            u8 = ord(u8)
            value |= (u8 & 0x7F) << shift
            if not (u8 & 0x80):
                break
            shift += 7
        
        if peek:
            self.seek(start)
        return value
    

    def peek_varint(self):
        value = 0
        shift = 0
        start = self.tell()

        while True:
            u8 = self.read(1)
            if not u8 or len(u8) < 1:
                raise EndOfDataException(f"Not enough data to parse Protobuf varint. Offset: {self.tell()}")
            u8 = ord(u8)
            value |= (u8 & 0x7F) << shift
            if not (u8 & 0x80):
                break
            shift += 7
        
        end = self.tell()
        self.seek(start)
        return value, end-start


    def parse_varint(self):
        value, length = self.peek_varint()
        self.skip(length)
        return value


    def peek_varint_key(self):
        value, length = self.peek_varint(peek)
        return (value & 0x7), (value >> 3), length


    def parse_varint_key(self, peek=False):
        value = self.parse_varint(peek)
        return (value & 0x7), (value >> 3)


    def parse_i32(self, peek=False):
        data = None
        if peek:
            data = self.peek(4)
        else:
            data = self.read(4)
        if not data or len(data) < 4:
            raise EndOfDataException(f"Not enough data to parse Protobuf I32 data. Offset: {self.tell()}")
        return struct.unpack("<I", data)[0]


    def parse_i64(self, peek=False):
        data = None
        if peek:
            data = self.peek(8)
        else:
            data = self.read(8)
        if not data or len(data) < 8:
            raise EndOfDataException(f"Not enough data to parse Protobuf I64 data. Offset: {self.tell()}")
        return struct.unpack("<Q", data)[0]

    
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