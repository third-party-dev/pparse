#!/usr/bin/env python3

"""
Pure Python FlatBuffers Parser
Parses FlatBuffers binary files using JSON schema exported by flatc --schema
"""

import struct
import json
from typing import Any, Dict, List, Optional, Union
from enum import IntEnum


class BaseType(IntEnum):
    """FlatBuffers base types"""
    NONE = 0
    UTYPE = 1
    BOOL = 2
    BYTE = 3
    UBYTE = 4
    SHORT = 5
    USHORT = 6
    INT = 7
    UINT = 8
    LONG = 9
    ULONG = 10
    FLOAT = 11
    DOUBLE = 12
    STRING = 13
    VECTOR = 14
    OBJ = 15  # Table
    UNION = 16
    ARRAY = 17


class FlatBuffersParser:
    """Parser for FlatBuffers binary format"""
    
    # Type format strings for struct.unpack
    TYPE_FORMATS = {
        BaseType.BOOL: '?',
        BaseType.BYTE: 'b',
        BaseType.UBYTE: 'B',
        BaseType.SHORT: 'h',
        BaseType.USHORT: 'H',
        BaseType.INT: 'i',
        BaseType.UINT: 'I',
        BaseType.LONG: 'q',
        BaseType.ULONG: 'Q',
        BaseType.FLOAT: 'f',
        BaseType.DOUBLE: 'd',
    }
    
    # Type sizes in bytes
    TYPE_SIZES = {
        BaseType.BOOL: 1,
        BaseType.BYTE: 1,
        BaseType.UBYTE: 1,
        BaseType.SHORT: 2,
        BaseType.USHORT: 2,
        BaseType.INT: 4,
        BaseType.UINT: 4,
        BaseType.LONG: 8,
        BaseType.ULONG: 8,
        BaseType.FLOAT: 4,
        BaseType.DOUBLE: 8,
    }
    
    def __init__(self, schema_json: Union[str, Dict], buffer: bytes):
        """
        Initialize parser with schema and buffer
        
        Args:
            schema_json: JSON schema (as string or dict) from flatc --schema
            buffer: Binary FlatBuffers data
        """
        if isinstance(schema_json, str):
            self.schema = json.loads(schema_json)
        else:
            self.schema = schema_json
            
        self.buffer = buffer
        self.pos = 0
        
        # Build lookup tables
        self.enums = {e['name']: e for e in self.schema.get('enums', [])}
        self.objects = {o['name']: o for o in self.schema.get('objects', [])}
        
    def read_scalar(self, offset: int, base_type: int) -> Any:
        """Read a scalar value at the given offset"""
        if base_type not in self.TYPE_FORMATS:
            raise ValueError(f"Unsupported scalar type: {base_type}")
            
        fmt = '<' + self.TYPE_FORMATS[base_type]  # Little-endian
        size = self.TYPE_SIZES[base_type]
        
        value = struct.unpack(fmt, self.buffer[offset:offset + size])[0]
        return value
    
    def read_offset(self, offset: int) -> int:
        """Read a 32-bit offset (soffset or uoffset)"""
        return struct.unpack('<I', self.buffer[offset:offset + 4])[0]
    
    def read_soffset(self, offset: int) -> int:
        """Read a 32-bit signed offset"""
        return struct.unpack('<i', self.buffer[offset:offset + 4])[0]
    
    def read_string(self, offset: int) -> str:
        """Read a string at the given offset"""
        # Offset points to string length (uint32)
        length = struct.unpack('<I', self.buffer[offset:offset + 4])[0]
        # String data follows length
        string_data = self.buffer[offset + 4:offset + 4 + length]
        return string_data.decode('utf-8')
    
    def read_vector(self, offset: int, element_type: Dict) -> List[Any]:
        """Read a vector at the given offset"""
        # Vector format: length (uint32) followed by elements
        length = struct.unpack('<I', self.buffer[offset:offset + 4])[0]
        
        elements = []
        current_offset = offset + 4
        
        try:
            base_type = element_type.get('base_type')
        except:
            breakpoint()
        
        if base_type == BaseType.STRING:
            # Vector of strings - each element is an offset
            for i in range(length):
                string_offset = self.read_offset(current_offset)
                abs_offset = current_offset + string_offset
                elements.append(self.read_string(abs_offset))
                current_offset += 4
                
        elif base_type == BaseType.OBJ:
            # Vector of tables - each element is an offset
            type_name = element_type.get('type')
            for i in range(length):
                table_offset = self.read_offset(current_offset)
                abs_offset = current_offset + table_offset
                elements.append(self.read_table(abs_offset, type_name))
                current_offset += 4
                
        elif base_type in self.TYPE_SIZES:
            # Vector of scalars
            element_size = self.TYPE_SIZES[base_type]
            for i in range(length):
                elements.append(self.read_scalar(current_offset, base_type))
                current_offset += element_size
        else:
            raise ValueError(f"Unsupported vector element type: {base_type}")
            
        return elements
    
    def read_table(self, offset: int, type_name: str) -> Dict[str, Any]:
        """Read a table (object) at the given offset"""
        if type_name not in self.objects:
            raise ValueError(f"Unknown object type: {type_name}")
            
        obj_schema = self.objects[type_name]
        
        # Read vtable offset (signed offset before the table)
        vtable_offset = self.read_soffset(offset)
        vtable_pos = offset - vtable_offset
        
        # Read vtable
        # vtable format: size of vtable, size of table, field offsets...
        vtable_size = struct.unpack('<H', self.buffer[vtable_pos:vtable_pos + 2])[0]
        table_size = struct.unpack('<H', self.buffer[vtable_pos + 2:vtable_pos + 4])[0]
        
        # Read field offsets from vtable
        field_offsets = []
        for i in range(4, vtable_size, 2):
            field_offset = struct.unpack('<H', self.buffer[vtable_pos + i:vtable_pos + i + 2])[0]
            field_offsets.append(field_offset)
        
        # Parse fields
        result = {}
        fields = obj_schema.get('fields', [])
        
        for idx, field in enumerate(fields):
            field_name = field['name']
            field_type = field['type']
            
            # Field index in vtable (skip vtable_size and table_size)
            vtable_idx = idx
            
            if vtable_idx >= len(field_offsets):
                # Field not present (default value should be used)
                continue
                
            field_offset_in_table = field_offsets[vtable_idx]
            
            if field_offset_in_table == 0:
                # Field not present in this instance
                continue
                
            field_pos = offset + field_offset_in_table
            base_type = field_type.get('base_type')
            
            #breakpoint()

            if base_type in (BaseType.STRING, "String"):
                # String is stored as offset
                string_offset = self.read_offset(field_pos)
                abs_offset = field_pos + string_offset
                result[field_name] = self.read_string(abs_offset)
                
            elif base_type in (BaseType.VECTOR, "Vector"):
                # Vector is stored as offset
                vector_offset = self.read_offset(field_pos)
                abs_offset = field_pos + vector_offset
                element_type = field_type.get('element')
                result[field_name] = self.read_vector(abs_offset, element_type)
                
            elif base_type in (BaseType.OBJ, "Obj"):
                # Nested table stored as offset
                table_offset = self.read_offset(field_pos)
                abs_offset = field_pos + table_offset
                nested_type = field_type.get('type')
                result[field_name] = self.read_table(abs_offset, nested_type)
                
            elif base_type in self.TYPE_SIZES:
                # Scalar value stored inline
                result[field_name] = self.read_scalar(field_pos, base_type)
                
            else:
                raise ValueError(f"Unsupported field type: {base_type}")
        
        return result
    
    def parse(self) -> Dict[str, Any]:
        """Parse the FlatBuffers buffer and return the root object"""
        # Root offset is stored at the beginning of the buffer
        root_offset = self.read_offset(0)
        
        # Get root type from schema
        root_type = self.schema.get('root_type')
        if not root_type:
            raise ValueError("Schema does not specify root_type")
        
        # Parse root table
        return self.read_table(root_offset, root_type)


def parse_flatbuffer(schema_json: Union[str, Dict], buffer: bytes) -> Dict[str, Any]:
    """
    Convenience function to parse a FlatBuffer
    
    Args:
        schema_json: JSON schema from flatc --schema
        buffer: Binary FlatBuffers data
        
    Returns:
        Parsed data as a dictionary
    """
    parser = FlatBuffersParser(schema_json, buffer)
    return parser.parse()


# Example usage
if __name__ == "__main__":
    # Load schema JSON
    with open("schema.json") as f:
        schema = json.load(f)

    # Load FlatBuffer binary
    with open("yolov5su_float32.tflite", "rb") as f:
        buffer = f.read()

    # Example schema (simplified)
    # example_schema = {
    #     "root_type": "Monster",
    #     "objects": [
    #         {
    #             "name": "Monster",
    #             "fields": [
    #                 {"name": "hp", "type": {"base_type": BaseType.SHORT}},
    #                 {"name": "name", "type": {"base_type": BaseType.STRING}},
    #                 {"name": "inventory", "type": {
    #                     "base_type": BaseType.VECTOR,
    #                     "element": {"base_type": BaseType.UBYTE}
    #                 }}
    #             ]
    #         }
    #     ]
    # }
    
    parser = FlatBuffersParser(schema, buffer)
    data = parser.parse()
    breakpoint()

    # print("FlatBuffers Parser ready!")
    # print("Usage:")
    # print("  parser = FlatBuffersParser(schema_json, buffer)")
    # print("  data = parser.parse()")