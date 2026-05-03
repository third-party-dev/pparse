
pub const STDOUT: i32 = 1;
pub const SIGTRAP: i32 = libc::SIGTRAP;

use alloc::vec::Vec;
use alloc::boxed::Box;
use alloc::ffi::CString;

pub fn exit(code: i32) -> ! {
  unsafe { libc::exit(code); }
}

pub fn abort() -> ! {
  unsafe { libc::abort(); }
}

pub fn raise(sig: i32) -> i32 {
  unsafe { libc::raise(sig) }
}

// _open(b"/etc/passwd\0", libc::O_RDONLY)
pub fn _open(path: &[u8], flags: i32) -> i32 {
  unsafe { libc::open(path.as_ptr() as *const libc::c_char, flags) }
}

// open(Box::from("/etc/passwd"), libc::O_RDONLY)
pub fn open(path: Box<str>, flags: i32) -> Result<i32, i32> {
  let path = CString::new(path.as_bytes()).map_err(|_| libc::EINVAL)?;
  let fd = unsafe { libc::open(path.as_ptr(), flags) };
  if fd < 0 {
    Err(unsafe { *libc::__errno_location() })
  } else {
    Ok(fd)
  }
}

// _stat(b"/etc/passwd\0")
// pub fn _stat(path: &[u8]) -> libc::stat {
//   let mut stat = core::mem::MaybeUninit::<libc::stat>::uninit();
//   unsafe { libc::stat(path.as_ptr(), stat.as_mut_ptr()) }
// }

pub fn stat(path: Box<str>) -> Result<libc::stat, i32> {
    let path = CString::new(path.as_bytes()).map_err(|_| libc::EINVAL)?;
    let mut stat = core::mem::MaybeUninit::<libc::stat>::uninit();
    let result = unsafe { libc::stat(path.as_ptr(), stat.as_mut_ptr()) };
    if result < 0 {
        Err(unsafe { *libc::__errno_location() })
    } else {
        Ok(unsafe { stat.assume_init() })
    }
}

pub fn _write(fd: i32, buf: &[u8]) -> isize {
  unsafe { libc::write(fd, buf.as_ptr() as *const libc::c_void, buf.len()) }
}

pub fn write(fd: i32, buf: &[u8]) -> Result<usize, i32> {
    let result = unsafe {
        libc::write(fd, buf.as_ptr() as *const libc::c_void, buf.len())
    };
    if result < 0 {
        Err(unsafe { *libc::__errno_location() })
    } else {
        Ok(result as usize)
    }
}

// let buf = [0u8; 10]; OR let buf: Vec<u8> = alloc::vec![0u8; 10];
// _read(fd, &mut buf[5..]);
pub fn _read(fd: i32, buf: &mut [u8], count: usize) -> i32 {
    unsafe { libc::read(fd, buf.as_mut_ptr() as *mut libc::c_void, buf.len()) as i32 }
}


pub fn read(fd: i32, len: usize) -> Result<Vec<u8>, i32> {
    let mut buf: Vec<u8> = Vec::with_capacity(len);
    let result = unsafe {
        libc::read(fd, buf.as_mut_ptr() as *mut libc::c_void, len)
    };
    if result < 0 {
        Err(unsafe { *libc::__errno_location() })
    } else {
        unsafe { buf.set_len(result as usize) };
        Ok(buf)
    }
}