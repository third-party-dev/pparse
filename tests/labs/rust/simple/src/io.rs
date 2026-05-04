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