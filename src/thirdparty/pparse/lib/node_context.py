
from .reader import (
    Reader,
    Range,
)

class NodeContext:
    def __init__(self, parent: "Node", reader: Reader, parser: "Parser"):
        self._reader = reader.dup()
        self._reader.seek(reader.tell())
        self._state = None
        self._parent = parent  # Parent Node (None for root)
        self._start = self.tell()
        self._end = None
        self._parser = parser
        # When doing a recursive parse, list of descendent references.
        self._descendants = []

    def parent(self):
        return self._parent

    def parent_ctx(self):
        if self._parent:
            return self._parent.ctx()
        return None

    def reader(self):
        return self._reader.dup()

    def state(self):
        return self._state

    def parser(self):
        return self._parser

    def _next_state(self, state):
        self._state = state()

    def set_remaining(self, length):
        self._end = self.tell() + length

    def mark_end(self, node):
        self._end = self.tell()
        node.set_length(self._end - self._start)

    def mark_field_start(self):
        self._field_start = self.tell()

    def field_start(self):
        return self._field_start

    def dup(self):
        return self._reader.dup()

    def tell(self):
        return self._reader.tell()

    def seek(self, *args, **kwargs):
        return self._reader.seek(*args, **kwargs)

    def skip(self, *args, **kwargs):
        return self._reader.skip(*args, **kwargs)

    def peek(self, *args, **kwargs):
        return self._reader.peek(*args, **kwargs)

    def read(self, *args, **kwargs):
        return self._reader.read(*args, **kwargs)

    def left(self):
        if not isinstance(self._reader, Range):
            raise Exception("Reader must be range to use left()")
        return self._reader.left()