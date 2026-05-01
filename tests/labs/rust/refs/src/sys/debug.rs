
/*

Tip: Use rust-lldb, not lldb
breakpoint() => breakpoint!()
locals() => frame variable

*/


#[macro_export]
macro_rules! breakpoint {
    () => {
        #[cfg(debug_assertions)]
        unsafe {
            // x86 / x86_64
            #[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
            core::arch::asm!("int3", options(nomem, nostack, preserves_flags));

            // ARM64
            #[cfg(target_arch = "aarch64")]
            core::arch::asm!("brk #0", options(nomem, nostack, preserves_flags));

            // ARM32
            #[cfg(target_arch = "arm")]
            core::arch::asm!("bkpt #0", options(nomem, nostack, preserves_flags));

            // MIPS
            #[cfg(any(target_arch = "mips", target_arch = "mips64"))]
            core::arch::asm!("break", options(nomem, nostack, preserves_flags));

            // AVR
            #[cfg(target_arch = "avr")]
            core::arch::asm!("break", options(nomem, nostack, preserves_flags));

            // RISC-V
            #[cfg(any(target_arch = "riscv32", target_arch = "riscv64"))]
            core::arch::asm!("ebreak", options(nomem, nostack, preserves_flags));

            // WASM
            #[cfg(any(target_arch = "wasm32", target_arch = "wasm64"))]
            core::arch::asm!("unreachable", options(nomem, nostack, preserves_flags));

            // PowerPC
            #[cfg(any(target_arch = "powerpc", target_arch = "powerpc64"))]
            core::arch::asm!("tw 31,0,0", options(nomem, nostack));

            // Sparc
            #[cfg(any(target_arch = "sparc", target_arch = "sparc64"))]
            core::arch::asm!("ta 1", options(nomem, nostack));

            // S390X
            #[cfg(target_arch = "s390x")]
            core::arch::asm!("trap2");

            // LoongArch64
            #[cfg(target_arch = "loongarch64")]
            core::arch::asm!("break 0", options(nomem, nostack, preserves_flags));

            #[cfg(target_arch="hexagon")]
            core::arch::asm!("trap0(#0)", options(nomem, nostack));

            #[cfg(target_arch="m68k")]
            core::arch::asm!("trap #15", options(nomem, nostack));

            #[cfg(target_arch="csky")]
            core::arch::asm!("bkpt", options(nomem, nostack, preserves_flags));

            #[cfg(target_arch="xtensa")]
            core::arch::asm!("break 0,0", options(nomem, nostack, preserves_flags));

            // Catch-all
            #[cfg(not(any(
                target_arch = "x86",
                target_arch = "x86_64",  // Only one I've tested.
                target_arch = "aarch64",
                target_arch = "arm",
                target_arch = "mips",
                target_arch = "mips64",
                target_arch = "avr",
                target_arch = "riscv32",
                target_arch = "riscv64",
                target_arch = "wasm32",
                target_arch = "wasm64",
                target_arch = "powerpc",
                target_arch = "powerpc64",
                target_arch = "sparc",
                target_arch = "sparc64",
                target_arch = "s390x",
                target_arch = "loongarch64",
                target_arch = "hexagon",
                target_arch = "m68k",
                target_arch = "csky",
                target_arch = "xtensa",
            )))]
            {
                // Note: bpf and nvptx64 have no breakpoint.
                ::libc::raise(::libc::SIGTRAP);
                //compile_error!("No breakpoint instruction defined for this architecture");
            }
        }
    }
}







