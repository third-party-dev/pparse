pub mod node;
pub mod parser;
pub mod lazy;


use alloc::boxed::Box;
use alloc::rc::Rc;


pub trait Reader {
    fn tell(&self) -> u64;
    fn seek(&mut self, offset: u64) -> u64; // returns tell()
    fn skip(&mut self, length: u64) -> u64; // returns seek() i.e tell()
    fn peek(&mut self, length: u64) -> Box<str>;
    fn read(&mut self, length: u64) -> Box<str>;
}

// Data is the user-mode low level IO interface.
pub trait Data {
    fn _load_length(&mut self); // loads data length into self.length
    //fn open(&self, offset: u64) -> Cursor;
    fn peek(&self, cursor: &Cursor, length: u64) -> Box<str>;
    fn seek(&self, cursor: &mut Cursor) -> u64; // returns cursor.tell()
    fn read(&self, cursor: &mut Cursor, length: u64) -> Box<str>;
}

pub struct FileData {
    length: u64,
    fd: i32,
}

impl FileData {
    pub fn open(fpath: Box<str>) -> Self {
        // TODO: do cstdlib open of fpath and assign return to fd
        FileData { length: 0, fd: -1 }
    }
}

// FileData is the user-mode low level IO interface for files via std io.
// Note: This does not support mmap'ed files, streams, or buffers.
impl Data for FileData {
    fn _load_length(&mut self) {
        // TODO: use stat()
        self.length = 0;
    }
    // fn open(&self, offset: u64) -> Cursor {
    //     // TODO: Check if offset in bounds?
    //     Cursor::new(self, offset)
    // }
    fn peek(&self, cursor: &Cursor, length: u64) -> Box<str> {
        // TODO: seek(cursor.tell(), os.SEEK_SET)
        // TODO: read(length)
        Box::from("mock_peek")
    }
    fn seek(&self, cursor: &mut Cursor) -> u64
    {
        // TODO: seek(cursor.tell(), os.SEEK_SET)
        cursor.tell()
    }
    fn read(&self, cursor: &mut Cursor, length: u64) -> Box<str> {
        // TODO: self.seek(cursor)
        // TODO: read(length)
        Box::from("mock_read")
    }
}

pub struct DataUtl;
impl DataUtl {
    pub fn open(data: Rc<dyn Data>, offset: u64) -> Cursor {
        Cursor::new(data, offset)
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
    fn dup(&self) -> Cursor {
        Cursor::new(self.data.clone(), self.offset)
    }
}

// Note: Cursor is ignorant of length.
impl Reader for Cursor {
    fn tell(&self) -> u64 {
        self.offset
    }
    fn seek(&mut self, offset: u64) -> u64
    {
        self.offset = offset;
        self.data.clone().seek(self)
    }
    fn skip(&mut self, length: u64) -> u64 {
        self.offset = self.offset + length;
        self.data.clone().seek(self)
    }
    fn peek(&mut self, length: u64) -> Box<str> {
        self.data.clone().peek(self, length)
    }
    fn read(&mut self, length: u64) -> Box<str> {
        let data = self.data.clone().read(self, length);
        self.offset = self.offset + (data.len() as u64);
        data
    }
}

