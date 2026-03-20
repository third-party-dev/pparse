# Notes

## Design

Starting over ... we use the reflection.fbs to generate python bindings:

```sh
pip install flatbuffers
flatc --python reflection.fbs
```

Then we'll compile the schema we want to process:

`flatc --binary --schema path/to/tflite/schema.fbs`

This will create `schema.bfbs`. We then parse `schema.bfbs` with the reflection bindings. Access to the schema in this way allows us to _pparse_ a target tflite file. Note: If you intend to load the whole tflite into memory at once, it'll be more straight forward to use a tflite binding.

You can also parse the schema by serializing to JSON:

`flatc --json --schema schema.fbs`



`----------------------------------`








`tensorflow/lite/schema/schema.fbs`

`flatc --binary --schema --reflect-types --reflect-names schema.fbs`

Builds target schema into a binary descriptor (`bfbs`) that meets `reflection.fbs` schema.

```python
    # Load reflection schema to interpret the compiled schema
    from reflection import Schema  # from generated reflection Python code
    
    with open("schema.bfbs","rb") as f:
        buf = f.read()
    
    schema = Schema.GetRootAsSchema(buf, 0)
```


```python
    import struct
    
    class ByteProvider:
        def __init__(self, f):
            self.f = f
    
        def read_at(self, offset, size):
            self.f.seek(offset)
            return self.f.read(size)
    
        def u8(self, off):  return self.read_at(off, 1)[0]
        def i16(self, off): return struct.unpack('<h', self.read_at(off, 2))[0]
        def u16(self, off): return struct.unpack('<H', self.read_at(off, 2))[0]
        def u32(self, off): return struct.unpack('<I', self.read_at(off, 4))[0]
        def i32(self, off): return struct.unpack('<i', self.read_at(off, 4))[0]
    
    def read_uoffset(buf, off):
        return buf.u32(off)
    
    def read_string(buf, off):
        strlen = buf.u32(off)
        return buf.read_at(off + 4, strlen).decode("utf-8")
    
    def read_vector(buf, off):
        length = buf.u32(off)
        base = off + 4
        return length, base
    
    class Table:
        def __init__(self, buf, table_pos):
            self.buf = buf
            self.table_pos = table_pos
    
            vtable_rel = buf.i32(table_pos)
            self.vtable_pos = table_pos - vtable_rel
    
            self.vtable_len = buf.u16(self.vtable_pos)
            self.obj_len = buf.u16(self.vtable_pos + 2)
    
        def field_offset(self, field_id):
            vt_off = 4 + field_id * 2
            if vt_off >= self.vtable_len:
                return 0
            return self.buf.u16(self.vtable_pos + vt_off)
    
        def field_pos(self, field_id):
            off = self.field_offset(field_id)
            if off == 0:
                return None
            return self.table_pos + off
    
    class ReflectionSchema:
        def __init__(self, buf):
            root = buf.u32(0)
            self.schema = Table(buf, root)
    
        def root_table(self):
            # field 0 = root_table
            off = self.schema.field_pos(0)
            uoff = self.buf.u32(off)
            return Table(self.buf, off + uoff)
    
    '''
    table Model {
    version:uint;
    operator_codes:[OperatorCode];
    subgraphs:[SubGraph];
    description:string;
    buffers:[Buffer];
    }
    '''
    
    class TFLiteModel:
        def __init__(self, buf):
            root = buf.u32(0)
            self.model = Table(buf, root)
    
        def version(self):
            pos = self.model.field_pos(0)
            return self.model.buf.u32(pos)
    
        def description(self):
            pos = self.model.field_pos(3)
            if not pos:
                return None
            uoff = self.model.buf.u32(pos)
            return read_string(self.model.buf, pos + uoff)
    
        def subgraphs(self):
            pos = self.model.field_pos(2)
            if not pos:
                return []
    
            uoff = self.model.buf.u32(pos)
            vec_off = pos + uoff
    
            n, base = read_vector(self.model.buf, vec_off)
            result = []
    
            for i in range(n):
                elem_uoff = self.model.buf.u32(base + i * 4)
                result.append(
                    Table(self.model.buf, base + i * 4 + elem_uoff)
                )
            return result
    
    def subgraph_name(buf, sg):
        pos = sg.field_pos(4)
        if not pos:
            return None
        uoff = buf.u32(pos)
        return read_string(buf, pos + uoff)
    
    with open("model.tflite", "rb") as f:
        buf = ByteProvider(f)
    
        model = TFLiteModel(buf)
    
        print("TFLite version:", model.version())
        print("Description:", model.description())
    
        for i, sg in enumerate(model.subgraphs()):
            print(f"Subgraph {i} name:", subgraph_name(buf, sg))
    
    
    '''
    table SubGraph {
    tensors:[Tensor];
    inputs:[int];
    outputs:[int];
    operators:[Operator];
    name:string;
    }
    '''

```

```python
    '''
    table Schema {
    root_table:Object;
    objects:[Object];
    }
    
    table Object {
    name:string;
    fields:[Field];
    }
    
    table Field {
    name:string;
    type:Type;
    offset:ushort;   // <<<<<< IMPORTANT
    id:ushort;
    }
    
    table Type {
    base_type:BaseType;
    element:BaseType;
    index:int;
    }
    '''
    
    def find_object(schema, name):
        for i in range(schema.objects_len()):
            obj = schema.objects(i)
            if obj.name().decode() == name:
                return obj
        return None
    
    model_object = find_object(schema, "tflite.Model")
    
    for i in range(model_object.fields_len()):
        field = model_object.fields(i)
        print(field.name().decode(), field.offset())
    
    '''
    version         offset=4
    operator_codes  offset=6
    subgraphs       offset=8
    description     offset=10
    buffers         offset=12
    '''
    
    def read_named_fields(buf, table, schema_object):
        result = {}
    
        for i in range(schema_object.fields_len()):
            field = schema_object.fields(i)
    
            vt_index = field.offset() // 2
            vt_entry_pos = table.vtable_pos + 4 + vt_index * 2
    
            if vt_entry_pos >= table.vtable_pos + table.vtable_len:
                continue
    
            field_rel = buf.u16(vt_entry_pos)
            if field_rel == 0:
                continue  # field not present
    
            field_pos = table.table_pos + field_rel
            result[field.name().decode()] = field_pos
    
        return result
    
    '''
    {
    "version": 1234,
    "subgraphs": <offset>,
    "buffers": <offset>,
    }
    '''
    
    t = field.type()
    base = t.base_type()
    elem = t.element()
    index = t.index()
    
    def decode_field(buf, field, field_pos):
        t = field.type()
    
        if t.base_type() == BaseType.Int:
            return buf.i32(field_pos)
    
        if t.base_type() == BaseType.UInt:
            return buf.u32(field_pos)
    
        if t.base_type() == BaseType.String:
            uoff = buf.u32(field_pos)
            return read_string(buf, field_pos + uoff)
    
        if t.base_type() == BaseType.Vector:
            uoff = buf.u32(field_pos)
            vec_pos = field_pos + uoff
            return decode_vector(buf, t, vec_pos)
    
        if t.base_type() == BaseType.Obj:
            uoff = buf.u32(field_pos)
            return Table(buf, field_pos + uoff)
    
        raise NotImplementedError
    
    def decode_table(buf, table, schema_object):
        result = {}
    
        for i in range(schema_object.fields_len()):
            field = schema_object.fields(i)
            off = table.field_offset(field.offset() // 2)
            if off == 0:
                continue
    
            field_pos = table.table_pos + off
            result[field.name().decode()] = decode_field(
                buf, field, field_pos
            )
    
        return result
    
    decoded = decode_table(buf, model_table, model_object)
    
    print(decoded["version"])
    print(len(decoded["subgraphs"]))

```
