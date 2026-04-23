import io
import sys

def _print_cb(dst=sys.stdout, value=''):
    try:
        print(value, file=dst)
    except BrokenPipeError:
        # Thrown when truncating output (e.g. head).
        return


class Dumper:
    _default = None

    @classmethod
    def default(cls):
        if cls._default is None:
            cls._default = cls()
        return cls._default

    def __init__(self, dumpers=None, cb=_print_cb, dst=sys.stdout):
        import numbers
        from thirdparty.pparse.lib import Node
        from collections.abc import Iterable

        self.dumpers = dumpers
        if self.dumpers is None:
            self.dumpers = [
                [Node, self._dump_node_wrapper],
                [dict, self._dump_dict_wrapper],
                [bytes, self._dump_bytes_wrapper],
                [str, self._dump_str_wrapper],
                [int, self._dump_misc_wrapper],
                [float, self._dump_misc_wrapper],
                [numbers.Number, self._dump_misc_wrapper],
                [bool, self._dump_misc_wrapper],
                [type(None), self._dump_misc_wrapper],
                [io.BytesIO, self._dump_bytesio_wrapper],
                [Iterable, self._dump_iter_wrapper],
            ]
        
        self.cb=cb
        self.dst=dst


    def _dump_node_wrapper(self, elem_name="entry", obj=None, attrs='', depth=0, step=2):
        spacer = " " * depth
        self.cb(self.dst, f'{spacer}<{elem_name} value_is="Node" {attrs}>')
        obj.dump(depth + step)
        closing_attrs = ''
        if attrs and len(attrs) > 0:
            closing_attrs = f'<!-- tag_attrs: {attrs} -->'
        self.cb(self.dst, f'{spacer}</{elem_name}>{closing_attrs}')


    def _dump_dict_wrapper(self, elem_name="entry", obj=None, attrs='', depth=0, step=2):
        spacer = " " * depth
        if len(obj.keys()) == 0:
            self.cb(self.dst, f'{spacer}<{elem_name} value_is="dict" {attrs} empty="y"></{elem_name}>')
        else:
            self.cb(self.dst, f'{spacer}<{elem_name} value_is="dict" {attrs}>')
            self._dump_dict(obj, depth + step)
            closing_attrs = ''
            if attrs and len(attrs) > 0:
                closing_attrs = f'<!-- tag_attrs: {attrs} -->'
            self.cb(self.dst, f'{spacer}</{elem_name}>{closing_attrs}')


    def _dump_bytes_wrapper(self, elem_name="entry", obj=None, attrs='', depth=0, step=2):
        spacer = " " * depth
        if len(obj) == 0:
            self.cb(self.dst, f'{spacer}<{elem_name} value_is="bytes" {attrs} empty="y"></{elem_name}>')
        else:
            self.cb(self.dst, f'{spacer}<{elem_name} value_is="bytes" {attrs} length="{len(obj)}">')
            self._dump_bytes(obj, depth + step)
            closing_attrs = ''
            if attrs and len(attrs) > 0:
                closing_attrs = f'<!-- tag_attrs: {attrs} -->'
            self.cb(self.dst, f'{spacer}</{elem_name}>{closing_attrs}')


    def _dump_str_wrapper(self, elem_name="entry", obj=None, attrs='', depth=0, step=2):
        spacer = " " * depth
        if len(obj) == 0:
            self.cb(self.dst, f'{spacer}<{elem_name} value_is="str" {attrs} empty="y"></{elem_name}>')
        else:
            self.cb(self.dst, f'{spacer}<{elem_name} value_is="str" {attrs} length="{len(obj)}">')
            self._dump_str(obj, depth + step)
            closing_attrs = ''
            if attrs and len(attrs) > 0:
                closing_attrs = f'<!-- tag_attrs: {attrs} -->'
            self.cb(self.dst, f'{spacer}</{elem_name}>{closing_attrs}')


    def _dump_misc_wrapper(self, elem_name="entry", obj=None, attrs='', depth=0, step=2):
        spacer = " " * depth
        self.cb(self.dst, f'{spacer}<{elem_name} value_is="scalar" {attrs}>{obj}</{elem_name}>')


    def _dump_bytesio_wrapper(self, elem_name="entry", obj=None, attrs='', depth=0, step=2):
        spacer = " " * depth
        self.cb(self.dst, f'{spacer}<{elem_name} value_is="BytesIO" {attrs}>{obj}</{elem_name}>')


    def _dump_iter_wrapper(self, elem_name="entry", obj=None, attrs='', depth=0, step=2):
        spacer = " " * depth
        if len(obj) == 0:
            self.cb(self.dst, f'{spacer}<{elem_name} value_is="list" {attrs} empty="y"></{elem_name}>')
        else:
            self.cb(self.dst, f'{spacer}<{elem_name} value_is="list" {attrs}>')
            self._dump_list(obj, depth + step)
            closing_attrs = ''
            if attrs and len(attrs) > 0:
                closing_attrs = f'<!-- tag_attrs: {attrs} -->'
            self.cb(self.dst, f'{spacer}</{elem_name}>{closing_attrs}')


    def _dump_else_wrapper(self, elem_name="entry", obj=None, attrs='', depth=0, step=2):
        spacer = " " * depth
        self.cb(self.dst, f'{spacer}<{elem_name} value_is="unknown" {attrs}>')
        self.cb(self.dst, f'{spacer}{obj}')
        closing_attrs = ''
        if attrs and len(attrs) > 0:
            closing_attrs = f'<!-- tag_attrs: {attrs} -->'
        self.cb(self.dst, f'{spacer}</{elem_name}>{closing_attrs}')


    def _dump_str(self, obj, depth=0, step=2):
        spacer = " " * depth
        self.cb(self.dst, f'{spacer}<string>{obj}</string>')


    def _dump_bytes(self, obj, depth=0, step=2):
        # Bytes can be expressed in many ways:
        # hex dump, byte string dump, byte hex string dump, snippets.

        # As a default, we'll dump as is for first 16 bytes. If larger than
        # 16 bytes, we'll print the first 16 bytes and last 16 bytes.

        spacer = " " * depth
        if len(obj) <= 16:
            self.cb(self.dst, f'{spacer}{obj}')
        elif len(obj) >16:
            self.cb(self.dst, f'{spacer}{obj[:16]}')
            if len(obj) >= 32:
                self.cb(self.dst, f'{spacer}... snip ...')
                self.cb(self.dst, f'{spacer}{obj[-16:]}')
            else:
                self.cb(self.dst, f'{spacer}{obj[16:]}')


    # from thirdparty.pparse.lib import Node
    # print(ppobj.root_node().dump())
    def _dump_list(self, obj, depth=0, step=2):
        for idx in range(len(obj)):
            entry = obj[idx]
            entry_attrs = [f'idx="{idx}"']
            self.dump("entry", entry, ' '.join(entry_attrs), depth=depth, step=step)


    def _dump_dict(self, obj, depth=0, step=2):
        for key in obj:
            entry = obj[key]
            entry_attrs = [f'key="{key}"']
            self.dump("entry", entry, ' '.join(entry_attrs), depth=depth, step=step)


    # ** The only public call. **
    def dump(self, elem_name="entry", obj=None, attrs='', depth=0, step=2):
        for dumper in self.dumpers:
            if isinstance(obj, dumper[0]):
                dumper[1](elem_name=elem_name, obj=obj, attrs=attrs, depth=depth, step=step)
                return
        self._dump_else(elem_name=elem_name, obj=obj, attrs=attrs, depth=depth, step=step)


