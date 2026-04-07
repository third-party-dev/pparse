
class FlatbuffersSchema():

    def __init__(self, schema_obj={}):
        # TODO: Consider default should have all references below (but empty)?
        self._schema = schema_obj

        self.root_table_name = self._schema['root_table']['name']

        #self.enums = {e['name']: e for e in self._schema.get('enums', [])}
        self.enums = self._schema.get('enums', [])
        self.objects = {o['name']: o for o in self._schema.get('objects', [])}
                
        self.objects_by_index = {}
        for idx, obj in enumerate(self._schema.get('objects', [])):
            self.objects_by_index[idx] = obj

        self.enums_by_index = {}
        for idx, enum in enumerate(self._schema.get('enums', [])):
            self.enums_by_index[idx] = enum

        # Type format strings for struct.unpack - using base_type string names
        self.TYPE_FORMATS = {
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
        self.TYPE_SIZES = {
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