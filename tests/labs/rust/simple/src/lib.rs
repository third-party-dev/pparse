use libc;
use alloc::boxed::Box;
use alloc::vec;
use alloc::vec::Vec;
use alloc::ffi::CString;
use core::result::Result;


pub trait Data {
    //fn len(&self) -> usize;
    fn tell(&self) -> u64;
    fn seek(&self, offset: u64) -> u64;
    fn peek(&self, length: u64) -> &Box<[u8]>;
    fn read(&self, length: u64) -> &Box<[u8]>;
}

pub struct FileData {
    fd: i32,
    offset: usize,
}

impl Data for FileData {


    fn seek(&mut self, offset: usize) {
        self.offset = offset;
        unsafe {
            libc::lseek(self.fd, offset as i64, libc::SEEK_SET);
        }
    }

    fn read(&mut self, buf: &mut [u8]) -> usize {
        let n = unsafe {
            libc::read(
                self.fd,
                buf.as_mut_ptr() as *mut libc::c_void,
                buf.len(),
            )
        };
        if n > 0 {
            self.offset += n as usize;
        }
        n as usize
    }

    fn peek(&self, buf: &mut [u8]) -> usize {
        unsafe {
            let mut tmp_off = libc::lseek(self.fd, 0, libc::SEEK_CUR);
            libc::lseek(self.fd, self.offset as i64, libc::SEEK_SET);

            let n = libc::read(
                self.fd,
                buf.as_mut_ptr() as *mut libc::c_void,
                buf.len(),
            );

            libc::lseek(self.fd, tmp_off, libc::SEEK_SET);
            n as usize
        }
    }





pub fn seek(fd: libc::c_int, offset: libc::off_t) -> i64
{
    let result = unsafe { libc::lseek(fd, offset, libc::SEEK_SET) };

    if result < 0 { unsafe { libc::abort(); } }

    tell(fd)
}

pub fn peek(fd: libc::c_int, offset: libc::off_t, length: usize) -> Box<[u8]>
{
    let mut buffer = vec![0u8; length].into_boxed_slice();

    let bytes_read = unsafe {
        libc::pread(
            fd,
            buffer.as_mut_ptr() as *mut libc::c_void,
            length,
            offset,
        )
    };
    if bytes_read < 0 { unsafe { libc::abort(); } }

    let bytes_read = bytes_read as usize;
    buffer.truncate(bytes_read);
    buffer
}

pub fn read(fd: libc::c_int, length: usize) -> Box<[u8]> {

    let mut buffer: Vec<u8> = vec![0u8; length];

    let bytes_read = unsafe {
        libc::read(
            fd,
            buffer.as_mut_ptr() as *mut libc::c_void,
            length,
        )
    };

    if bytes_read < 0 {
        unsafe { libc::abort(); }
    }

    let bytes_read = bytes_read as usize;

    // SAFELY set length after read (valid because we fully initialized buffer)
    unsafe {
        buffer.set_len(bytes_read);
    }

    buffer.into_boxed_slice()
}


































}












pub trait Reader {
    fn tell(&self) -> u64;

    fn seek(&mut self, offset: u64);

    fn skip(&mut self, length: u64);

    fn peek(&mut self, offset: u64, length: usize) -> Box<[u8]>;

    fn read(&mut self, length: usize) -> Box<[u8]>;
}


pub struct Data;


pub struct Cursor {
    pub _data: &Data,
    pub _offset: u64,
    
}

pub struct Range {
    pub _start: Cursor,
    pub _cursor: Cursor,
}


impl FileData 




pub trait Data {
    fn open(path: &str, flags: libc::c_int) -> Self where Self: Sized;

    fn peek(&mut self, offset: u64, length: usize) -> Box<[u8]>;

    fn seek(&mut self, offset: u64);

    fn read(&mut self, length: usize) -> Box<[u8]>;

    fn tell(&self) -> u64;
}


pub struct Cursor {
    pub fd: libc::c_int,
    
}


pub struct FileData {
    pub _data: Cursor,
    pub _offset: u64,
}


impl FileData {
    pub fn open(path: &str) -> Self {

        let c_path = CString::new(path).unwrap();

        let fd = unsafe { libc::open(c_path.as_ptr(), libc::O_RDONLY) };

        if fd < 0 { unsafe { libc::abort(); } }

        Self {
            cursor: Cursor {
                fd,
                current_offset: 0,
            }
            offset
        }
    }
}




pub fn open(path: &str, flags: libc::c_int) -> Cursor {

    let c_path = CString::new(path).unwrap();

    let fd = unsafe {
        libc::open(c_path.as_ptr(), flags)
    };

    if fd < 0 {
        unsafe { libc::abort(); }
    }

    Cursor {
        fd,
        current_offset: 0,
    }
}



pub fn tell(fd: libc::c_int) -> i64
{
    let result = unsafe { libc::lseek(fd, 0, libc::SEEK_CUR) };

    if result < 0 { unsafe { libc::abort(); } }

    result as i64
}


use core::result::Result;

pub fn seek(fd: libc::c_int, offset: libc::off_t) -> i64
{
    let result = unsafe { libc::lseek(fd, offset, libc::SEEK_SET) };

    if result < 0 { unsafe { libc::abort(); } }

    tell(fd)
}

pub fn peek(fd: libc::c_int, offset: libc::off_t, length: usize) -> Box<[u8]>
{
    let mut buffer = vec![0u8; length].into_boxed_slice();

    let bytes_read = unsafe {
        libc::pread(
            fd,
            buffer.as_mut_ptr() as *mut libc::c_void,
            length,
            offset,
        )
    };
    if bytes_read < 0 { unsafe { libc::abort(); } }

    let bytes_read = bytes_read as usize;
    buffer.truncate(bytes_read);
    buffer
}

pub fn read(fd: libc::c_int, length: usize) -> Box<[u8]> {

    let mut buffer: Vec<u8> = vec![0u8; length];

    let bytes_read = unsafe {
        libc::read(
            fd,
            buffer.as_mut_ptr() as *mut libc::c_void,
            length,
        )
    };

    if bytes_read < 0 {
        unsafe { libc::abort(); }
    }

    let bytes_read = bytes_read as usize;

    // SAFELY set length after read (valid because we fully initialized buffer)
    unsafe {
        buffer.set_len(bytes_read);
    }

    buffer.into_boxed_slice()
}





pub struct OpenFlags(pub i32);

impl OpenFlags {
    pub const READ_ONLY:  OpenFlags = OpenFlags(libc::O_RDONLY);
    pub const WRITE_ONLY: OpenFlags = OpenFlags(libc::O_WRONLY);
    pub const READ_WRITE: OpenFlags = OpenFlags(libc::O_RDWR);
    pub const CREATE:     OpenFlags = OpenFlags(libc::O_CREAT);
    pub const TRUNCATE:   OpenFlags = OpenFlags(libc::O_TRUNC);
}

pub enum SeekFrom {
    Start(u64),
    Current(i64),
    End(i64),
}

pub struct File {
    fd: i32,
}

impl File {
    pub const INVALID: i32 = -1;

    pub fn open(path: &[u8], flags: OpenFlags) -> Option<File> {
        if path.is_empty() || path[path.len() - 1] != 0 {
            return None;
        }
        let fd = unsafe {
            libc::open(path.as_ptr() as *const libc::c_char, flags.0)
        };
        if fd < 0 { None } else { Some(File { fd }) }
    }

    pub fn read(&self, buf: &mut [u8]) -> Option<usize> {
        if buf.is_empty() { return Some(0); }
        let n = unsafe {
            libc::read(
                self.fd,
                buf.as_mut_ptr() as *mut libc::c_void,
                buf.len(),
            )
        };
        if n < 0 { None } else { Some(n as usize) }
    }

    pub fn write(&self, buf: &[u8]) -> Option<usize> {
        if buf.is_empty() { return Some(0); }
        let n = unsafe {
            libc::write(
                self.fd,
                buf.as_ptr() as *const libc::c_void,
                buf.len(),
            )
        };
        if n < 0 { None } else { Some(n as usize) }
    }

    pub fn seek(&self, pos: SeekFrom) -> Option<u64> {
        let (offset, whence) = match pos {
            SeekFrom::Start(n)   => (n as i64,  libc::SEEK_SET),
            SeekFrom::Current(n) => (n,          libc::SEEK_CUR),
            SeekFrom::End(n)     => (n,          libc::SEEK_END),
        };
        let result = unsafe {
            libc::lseek(self.fd, offset as libc::off_t, whence)
        };
        if result < 0 { None } else { Some(result as u64) }
    }

    pub fn offset(&self) -> Option<u64> {
        self.seek(SeekFrom::Current(0))
    }

    pub fn size(&self) -> Option<u64> {
        let current = self.offset()?;
        let end     = self.seek(SeekFrom::End(0))?;
        self.seek(SeekFrom::Start(current))?;
        Some(end)
    }

    pub fn as_fd(&self) -> i32 {
        self.fd
    }
}

impl Drop for File {
    fn drop(&mut self) {
        if self.fd >= 0 {
            unsafe { libc::close(self.fd); }
            self.fd = Self::INVALID;
        }
    }
}

pub struct Console;

impl Console {

    pub fn write(msg: &[u8]) {
        unsafe { libc::write(1, msg.as_ptr() as *const libc::c_void, msg.len()); }
    }

    pub fn error(msg: &[u8]) {
        unsafe { libc::write(2, msg.as_ptr() as *const libc::c_void, msg.len()); }
    }

    pub fn write_usize(mut n: usize) {
        let mut buf = [0u8; 20];
        if n == 0 {
            Self::write(b"0");
            return;
        }
        let mut i = 20;
        while n > 0 {
            i -= 1;
            buf[i] = b'0' + (n % 10) as u8;
            n /= 10;
        }
        Self::write(&buf[i..]);
    }

    pub fn write_i64(n: i64) {
        if n < 0 {
            Self::write(b"-");
            Self::write_usize((-n) as usize);
        } else {
            Self::write_usize(n as usize);
        }
    }

    pub fn write_u64(n: u64) {
        Self::write_usize(n as usize);
    }

    pub fn write_all(parts: &[&[u8]]) {
        let mut i = 0;
        while i < parts.len() {
            Self::write(parts[i]);
            i += 1;
        }
    }

    pub fn newline() {
        Self::write(b"\n");
    }


    // stringify a single value into a caller-supplied buffer
    // returns the number of bytes written

    fn nul_term(fmt: &[u8]) -> [u8; 32] {
        let mut tmp = [0u8; 32];
        let n = fmt.len().min(31);
        tmp[..n].copy_from_slice(&fmt[..n]);
        tmp
    }

    pub fn str_i(buf: &mut [u8], fmt: &[u8], val: i64) -> usize {
        let fmt = Self::nul_term(fmt);
        let n = unsafe {
            libc::snprintf(
                buf.as_mut_ptr() as *mut libc::c_char,
                buf.len(),
                fmt.as_ptr() as *const libc::c_char,
                val,
            )
        };
        if n > 0 { (n as usize).min(buf.len()) } else { 0 }
    }

    pub fn str_u(buf: &mut [u8], fmt: &[u8], val: u64) -> usize {
        let fmt = Self::nul_term(fmt);
        let n = unsafe {
            libc::snprintf(
                buf.as_mut_ptr() as *mut libc::c_char,
                buf.len(),
                fmt.as_ptr() as *const libc::c_char,
                val,
            )
        };
        if n > 0 { (n as usize).min(buf.len()) } else { 0 }
    }

    pub fn str_f(buf: &mut [u8], fmt: &[u8], val: f64) -> usize {
        let fmt = Self::nul_term(fmt);
        let n = unsafe {
            libc::snprintf(
                buf.as_mut_ptr() as *mut libc::c_char,
                buf.len(),
                fmt.as_ptr() as *const libc::c_char,
                val,
            )
        };
        if n > 0 { (n as usize).min(buf.len()) } else { 0 }
    }
}

pub struct Process;

impl Process {
    pub fn exit(code: i32) -> ! {
        unsafe { libc::exit(code); }
    }

    pub fn abort() -> ! {
        unsafe { libc::abort(); }
    }
}