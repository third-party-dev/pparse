use core::panic::PanicInfo;

#[panic_handler]
fn panic(_: &PanicInfo) -> ! {
     unsafe {
        libc::write(2, b"panic\n".as_ptr() as *const libc::c_void, 6);
        libc::exit(1);
    }
}

#[no_mangle]
pub extern "C" fn rust_eh_personality() {
    // Called by debug libcore during exception handling.
}