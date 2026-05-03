use core::panic::PanicInfo;
use crate::println;
use crate::sys::cstdlib::abort;

// #[panic_handler]
// fn panic(_: &PanicInfo) -> ! {
//      unsafe {
//         libc::write(2, b"panic\n".as_ptr() as *const libc::c_void, 6);
//         libc::exit(1);
//     }
// }

#[panic_handler]
fn panic(info: &PanicInfo) -> ! {
    if let Some(location) = info.location() {
        println!("panic at {}:{}", location.file(), location.line());
    }
    unsafe { libc::exit(1); }
}

#[no_mangle]
pub extern "C" fn rust_eh_personality() {
    // Called by debug libcore during exception handling.
}

#[no_mangle]
pub unsafe extern "C" fn _Unwind_Resume() -> ! {
    //core::intrinsics::abort()
    abort()
}