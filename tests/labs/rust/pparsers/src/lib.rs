mod arena;
mod error;
mod parser;

use arena::NULL_INDEX;
use error::{
    ErrorBlock,
    ERR_INVALID_ARG,
    global_set, global_code, global_msg_ptr,
};
use parser::Parser;
use libc::{c_int, c_char, size_t};

// ------------------------------------------------------------------
// ParseTree — owns the parser + per-tree error block
// ------------------------------------------------------------------
pub struct ParseTree {
    parser: Parser,
    err:    ErrorBlock,
    root:   u32,
}

// ------------------------------------------------------------------
// Lifecycle
// ------------------------------------------------------------------

#[no_mangle]
pub extern "C" fn tree_new() -> *mut ParseTree {
    let ptr = unsafe {
        libc::malloc(std::mem::size_of::<ParseTree>()) as *mut ParseTree
    };
    if ptr.is_null() {
        global_set(error::ERR_OUT_OF_MEMORY, b"malloc failed for ParseTree");
        return std::ptr::null_mut();
    }
    unsafe {
        ptr.write(ParseTree {
            parser: Parser::new(),
            err:    ErrorBlock::new(),
            root:   NULL_INDEX,
        });
    }
    ptr
}

#[no_mangle]
pub extern "C" fn tree_free(tree: *mut ParseTree) {
    if !tree.is_null() {
        unsafe {
            std::ptr::drop_in_place(tree);
            libc::free(tree as *mut libc::c_void);
        }
    }
}

// ------------------------------------------------------------------
// Error access — per-tree
// ------------------------------------------------------------------

#[no_mangle]
pub extern "C" fn tree_error_code(tree: *const ParseTree) -> c_int {
    if tree.is_null() { return ERR_INVALID_ARG; }
    unsafe { (*tree).err.code }
}

#[no_mangle]
pub extern "C" fn tree_error_msg(tree: *const ParseTree) -> *const u8 {
    if tree.is_null() { return global_msg_ptr(); }
    unsafe { (*tree).err.msg.as_ptr() }
}

#[no_mangle]
pub extern "C" fn tree_error_clear(tree: *mut ParseTree) {
    if !tree.is_null() {
        unsafe { (*tree).err.clear(); }
    }
}

// ------------------------------------------------------------------
// Error access — global fallback
// ------------------------------------------------------------------

#[no_mangle]
pub extern "C" fn global_error_code() -> c_int {
    global_code()
}

#[no_mangle]
pub extern "C" fn global_error_msg() -> *const u8 {
    global_msg_ptr()
}

// ------------------------------------------------------------------
// Parse
// ------------------------------------------------------------------

#[no_mangle]
pub extern "C" fn tree_open_file(
    tree: *mut ParseTree,
    path: *const c_char,
) -> c_int {
    if tree.is_null() { return -1; }
    let t = unsafe { &mut *tree };
    t.err.clear();
    if t.parser.open_file(path, &mut t.err) { 0 } else { -1 }
}

#[no_mangle]
pub extern "C" fn tree_parse(tree: *mut ParseTree) -> c_int {
    if tree.is_null() { return -1; }
    let t = unsafe { &mut *tree };
    t.err.clear();
    t.root = t.parser.parse(&mut t.err);
    if t.root == NULL_INDEX { -1 } else { 0 }
}

#[no_mangle]
pub extern "C" fn tree_close_file(tree: *mut ParseTree) {
    if !tree.is_null() {
        unsafe { (*tree).parser.close_file(); }
    }
}

// ------------------------------------------------------------------
// Node access — all read-only, safe for Python
// ------------------------------------------------------------------

#[no_mangle]
pub extern "C" fn tree_node_count(tree: *const ParseTree) -> size_t {
    if tree.is_null() { return 0; }
    unsafe { (*tree).parser.arena.node_count }
}

#[no_mangle]
pub extern "C" fn tree_root(tree: *const ParseTree) -> u32 {
    if tree.is_null() { return NULL_INDEX; }
    unsafe { (*tree).root }
}

#[no_mangle]
pub extern "C" fn node_kind(
    tree:  *const ParseTree,
    index: u32,
) -> u8 {
    if tree.is_null() { return 0; }
    let t = unsafe { &*tree };
    if index as usize >= t.parser.arena.node_count { return 0; }
    t.parser.arena.node(index).kind
}

#[no_mangle]
pub extern "C" fn node_start(
    tree:  *const ParseTree,
    index: u32,
) -> u64 {
    if tree.is_null() { return 0; }
    let t = unsafe { &*tree };
    if index as usize >= t.parser.arena.node_count { return 0; }
    t.parser.arena.node(index).start
}

#[no_mangle]
pub extern "C" fn node_end(
    tree:  *const ParseTree,
    index: u32,
) -> u64 {
    if tree.is_null() { return 0; }
    let t = unsafe { &*tree };
    if index as usize >= t.parser.arena.node_count { return 0; }
    t.parser.arena.node(index).end
}

#[no_mangle]
pub extern "C" fn node_child_count(
    tree:  *const ParseTree,
    index: u32,
) -> u32 {
    if tree.is_null() { return 0; }
    let t = unsafe { &*tree };
    if index as usize >= t.parser.arena.node_count { return 0; }
    let node = t.parser.arena.node(index);
    if node.child_start == NULL_INDEX { return 0; }
    node.child_end - node.child_start
}

#[no_mangle]
pub extern "C" fn node_child(
    tree:        *const ParseTree,
    node_index:  u32,
    child_index: u32,
) -> u32 {
    if tree.is_null() { return NULL_INDEX; }
    let t = unsafe { &*tree };
    if node_index as usize >= t.parser.arena.node_count { return NULL_INDEX; }
    let node = t.parser.arena.node(node_index);
    if node.child_start == NULL_INDEX { return NULL_INDEX; }
    let abs = node.child_start + child_index;
    if abs >= node.child_end { return NULL_INDEX; }
    t.parser.arena.child_at(abs)
}