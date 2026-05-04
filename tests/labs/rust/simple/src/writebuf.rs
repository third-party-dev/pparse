use crate::io::Console;

pub struct WriteBuf {
    buf: [u8; 256],
    len: usize,
}

impl WriteBuf {
    pub const fn new() -> WriteBuf {
        WriteBuf { buf: [0u8; 256], len: 0 }
    }

    // pub fn bytes(&mut self, bytes: &[u8]) -> &mut Self {
    //     let mut src = bytes;
    //     while !src.is_empty() {
    //         let space = self.buf.len() - self.len;
    //         if space == 0 { self.flush(); }
    //         let n = src.len().min(self.buf.len() - self.len);
    //         self.buf[self.len..self.len + n].copy_from_slice(&src[..n]);
    //         self.len += n;
    //         src = &src[n..];
    //     }
    //     self
    // }


    pub fn bytes(&mut self, bytes: &[u8]) -> &mut Self {
        let space = self.buf.len() - self.len;
        let n     = bytes.len().min(space);
        self.buf[self.len..self.len + n].copy_from_slice(&bytes[..n]);
        self.len += n;
        self
    }

    pub fn out(&mut self, value: &str) -> &mut Self {
        self.bytes(value.as_bytes())
    }

    pub fn int(&mut self, fmt: &str, val: i64) -> &mut Self {
        let mut tmp = [0u8; 64];
        let n = Console::str_i(&mut tmp, fmt.as_bytes(), val);
        self.bytes(&tmp[..n])
    }

    pub fn uint(&mut self, fmt: &str, val: u64) -> &mut Self {
        let mut tmp = [0u8; 64];
        let n = Console::str_u(&mut tmp, fmt.as_bytes(), val);
        self.bytes(&tmp[..n])
    }

    pub fn float(&mut self, fmt: &str, val: f64) -> &mut Self {
        let mut tmp = [0u8; 64];
        let n = Console::str_f(&mut tmp, fmt.as_bytes(), val);
        self.bytes(&tmp[..n])
    }


    // TODO: Rethink this one.
    pub fn hex(&mut self, mut n: u64) -> &mut Self {
        let mut tmp = [0u8; 16];
        if n == 0 {
            return self.bytes(b"0");
        }
        let mut i = 16;
        while n > 0 {
            i -= 1;
            let nibble = (n & 0xf) as u8;
            tmp[i] = if nibble < 10 { b'0' + nibble } else { b'a' + nibble - 10 };
            n >>= 4;
        }
        self.bytes(&tmp[i..])
    }


    pub fn flush(&mut self) {
        unsafe { libc::write(1, self.buf.as_ptr() as *const libc::c_void, self.len); }
        self.len = 0;
    }

    pub fn flush_err(&mut self) {
        unsafe { libc::write(2, self.buf.as_ptr() as *const libc::c_void, self.len); }
        self.len = 0;
    }
}

/*
let mut msg = WriteBuf::new();
let name = "Vinnie";

msg.out("Hello ").out(name).out(".");

msg.bytes(b"Hello ").bytes(name).bytes(b".");

msg.bytes(b"Hello ").bytes(name).bytes(b".");

*/

/*
let mut w = WriteBuf::new();
w.bytes(b"parsed ")
 .uint(node_count)
 .bytes(b" nodes at offset 0x")
 .hex(offset)
 .bytes(b"\n")
 .flush();
*/