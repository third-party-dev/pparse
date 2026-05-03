pub mod node;
pub mod parser;
pub mod lazy;


use alloc::boxed::Box;
use alloc::rc::Rc;
use alloc::vec::Vec;

use crate::sys::cstdlib;
use crate::sys::cstdlib::{
    O_RDONLY,
    SEEK_SET,
};

use core::fmt::{
    Display,
    Formatter,
    Result as FmtResult
};

pub struct ErrnoException { msg: Box<str>, errno: i32, }
impl ErrnoException {
    pub fn new(msg: Box<str>, errno: i32) -> Self {
        ErrnoException { msg: msg, errno: errno }
    }
}
pub struct EndOfDataException { msg: Box<str>, }
pub struct EndOfNodeException { msg: Box<str>, }
pub struct UnsupportedFormatException { msg: Box<str>, }
pub struct BufferFullException { msg: Box<str>, }
pub struct ValueException { msg: Box<str>, }


pub enum Exception {
    Errno(ErrnoException),
    Value(ValueException),
    EndOfData(EndOfDataException),
    EndOfNode(EndOfNodeException),
    UnsupportedFormat(UnsupportedFormatException),
    BufferFull(BufferFullException),
}

impl From<ErrnoException> for Exception {
    fn from(e: ErrnoException) -> Self { Exception::Errno(e) }
}

impl From<EndOfDataException> for Exception {
    fn from(e: EndOfDataException) -> Self { Exception::EndOfData(e) }
}

impl From<EndOfNodeException> for Exception {
    fn from(e: EndOfNodeException) -> Self { Exception::EndOfNode(e) }
}

impl From<UnsupportedFormatException> for Exception {
    fn from(e: UnsupportedFormatException) -> Self { Exception::UnsupportedFormat(e) }
}

impl From<BufferFullException> for Exception {
    fn from(e: BufferFullException) -> Self { Exception::BufferFull(e) }
}

impl From<ValueException> for Exception {
    fn from(e: ValueException) -> Self { Exception::Value(e) }
}

impl Display for Exception {
    fn fmt(&self, f: &mut Formatter<'_>) -> FmtResult {
        match self {
            Exception::Errno(e) => write!(f, "errno {}: {}", e.errno, e.msg),
            Exception::Value(e) => write!(f, "ValueError: {}", e.msg),
            Exception::EndOfData(e) => write!(f, "EndOfData: {}", e.msg),
            Exception::EndOfNode(e) => write!(f, "EndOfNode: {}", e.msg),
            Exception::UnsupportedFormat(e) => write!(f, "UnsupportedFormat: {}", e.msg),
            Exception::BufferFull(e) => write!(f, "BufferFull: {}", e.msg),
        }
    }
}




pub trait Reader {
    fn tell(&self) -> u64;
    fn seek(&mut self, offset: u64) -> Result<u64, Exception>; // returns tell()
    fn skip(&mut self, length: u64) -> Result<u64, Exception>; // returns seek() i.e tell()
    fn peek(&mut self, length: u64) -> Result<Vec<u8>, Exception>;
    fn read(&mut self, length: u64) -> Result<Vec<u8>, Exception>;
}

// Data is the user-mode low level IO interface.
pub trait Data {
    fn length(&self) -> Result<u64, Exception>;
    fn seek(&self, cursor: &Cursor) -> Result<u64, Exception>; // returns cursor.tell()
    fn peek(&self, cursor: &Cursor, length: u64) -> Result<Vec<u8>, Exception>;
    fn read(&self, cursor: &mut Cursor, length: u64) -> Result<Vec<u8>, Exception>;
}

pub struct FileData {
    length: u64,
    fd: i32,
}

impl FileData {
    pub fn open(fpath: &[u8]) -> Result<Self, Exception> {
        match cstdlib::stat(fpath) {
            Ok(s) => match cstdlib::open(fpath, O_RDONLY) {
                Ok(fd) => Ok(FileData { length: s.st_size as u64, fd: fd }),
                Err(errno) => {
                    let msg = Box::from("Failed to open file.");
                    Err(Exception::Errno(ErrnoException::new(msg, errno)))
                },
            },
            Err(errno) => {
                let msg = Box::from("Failed to stat file.");
                Err(Exception::Errno(ErrnoException::new(msg, errno)))
            },
        }
    }
}

// FileData is the user-mode low level IO interface for files via std io.
// Note: This does not support mmap'ed files, streams, or buffers.
impl Data for FileData {
    fn length(&self) -> Result<u64, Exception> { Ok(self.length) }

    fn seek(&self, cursor: &Cursor) -> Result<u64, Exception>
    {
        match cstdlib::lseek(self.fd, cursor.tell() as i64, SEEK_SET) {
            Err(errno) => {
                let msg = Box::from("Failed to seek file.");
                Err(Exception::Errno(ErrnoException::new(msg, errno)))
            },
            Ok(res) => Ok(res as u64),
        }
        // Reader responsible for updating cursor, not Data.
    }

    fn peek(&self, cursor: &Cursor, length: u64) -> Result<Vec<u8>, Exception> {
        self.seek(cursor)?;
        match cstdlib::read(self.fd, length as usize) {
            Err(errno) => {
                let msg = Box::from("Failed to peek file.");
                Err(Exception::Errno(ErrnoException::new(msg, errno)))
            },
            Ok(res) => Ok(res),
        }
        // No rewind because we seek for every read/peek.
    }

    fn read(&self, cursor: &mut Cursor, length: u64) -> Result<Vec<u8>, Exception> {
        self.seek(cursor)?;
        match cstdlib::read(self.fd, length as usize) {
            Err(errno) => {
                let msg = Box::from("Failed to read file.");
                Err(Exception::Errno(ErrnoException::new(msg, errno)))
            },
            Ok(res) => Ok(res),
        }
        // No rewind because we seek for every read/peek.
    }
}

pub struct DataUtl;
impl DataUtl {
    pub fn cursor(data: Rc<dyn Data>, offset: u64) -> Cursor {
        Cursor::new(data, offset)
    }

    pub fn range(cursor: &Cursor, length: u64) -> Range {
        Range::new(cursor, length)
    }
}

pub struct Cursor {
    data: Rc<dyn Data>,
    offset: u64,
}

impl Cursor {
    pub fn new(data: Rc<dyn Data>, offset: u64) -> Self {
        Cursor { data: data.clone(), offset: offset }
    }
    pub fn dup(&self) -> Cursor {
        Cursor::new(self.data.clone(), self.offset)
    }
}

// Note: Cursor is ignorant of length.
impl Reader for Cursor {
    fn tell(&self) -> u64 {
        self.offset
    }
    fn seek(&mut self, offset: u64) -> Result<u64, Exception>
    {
        self.offset = offset;
        self.data.clone().seek(self)
    }
    fn skip(&mut self, length: u64) -> Result<u64, Exception> {
        self.offset = self.offset + length;
        self.data.clone().seek(self)
    }
    fn peek(&mut self, length: u64) -> Result<Vec<u8>, Exception> {
        self.data.clone().peek(self, length)
    }
    fn read(&mut self, length: u64) -> Result<Vec<u8>, Exception> {
        let data = self.data.clone().read(self, length)?;
        self.offset = self.offset + (data.len() as u64);
        Ok(data)
    }
}


pub struct Range {
    pub start_cursor: Cursor,
    pub cursor: Cursor,
    pub _start: u64,
    pub _length: u64,
    pub _end: u64,
}

impl Range {

    pub fn new(cursor: &Cursor, length: u64) -> Self {
        Range {
            start_cursor: cursor.dup(),
            cursor: cursor.dup(),
            _start: cursor.tell(),
            _length: length,
            _end: cursor.tell() + length,
        }
    }
    
    pub fn dup(&self) -> Range {
        Range {
            start_cursor: self.start_cursor.dup(),
            cursor: self.cursor.dup(),
            _start: self._start,
            _length: self._length,
            _end: self._end,
        }
    }

    pub fn valid_offset(&self, offset: u64) -> bool {
        offset >= self._start && offset <= self._end
    }

    pub fn _adjust_length(&mut self, length: u64) -> u64 {
        let mut length = length;
        let offset = self.tell() + length;
        if !(self.valid_offset(offset)) {
            length = self._end - self.tell();
        }
        length
    }

    pub fn cursor(&self) -> Cursor { self.cursor.dup() }
    pub fn length(&self) -> u64 { self._length }
    pub fn left(&self) -> u64 { self._end - self.tell() }

    pub fn truncate(&mut self, new_length: u64) -> Result<&mut Range, Exception> {
        if new_length > self._length {
            let e = ValueException { msg: Box::from("Truncation of Range must be <= Range length") };
            return Err(Exception::Value(e));
        }
        if self.cursor.tell() > self._start + new_length {
            let e = ValueException { msg: Box::from("Range cursor must not be in truncated space.") };
            return Err(Exception::Value(e));
        }

        self._length = new_length;
        self._end = self._start + self._length;
        Ok(self)
    }

}

// Note: Cursor is ignorant of length.
impl Reader for Range {
    fn tell(&self) -> u64 {
        self.cursor.tell()
    }

    fn seek(&mut self, offset: u64) -> Result<u64, Exception>
    {
        let mut offset = offset;
        if ! self.valid_offset(offset) {
            if offset < self._start {
                offset = self._start;
            }
            else if offset > self._end {
                offset = self._end;
            }
        }
        self.cursor.seek(offset)
    }

    fn skip(&mut self, length: u64) -> Result<u64, Exception> {
        let length = self._adjust_length(length);
        self.cursor.skip(length)
    }

    fn peek(&mut self, length: u64) -> Result<Vec<u8>, Exception> {
        let length = self._adjust_length(length);
        self.cursor.peek(length)
    }

    fn read(&mut self, length: u64) -> Result<Vec<u8>, Exception> {
        let length = self._adjust_length(length);
        self.cursor.read(length)
    }
}