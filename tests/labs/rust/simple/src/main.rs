#![no_std]
#![no_main]
#![allow(dead_code)]

//extern crate alloc;
//extern crate libc;

mod alloc;
mod io;
mod panic;
mod writebuf;

use writebuf::WriteBuf;

use io::{File, OpenFlags, Console, Process}; //SeekFrom

#[no_mangle]
pub extern "C" fn main(_argc: i32, _argv: *const *const u8) -> i32 {
    // Console::write(b"starting\n");

    // let file = match File::open(b"/etc/hostname\0", OpenFlags::READ_ONLY) {
    //     Some(f) => f,
    //     None    => {
    //         Console::error(b"failed to open file\n");
    //         Process::exit(1);
    //     }
    // };

    // let mut buf = [0u8; 256];
    // match file.read(&mut buf) {
    //     Some(n) => {
    //         Console::write(b"read ");
    //         Console::write_usize(n);
    //         Console::write(b" bytes: ");
    //         Console::write(&buf[..n]);
    //     }
    //     None => {
    //         Console::error(b"read failed\n");
    //         Process::exit(1);
    //     }
    // }

    // if let Some(size) = file.size() {
    //     Console::write(b"file size: ");
    //     Console::write_u64(size);
    //     Console::newline();
    // }

    // Console::write_all(&[b"result: ", b"ok", b"\n"]);

    let mut w = WriteBuf::new();
    w.bytes(b"parsed ").uint("%x", 0xdead).bytes(b" nodes at offset 0x").uint("%i", 7564).bytes(b"\n").flush();

    let mut msg = WriteBuf::new();
    let name = "Vinnie";
    msg.out("Hello ").out(name).out(".\n").flush();

    Process::exit(0);
}