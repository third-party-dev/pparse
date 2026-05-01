//#![no_std]
//extern crate alloc;

use alloc::vec::Vec;
use alloc::string::String;
use slotmap::{SlotMap, new_key_type};

new_key_type! {
    // Effectively: pub struct NodeId(slotmap::KeyData); with the macro.
    pub struct NodeId;
}

// pub struct NodeContext {
//     pub key: String,
//     pub value: Option<Value>,
// }

// pub enum Value {
//     Int(i64),
//     Bool(bool),
//     Str(String),
//     Node(NodeId),
// }

// pub struct Node {
//     pub context: NodeContext,
//     pub children: Vec<NodeId>,
//     pub parent: Option<NodeId>,
// }

pub struct Arena {
    pub nodes: SlotMap<NodeId, Node>,
}

impl Arena {
    pub fn new() -> Self {
        Arena {
            nodes: SlotMap::with_key(),
        }
    }

    pub fn insert(&mut self, node: Node) -> NodeId {
        self.nodes.insert(node)
    }

    pub fn get(&self, id: NodeId) -> Option<&Node> {
        self.nodes.get(id)
    }

    pub fn get_mut(&mut self, id: NodeId) -> Option<&mut Node> {
        self.nodes.get_mut(id)
    }
}

pub struct ParseTree {
    pub arena: Arena,
    pub root_id: NodeId,
}

impl ParseTree {
    pub fn new() -> Self {
        let mut arena = Arena::new();

        let root = Node {
            context: NodeContext { key: String::from("root"), value: None },
            children: Vec::new(),
            parent: None,
        };
        let root_id = arena.insert(root);

        ParseTree { arena, root_id }
    }

    pub fn add_child(&mut self, parent_id: NodeId, key: &str) -> NodeId {
        let child = Node {
            context: NodeContext {
                key: String::from(key),
                value: None,
            },
            children: Vec::new(),
            parent: Some(parent_id),
        };

        let child_id = self.arena.insert(child);

        // safe: these are two different slots
        if let Some(parent) = self.arena.get_mut(parent_id) {
            parent.children.push(child_id);
        }

        child_id
    }

    // Mutate an ancestor from a descendant's context -
    // the whole point of the arena: just index by id
    pub fn patch_ancestor(&mut self, ancestor_id: NodeId, value: Value) {
        if let Some(node) = self.arena.get_mut(ancestor_id) {
            node.context.value = Some(value);
        }
    }

    pub fn load(&mut self, id: NodeId) {
        // Collect child ids without holding a borrow
        let child_ids: Vec<NodeId> = self.arena
            .get(id)
            .map(|n| n.children.clone())
            .unwrap_or_default();

        for child_id in child_ids {
            self.load(child_id); // recurse

            // After child loads, freely mutate any ancestor by id
            // e.g. something discovered in child patches the root:
            self.patch_ancestor(self.root_id, Value::Bool(true));
        }
    }
}