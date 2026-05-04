use crate::arena::{Arena, NULL_INDEX};
use crate::error::{ErrorBlock, ERR_INVALID_ARG, ERR_IO, ERR_PARSE};

// Read buffer — small stack buffer, never the whole file
const READ_BUF_SIZE: usize = 4096;

pub struct Parser {
    pub arena:   Arena,
    fd:          libc::c_int,   // raw file descriptor, -1 = none
    file_offset: u64,           // current logical position
    buf:         [u8; READ_BUF_SIZE],
    buf_start:   u64,           // file offset of buf[0]
    buf_len:     usize,         // valid bytes in buf
}

impl Parser {
    pub fn new() -> Parser {
        Parser {
            arena:       Arena::new(),
            fd:          -1,
            file_offset: 0,
            buf:         [0u8; READ_BUF_SIZE],
            buf_start:   0,
            buf_len:     0,
        }
    }

    // ------------------------------------------------------------------
    // File management
    // ------------------------------------------------------------------

    pub fn open_file(
        &mut self,
        path: *const libc::c_char,
        err:  &mut ErrorBlock,
    ) -> bool {
        self.close_file();
        if path.is_null() {
            err.set(ERR_INVALID_ARG, b"null path");
            return false;
        }
        let fd = unsafe {
            libc::open(path, libc::O_RDONLY)
        };
        if fd < 0 {
            err.set(ERR_IO, b"open() failed");
            return false;
        }
        self.fd          = fd;
        self.file_offset = 0;
        self.buf_start   = 0;
        self.buf_len     = 0;
        true
    }

    pub fn close_file(&mut self) {
        if self.fd >= 0 {
            unsafe { libc::close(self.fd); }
            self.fd = -1;
        }
    }

    // ------------------------------------------------------------------
    // Seek + buffered read — never loads the whole file
    // ------------------------------------------------------------------

    // Seek to an absolute file offset
    fn seek(&mut self, offset: u64, err: &mut ErrorBlock) -> bool {
        if self.fd < 0 {
            err.set(ERR_IO, b"no file open");
            return false;
        }
        let result = unsafe {
            libc::lseek(self.fd, offset as libc::off_t, libc::SEEK_SET)
        };
        if result < 0 {
            err.set(ERR_IO, b"lseek() failed");
            return false;
        }
        self.file_offset = offset;
        self.buf_start   = offset;
        self.buf_len     = 0;   // invalidate buffer
        true
    }

    // Fill buffer from current file_offset
    fn fill_buf(&mut self, err: &mut ErrorBlock) -> bool {
        if self.fd < 0 {
            err.set(ERR_IO, b"no file open");
            return false;
        }
        let n = unsafe {
            libc::read(
                self.fd,
                self.buf.as_mut_ptr() as *mut libc::c_void,
                READ_BUF_SIZE,
            )
        };
        if n < 0 {
            err.set(ERR_IO, b"read() failed");
            return false;
        }
        self.buf_start = self.file_offset;
        self.buf_len   = n as usize;
        true
    }

    // Read a single byte at an absolute file offset
    // Seeks only when the offset is outside the current buffer window
    fn read_byte(
        &mut self,
        offset: u64,
        out:    &mut u8,
        err:    &mut ErrorBlock,
    ) -> bool {
        // check if offset is inside current buffer
        let buf_end = self.buf_start + self.buf_len as u64;
        if offset < self.buf_start || offset >= buf_end {
            if !self.seek(offset, err) { return false; }
            if !self.fill_buf(err)     { return false; }
        }
        if self.buf_len == 0 {
            err.set(ERR_IO, b"unexpected end of file");
            return false;
        }
        *out = self.buf[(offset - self.buf_start) as usize];
        true
    }

    // ------------------------------------------------------------------
    // Parse entry point
    // ------------------------------------------------------------------

    pub fn parse(&mut self, err: &mut ErrorBlock) -> u32 {
        self.arena.reset();

        if self.fd < 0 {
            err.set(ERR_PARSE, b"no file open");
            return NULL_INDEX;
        }

        // seed: read from offset 0
        if !self.seek(0, err) { return NULL_INDEX; }
        if !self.fill_buf(err) { return NULL_INDEX; }

        let root = self.arena.add_node(0, 0, 0, err);
        if root == NULL_INDEX { return NULL_INDEX; }

        let mut offset: u64 = 0;

        loop {
            let mut byte: u8 = 0;
            if !self.read_byte(offset, &mut byte, err) {
                // end of file is not an error here
                err.clear();
                break;
            }

            // skip whitespace
            match byte {
                b' ' | b'\t' | b'\n' | b'\r' => {
                    offset += 1;
                    continue;
                }
                _ => {}
            }

            // classify token — replace with your real grammar
            let kind = match byte {
                b'0'..=b'9' => 1u8,
                b'a'..=b'z' |
                b'A'..=b'Z' => 2u8,
                _            => 3u8,
            };

            let token_start = offset;

            // consume until whitespace
            loop {
                offset += 1;
                let mut next: u8 = 0;
                if !self.read_byte(offset, &mut next, err) {
                    err.clear();
                    break;
                }
                match next {
                    b' ' | b'\t' | b'\n' | b'\r' => break,
                    _ => {}
                }
            }

            let child = self.arena.add_node(kind, token_start, offset, err);
            if child == NULL_INDEX { return NULL_INDEX; }

            if !self.arena.add_child(root, child, err) {
                return NULL_INDEX;
            }
        }

        root
    }
}

impl Drop for Parser {
    fn drop(&mut self) {
        self.close_file();
    }
}