use crate::sys::cstdlib::{write, STDOUT};

use core::fmt::{self, Write};

struct Stdout;

impl Write for Stdout {
    fn write_str(&mut self, s: &str) -> fmt::Result {
        write(STDOUT, s.as_bytes()).expect("write(STDOUT) failed.");
        Ok(())
    }
}

pub fn _print(args: fmt::Arguments) {
    use core::fmt::Write;
    Stdout.write_fmt(args).unwrap();
}

#[macro_export]
macro_rules! print {
    ($($arg:tt)*) => ({
        $crate::sys::print::_print(core::format_args!($($arg)*));
    });
}

#[macro_export]
macro_rules! println {
    () => ($crate::print!("\n"));

    ($fmt:expr) => (
        $crate::print!(concat!($fmt, "\n"))
    );

    ($fmt:expr, $($arg:tt)*) => (
        $crate::print!(
            concat!($fmt, "\n"),
            $($arg)*
        )
    );
}