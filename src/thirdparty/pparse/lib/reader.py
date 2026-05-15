# Api for Reader-like objects (Cursor, Range)
class Reader:
    def dup(self):
        raise NotImplementedError()

    def tell(self):
        raise NotImplementedError()

    def seek(self):
        raise NotImplementedError()

    def skip(self):
        raise NotImplementedError()

    def peek(self):
        raise NotImplementedError()

    def read(self):
        raise NotImplementedError()


# Cursor manages offset. (Data does not manage offset.)
# Cursor does not manage boundaries.
class Cursor(Reader):
    def __init__(self, data, offset=0):
        self._data = data
        self._offset = offset

    def cursor(self):
        return self

    def dup(self):
        return self._data.open(self._offset)

    # Where in the Data are we
    def tell(self):
        return self._offset

    # Set cursor to specific location.
    def seek(self, offset):
        self._offset = offset
        return self._data.seek(self)

    def skip(self, length):
        self._offset += length
        return self._data.seek(self)

    # Read data ahead without progressing cursor.
    def peek(self, length):
        return self._data.peek(self, length)

    # Copy and progress data.
    def read(self, length, mode=None):
        data = self._data.read(self, length)
        self._offset += len(data)
        return data


# Range manages length and boundaries.
# Range start cursor and length are assumed correct.
# - Range has no insight into data.
# - Length must not be < 0
# Cursor does not manage length.
# Data does not manage offset.
class Range(Reader):
    # Given Cursor object is the start offset
    def __init__(self, cursor, length: int, offset: int = -1):
        self._start_cursor = cursor.dup()
        self._init(cursor.tell(), length, offset)

    def _init(self, start_offset, length, current_offset=-1):
        self._start_cursor.seek(start_offset)
        self._start = self._start_cursor.tell()
        self._cursor = self._start_cursor.dup()

        if current_offset >= 0:
            self._cursor.seek(current_offset)
        if length < 0:
            raise ValueError("Length must not be < 0")
        # Consider: Check for length beyond data?
        self._length = length
        self._end = self._start + length

    def cursor(self):
        return self._cursor.dup()

    def dup(self):
        return Range(self._start_cursor, self._length, self._cursor.tell())

    def truncate(self, new_length):
        if new_length > self._length:
            raise Exception("Truncation of Range must be <= Range length")
        if self._cursor.tell() > self._start + new_length:
            raise Exception("Range cursor must not be in truncated space.")

        self._length = new_length
        self._end = self._start + self._length

        return self

    def length(self):
        return self._length

    def left(self):
        return self._end - self.tell()

    def valid_offset(self, offset):
        return offset >= self._start and offset <= self._end

    def tell(self):
        return self._cursor.tell()

    # Set cursor to absolute location in Data (within bounds).
    def seek(self, offset):
        if not self.valid_offset(offset):
            if offset < self._start:
                offset = self._start
            elif offset > self._end:
                offset = self._end
        self._cursor.seek(offset)
        return offset

    # Ensure length (relative to cursor) is inbounds.
    def _adjust_length(self, length):
        if length < 0:
            return 0
        offset = self.tell() + length
        if not self.valid_offset(offset):
            length = self._end - self.tell()
        return length

    # Progress data without reading.
    def skip(self, length):
        length = self._adjust_length(length)
        return self._cursor.skip(length)

    # Read data ahead without progressing cursor.
    def peek(self, length):
        length = self._adjust_length(length)
        return self._cursor.peek(length)

    # Read data and progress data.
    def read(self, length):
        length = self._adjust_length(length)
        return self._cursor.read(length)


