
pub const STDOUT: i32 = 1;
pub const SIGTRAP: i32 = libc::SIGTRAP;

pub fn exit(code: i32) -> ! {
    unsafe { libc::exit(code); }
}

pub fn write(fd: i32, buf: &[u8]) -> isize {
    unsafe { libc::write(fd, buf.as_ptr() as *const libc::c_void, buf.len()) }
}

pub fn abort() -> ! {
    unsafe { libc::abort(); }
}

pub fn raise(sig: i32) -> i32 {
    unsafe { libc::raise(sig) }
}