#!/usr/bin/env python3

"""
Pure Python FlatBuffers Parser
Parses FlatBuffers binary files using JSON schema exported by flatc --schema
"""

import struct
import json
from typing import Any, Dict, List, Optional, Union


class FlatBuffersParser:
    """Parser for FlatBuffers binary format"""
    
    # Type format strings for struct.unpack - using base_type string names
    TYPE_FORMATS = {
        'Bool': '<?',
        'Byte': '<b',
        'UByte': '<B',
        'Short': '<h',
        'UShort': '<H',
        'Int': '<i',
        'UInt': '<I',
        'Long': '<q',
        'ULong': '<Q',
        'Float': '<f',
        'Double': '<d',
    }
    
    # Type sizes in bytes
    TYPE_SIZES = {
        'Bool': 1,
        'Byte': 1,
        'UByte': 1,
        'Short': 2,
        'UShort': 2,
        'Int': 4,
        'UInt': 4,
        'Long': 8,
        'ULong': 8,
        'Float': 4,
        'Double': 8,
    }
    
    def __init__(self, schema_json: Union[str, Dict], buffer: bytes):
        self.schema = schema_json
        self.buffer = buffer
        self.pos = 0
        
        # Lookup tables
        self.enums = {e['name']: e for e in self.schema.get('enums', [])}
        self.objects = {o['name']: o for o in self.schema.get('objects', [])}
        
        # Index-based lookup for objects
        self.objects_by_index = {}
        for idx, obj in enumerate(self.schema.get('objects', [])):
            self.objects_by_index[idx] = obj
        
    def read_scalar(self, offset: int, base_type: str) -> Any:
        """Read a scalar value at the given offset"""
        if base_type not in self.TYPE_FORMATS:
            raise ValueError(f"Unsupported scalar type: {base_type}")
        size = self.TYPE_SIZES[base_type]
        return struct.unpack(self.TYPE_FORMATS[base_type], self.buffer[offset:offset + size])[0]


    def read_u32(self, offset: int) -> int:
        """Read a 32-bit offset (soffset or uoffset)"""
        return struct.unpack('<I', self.buffer[offset:offset + 4])[0]
    
    def read_i32(self, offset: int) -> int:
        """Read a 32-bit signed offset"""
        return struct.unpack('<i', self.buffer[offset:offset + 4])[0]
    
    def read_string(self, offset: int) -> str:
        """Read a string at the given offset"""
        # Offset points to string length (uint32)
        length = struct.unpack('<I', self.buffer[offset:offset + 4])[0]
        # String data follows length
        string_data = self.buffer[offset + 4:offset + 4 + length]
        return string_data.decode('utf-8')
    
    def read_vector(self, offset: int, field_type: Dict) -> List[Any]:
        """Read a vector at the given offset"""

        elements = []
        length = self.read_u32(offset)
        current_offset = offset + 4
        
        element_type = field_type.get('element')
        
        # TODO: Unions? UTypes?

        if element_type == 'String':
            # Vector of strings (each element is an offset)
            for i in range(length):
                string_offset = self.read_u32(current_offset)
                abs_offset = current_offset + string_offset
                elements.append(self.read_string(abs_offset))
                current_offset += 4
                
        elif element_type == 'Obj':
            # Vector of tables (each element is an offset)
            type_index = field_type.get('index')
            if type_index is None:
                raise ValueError("Vector of objects missing 'index' field")
            if type_index not in self.objects_by_index:
                raise ValueError(f"Unknown object index: {type_index}")
            obj_schema = self.objects_by_index[type_index]
            type_name = obj_schema['name']
            
            for i in range(length):
                table_offset = self.read_u32(current_offset)
                abs_offset = current_offset + table_offset
                elements.append(self.read_table(abs_offset, type_name))
                current_offset += 4
                
        elif element_type in self.TYPE_SIZES:
            # Vector of scalars
            element_size = self.TYPE_SIZES[element_type]
            for i in range(length):
                elements.append(self.read_scalar(current_offset, element_type))
                current_offset += element_size
        else:
            raise ValueError(f"Unsupported vector element type: {element_type}")

        return elements
    
    def read_table(self, offset: int, type_name: str) -> Dict[str, Any]:
        """Read a table (object) at the given offset"""
        if type_name not in self.objects:
            raise ValueError(f"Unknown object type: {type_name}")
        obj_schema = self.objects[type_name]
        
        # Get (signed) vtable offset
        vtable_offset = self.read_i32(offset)
        vtable_pos = offset - vtable_offset
        
        # Read vtable: size of vtable, size of table, field offsets
        vtable_size = struct.unpack('<H', self.buffer[vtable_pos:vtable_pos + 2])[0]
        table_size = struct.unpack('<H', self.buffer[vtable_pos + 2:vtable_pos + 4])[0]
        field_offsets = []
        for i in range(4, vtable_size, 2):
            field_offset = struct.unpack('<H', self.buffer[vtable_pos + i:vtable_pos + i + 2])[0]
            field_offsets.append(field_offset)
        
        # Parse fields
        result = {}
        fields = obj_schema.get('fields', [])
        
        for field in fields:
            field_name = field['name']
            field_type = field['type']
            
            # Get the field ID (which determines position in vtable)
            # Fields are indexed by their 'id' if present, otherwise by order
            field_id = field.get('id', 0)
            
            # vtable entries correspond to field IDs
            # The vtable has entries for field 0, 1, 2, etc.
            if field_id >= len(field_offsets):
                # Field not present (using default value)
                continue
                
            field_offset_in_table = field_offsets[field_id]
            
            if field_offset_in_table == 0:
                # Field not present in this instance
                continue
                
            field_pos = offset + field_offset_in_table
            base_type = field_type.get('base_type')

            # TODO: Actually handle Unions and UTypes.
            if base_type == 'Union':
                '''
                {
                "name": "details",
                "type": { "base_type": "Union", "index": 11, "element_size": 1 },
                "id": 5,
                "offset": 14,
                "optional": true
                },
                '''
                self.read_scalar(field_pos, "UByte")
                self.read_u32(field_pos + 1)
                result[field_name] = "UNION PROCESSING NOT IMPLEMENTED"
            elif base_type == 'UType':
                val = self.read_scalar(field_pos, "UByte")
                if val != 0:
                    self.read_u32(field_pos + 1)
                result[field_name] = "UTYPE PROCESSING NOT IMPLEMENTED"
            
            elif base_type == 'String':
                # String is stored as offset
                string_offset = self.read_u32(field_pos)
                abs_offset = field_pos + string_offset
                result[field_name] = self.read_string(abs_offset)
                
            elif base_type == 'Vector':
                # Vector is stored as offset
                vector_offset = self.read_u32(field_pos)
                abs_offset = field_pos + vector_offset
                result[field_name] = self.read_vector(abs_offset, field_type)
                
            elif base_type == 'Obj':
                # Nested table stored as offset
                table_offset = self.read_u32(field_pos)
                abs_offset = field_pos + table_offset
                
                # Get nested type by index
                type_index = field_type.get('index')
                if type_index is None:
                    raise ValueError(f"Object field '{field_name}' missing 'index'")
                    
                if type_index not in self.objects_by_index:
                    raise ValueError(f"Unknown object index: {type_index}")
                    
                nested_obj = self.objects_by_index[type_index]
                nested_type = nested_obj['name']
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
        root_offset = self.read_u32(0)
        
        # Get root type from schema
        root_table = self.schema.get('root_table')
        if not root_table:
            raise ValueError("Schema does not specify root_table")
        
        root_type = root_table.get('name')
        if not root_type:
            raise ValueError("root_table does not specify name")
        
        # Parse root table
        return self.read_table(root_offset, root_type)


if __name__ == "__main__":
    with open("schema.json") as f:
        schema = json.load(f)

    # Load FlatBuffer binary
    with open("yolov5su_float32.tflite", "rb") as f:
        buffer = f.read()
    
    parser = FlatBuffersParser(schema, buffer)
    data = parser.parse()
    breakpoint()