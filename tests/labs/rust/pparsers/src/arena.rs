use crate::error::{ErrorBlock, ERR_ARENA_OVERFLOW, ERR_OUT_OF_MEMORY};

pub const NULL_INDEX: u32 = u32::MAX;

// Chunk size — number of nodes per allocation
const CHUNK_NODES: usize = 65536;

// Hard ceiling — total nodes across all chunks
const MAX_TOTAL_NODES: usize = 1 << 28; // 268 million nodes

// Max chunks we can track — no Vec, fixed pointer table
const MAX_CHUNKS: usize = MAX_TOTAL_NODES / CHUNK_NODES;

// ------------------------------------------------------------------
// A single node
// ------------------------------------------------------------------
pub struct Node {
    pub kind:        u8,
    pub start:       u64,   // byte offset in file
    pub end:         u64,
    pub child_start: u32,   // index into Arena.children[]
    pub child_end:   u32,
}

// ------------------------------------------------------------------
// Flat child index storage — same chunk scheme as nodes
// ------------------------------------------------------------------
const CHUNK_CHILDREN: usize = 65536;
const MAX_CHILD_CHUNKS: usize = MAX_CHUNKS;

// ------------------------------------------------------------------
// Arena — growable via malloc'd chunks, no generics, no Vec
// ------------------------------------------------------------------
pub struct Arena {
    // node storage
    node_chunks:     [*mut Node; MAX_CHUNKS],
    node_chunk_count: usize,
    pub node_count:  usize,

    // child index storage
    child_chunks:      [*mut u32; MAX_CHILD_CHUNKS],
    child_chunk_count: usize,
    pub child_count:   usize,
}

impl Arena {
    pub fn new() -> Arena {
        Arena {
            node_chunks:       [std::ptr::null_mut(); MAX_CHUNKS],
            node_chunk_count:  0,
            node_count:        0,
            child_chunks:      [std::ptr::null_mut(); MAX_CHILD_CHUNKS],
            child_chunk_count: 0,
            child_count:       0,
        }
    }

    // Reset without freeing memory — reuse allocated chunks
    pub fn reset(&mut self) {
        self.node_count  = 0;
        self.child_count = 0;
    }

    // Free all chunks
    pub fn free_all(&mut self) {
        let mut i = 0;
        while i < self.node_chunk_count {
            unsafe { libc::free(self.node_chunks[i] as *mut libc::c_void); }
            self.node_chunks[i] = std::ptr::null_mut();
            i += 1;
        }
        self.node_chunk_count = 0;
        self.node_count       = 0;

        let mut i = 0;
        while i < self.child_chunk_count {
            unsafe { libc::free(self.child_chunks[i] as *mut libc::c_void); }
            self.child_chunks[i] = std::ptr::null_mut();
            i += 1;
        }
        self.child_chunk_count = 0;
        self.child_count       = 0;
    }

    // ------------------------------------------------------------------
    // Node allocation
    // ------------------------------------------------------------------
    pub fn add_node(
        &mut self,
        kind:  u8,
        start: u64,
        end:   u64,
        err:   &mut ErrorBlock,
    ) -> u32 {
        if self.node_count >= MAX_TOTAL_NODES {
            err.set(ERR_ARENA_OVERFLOW, b"node arena hard limit reached");
            return NULL_INDEX;
        }

        // grow if needed
        let chunk_idx  = self.node_count / CHUNK_NODES;
        let within     = self.node_count % CHUNK_NODES;

        if within == 0 {
            // need a new chunk
            if chunk_idx >= MAX_CHUNKS {
                err.set(ERR_ARENA_OVERFLOW, b"node chunk table full");
                return NULL_INDEX;
            }
            let ptr = unsafe {
                libc::malloc(
                    CHUNK_NODES * std::mem::size_of::<Node>()
                ) as *mut Node
            };
            if ptr.is_null() {
                err.set(ERR_OUT_OF_MEMORY, b"malloc failed for node chunk");
                return NULL_INDEX;
            }
            self.node_chunks[chunk_idx] = ptr;
            self.node_chunk_count += 1;
        }

        let idx  = self.node_count as u32;
        let node = self.node_mut(idx);
        node.kind        = kind;
        node.start       = start;
        node.end         = end;
        node.child_start = NULL_INDEX;
        node.child_end   = NULL_INDEX;

        self.node_count += 1;
        idx
    }

    // ------------------------------------------------------------------
    // Child index allocation
    // ------------------------------------------------------------------
    pub fn add_child(
        &mut self,
        parent: u32,
        child:  u32,
        err:    &mut ErrorBlock,
    ) -> bool {
        if self.child_count >= MAX_TOTAL_NODES {
            err.set(ERR_ARENA_OVERFLOW, b"child arena hard limit reached");
            return false;
        }

        let chunk_idx = self.child_count / CHUNK_CHILDREN;
        let within    = self.child_count % CHUNK_CHILDREN;

        if within == 0 {
            if chunk_idx >= MAX_CHILD_CHUNKS {
                err.set(ERR_ARENA_OVERFLOW, b"child chunk table full");
                return false;
            }
            let ptr = unsafe {
                libc::malloc(
                    CHUNK_CHILDREN * std::mem::size_of::<u32>()
                ) as *mut u32
            };
            if ptr.is_null() {
                err.set(ERR_OUT_OF_MEMORY, b"malloc failed for child chunk");
                return false;
            }
            self.child_chunks[chunk_idx] = ptr;
            self.child_chunk_count += 1;
        }

        // update parent's child range
        let p = self.node_mut(parent);
        if p.child_start == NULL_INDEX {
            p.child_start = self.child_count as u32;
            p.child_end   = self.child_count as u32;
        }
        p.child_end += 1;

        // write child index
        let slot = self.child_slot_mut(self.child_count);
        *slot = child;
        self.child_count += 1;
        true
    }

    // ------------------------------------------------------------------
    // Accessors
    // ------------------------------------------------------------------
    pub fn node(&self, idx: u32) -> &Node {
        let i = idx as usize;
        let chunk = self.node_chunks[i / CHUNK_NODES];
        unsafe { &*chunk.add(i % CHUNK_NODES) }
    }

    fn node_mut(&mut self, idx: u32) -> &mut Node {
        let i = idx as usize;
        let chunk = self.node_chunks[i / CHUNK_NODES];
        unsafe { &mut *chunk.add(i % CHUNK_NODES) }
    }

    pub fn child_at(&self, abs_index: u32) -> u32 {
        let i = abs_index as usize;
        let chunk = self.child_chunks[i / CHUNK_CHILDREN];
        unsafe { *chunk.add(i % CHUNK_CHILDREN) }
    }

    fn child_slot_mut(&mut self, abs_index: usize) -> &mut u32 {
        let chunk = self.child_chunks[abs_index / CHUNK_CHILDREN];
        unsafe { &mut *chunk.add(abs_index % CHUNK_CHILDREN) }
    }
}

impl Drop for Arena {
    fn drop(&mut self) {
        self.free_all();
    }
}