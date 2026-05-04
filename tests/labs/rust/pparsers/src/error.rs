use libc::c_int;

// ------------------------------------------------------------------
// Error codes
// ------------------------------------------------------------------
pub const ERR_NONE:           c_int = 0;
pub const ERR_INVALID_ARG:    c_int = 1;
pub const ERR_IO:             c_int = 2;
pub const ERR_ARENA_OVERFLOW: c_int = 3;
pub const ERR_PARSE:          c_int = 4;
pub const ERR_OUT_OF_MEMORY:  c_int = 5;

pub const MSG_LEN: usize = 256;

// ------------------------------------------------------------------
// Error block — stored both globally and per-tree
// ------------------------------------------------------------------
pub struct ErrorBlock {
    pub code: c_int,
    pub msg:  [u8; MSG_LEN],
    pub msg_len: usize,
}

impl ErrorBlock {
    pub const fn new() -> ErrorBlock {
        ErrorBlock {
            code:    ERR_NONE,
            msg:     [0u8; MSG_LEN],
            msg_len: 0,
        }
    }

    pub fn set(&mut self, code: c_int, msg: &[u8]) {
        self.code = code;
        let len = msg.len().min(MSG_LEN - 1);
        self.msg[..len].copy_from_slice(&msg[..len]);
        self.msg[len] = 0;
        self.msg_len = len;
    }

    pub fn clear(&mut self) {
        self.code    = ERR_NONE;
        self.msg[0]  = 0;
        self.msg_len = 0;
    }

    pub fn is_set(&self) -> bool {
        self.code != ERR_NONE
    }
}

// ------------------------------------------------------------------
// Global fallback error block
// Only written when no per-tree block is available (e.g. tree_new
// itself fails).
// ------------------------------------------------------------------
static mut GLOBAL_ERROR: ErrorBlock = ErrorBlock::new();

pub fn global_set(code: c_int, msg: &[u8]) {
    unsafe { GLOBAL_ERROR.set(code, msg); }
}

pub fn global_clear() {
    unsafe { GLOBAL_ERROR.clear(); }
}

pub fn global_code() -> c_int {
    unsafe { GLOBAL_ERROR.code }
}

pub fn global_msg_ptr() -> *const u8 {
    unsafe { GLOBAL_ERROR.msg.as_ptr() }
}