import ctypes
import pathlib

_lib = ctypes.CDLL(str(pathlib.Path(__file__).parent / "libmyproject.so"))

NULL_INDEX = 0xFFFFFFFF

# lifecycle
_lib.tree_new.argtypes           = []
_lib.tree_new.restype            = ctypes.c_void_p
_lib.tree_free.argtypes          = [ctypes.c_void_p]
_lib.tree_free.restype           = None

# error — per tree
_lib.tree_error_code.argtypes    = [ctypes.c_void_p]
_lib.tree_error_code.restype     = ctypes.c_int
_lib.tree_error_msg.argtypes     = [ctypes.c_void_p]
_lib.tree_error_msg.restype      = ctypes.c_char_p
_lib.tree_error_clear.argtypes   = [ctypes.c_void_p]
_lib.tree_error_clear.restype    = None

# error — global fallback
_lib.global_error_code.argtypes  = []
_lib.global_error_code.restype   = ctypes.c_int
_lib.global_error_msg.argtypes   = []
_lib.global_error_msg.restype    = ctypes.c_char_p

# parse
_lib.tree_open_file.argtypes     = [ctypes.c_void_p, ctypes.c_char_p]
_lib.tree_open_file.restype      = ctypes.c_int
_lib.tree_parse.argtypes         = [ctypes.c_void_p]
_lib.tree_parse.restype          = ctypes.c_int
_lib.tree_close_file.argtypes    = [ctypes.c_void_p]
_lib.tree_close_file.restype     = None

# node access
_lib.tree_node_count.argtypes    = [ctypes.c_void_p]
_lib.tree_node_count.restype     = ctypes.c_size_t
_lib.tree_root.argtypes          = [ctypes.c_void_p]
_lib.tree_root.restype           = ctypes.c_uint32
_lib.node_kind.argtypes          = [ctypes.c_void_p, ctypes.c_uint32]
_lib.node_kind.restype           = ctypes.c_uint8
_lib.node_start.argtypes         = [ctypes.c_void_p, ctypes.c_uint32]
_lib.node_start.restype          = ctypes.c_uint64
_lib.node_end.argtypes           = [ctypes.c_void_p, ctypes.c_uint32]
_lib.node_end.restype            = ctypes.c_uint64
_lib.node_child_count.argtypes   = [ctypes.c_void_p, ctypes.c_uint32]
_lib.node_child_count.restype    = ctypes.c_uint32
_lib.node_child.argtypes         = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32]
_lib.node_child.restype          = ctypes.c_uint32


class ParseError(Exception):
    def __init__(self, code: int, msg: str):
        super().__init__(msg)
        self.code = code


def _check(tree_ptr, result: int):
    """Raise ParseError if result is -1."""
    if result == -1:
        code = _lib.tree_error_code(tree_ptr)
        msg  = _lib.tree_error_msg(tree_ptr)
        raise ParseError(code, msg.decode() if msg else "unknown error")


class ParseTree:
    def __init__(self):
        self._ptr = _lib.tree_new()
        if not self._ptr:
            code = _lib.global_error_code()
            msg  = _lib.global_error_msg()
            raise ParseError(code, msg.decode() if msg else "tree_new failed")

    def __del__(self):
        if self._ptr:
            _lib.tree_free(self._ptr)
            self._ptr = None

    # --- parse interface ---

    def open_file(self, path: str):
        _check(self._ptr, _lib.tree_open_file(self._ptr, path.encode()))

    def parse(self):
        _check(self._ptr, _lib.tree_parse(self._ptr))

    def close_file(self):
        _lib.tree_close_file(self._ptr)

    def clear_error(self):
        _lib.tree_error_clear(self._ptr)

    # --- node access ---

    def node_count(self) -> int:
        return _lib.tree_node_count(self._ptr)

    def root(self) -> int:
        return _lib.tree_root(self._ptr)

    def node_kind(self, index: int) -> int:
        return _lib.node_kind(self._ptr, index)

    def node_start(self, index: int) -> int:
        return _lib.node_start(self._ptr, index)

    def node_end(self, index: int) -> int:
        return _lib.node_end(self._ptr, index)

    def node_child_count(self, index: int) -> int:
        return _lib.node_child_count(self._ptr, index)

    def node_child(self, node_index: int, child_index: int) -> int:
        return _lib.node_child(self._ptr, node_index, child_index)