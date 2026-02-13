import flatbuffers
import reflection.Schema as reflection_schema  # from the generated reflection.py

# Read the .bfbs file
with open("schema.bfbs", "rb") as f:
    bfbs_data = f.read()

# Use FlatBuffers Python API to access it
buf = bytearray(bfbs_data)
schema = reflection_schema.GetRootAsSchema(buf, 0)

for i in range(schema.ObjectsLength()):
    obj = schema.Objects(i)
    print("Table:", obj.Name().decode('utf-8'))
    for j in range(obj.FieldsLength()):
        field = obj.Fields(j)
        print("  Field:", field.Name().decode('utf-8'), "Type:", field.Type().BaseType())

'''
def get_string(buf, offset):
    return flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset).decode('utf-8')

# Example: access table dynamically (simplified)
table_offset = flatbuffers.encode.Get(flatbuffers.packer.uoffset, data, 0)
# Then use offsets from schema.Objects()[0].Fields() to read values
'''