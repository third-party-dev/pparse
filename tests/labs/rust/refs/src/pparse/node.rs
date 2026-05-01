use core::cell::{
    //Ref,
    RefCell,
    //RefMut,
};
use alloc::rc::{
    Rc,
    Weak,
};

use alloc::vec::Vec;

use alloc::collections::BTreeMap;

//use alloc::string::String;

use slotmap::{
    SlotMap,
    new_key_type
};

use core::fmt::{
    Display,
    Formatter,
    Result
};

use alloc::boxed::Box;

use core::any::{
    Any,
    TypeId
};


new_key_type! {
    // Effectively: pub struct NodeId(slotmap::KeyData); with the macro.
    pub struct NodeId;
}


pub struct Parser {
    arena: Option<NodeArena>,
}


impl Parser {
    fn new() -> Rc<RefCell<Parser>> {
        // Note: Acceptable to have Parser with arena = None, but
        //       never accept Arena without parser. Therefore we create
        //       the parser first and then use its ref to create arena.
        let parser_ref = Rc::new(RefCell::new(Parser { arena: None }));
        let parser_weak = Rc::downgrade(&parser_ref);
        parser_ref.borrow_mut().arena = Some(NodeArena::new(parser_weak));
        parser_ref
    }

    fn new_node(parser_weak: &ParserWeak, parent_id: NodeId) -> NodeId {
        let parser_rc = parser_weak.upgrade();
        let parser = parser_rc.unwrap();
        let mut parser = parser.borrow_mut();
        parser.arena.as_mut().unwrap().nodes.insert_with_key(|node_id| Node {
            ctx: Some(NodeContext::new(node_id, parent_id, parser_weak.clone())),
            value: NodeValue::None,
        })
    }
}


pub type ParserWeak = Weak<RefCell<Parser>>;


pub struct NodeContext {
    this_id: NodeId,
    // If this_id == parent_id, we're root.
    parent_id: NodeId,
    parser: ParserWeak,
    attr: BTreeMap<TypeId, Box<dyn Any>>,

    //state
    //reader
    start: usize,
    end: usize,
    descendants: Vec<NodeId>,
}


impl NodeContext {
    fn new(this_id: NodeId, parent_id: NodeId, parser: ParserWeak) -> Self {
        NodeContext {
            this_id: this_id,
            parent_id: parent_id,
            parser: parser,
            attr: BTreeMap::new(),

            start: 0,
            end: 0,
            descendants: Vec::new(),
        }
    }

    pub fn insert_attr<T: Any>(&mut self, val: T) {
        self.attr.insert(TypeId::of::<T>(), Box::new(val));
    }

    pub fn get_attr<T: Any>(&self) -> Option<&T> {
        self.attr.get(&TypeId::of::<T>())
            .and_then(|v| v.downcast_ref())
    }

    pub fn get_attr_mut<T: Any>(&mut self) -> Option<&mut T> {
        self.attr.get_mut(&TypeId::of::<T>())
            .and_then(|v| v.downcast_mut())
    }
}

pub enum NodeValue {
    None,
    Integer(i64),
    Unsigned(u64),
    Float(f64),
    Str(Box<str>),
    Bytes(Box<[u8]>),
    Node(NodeId),
    List(Vec<NodeValue>),
    Map(BTreeMap<Box<str>, NodeValue>),
}


pub struct Node {
    ctx: Option<NodeContext>,
    pub value: NodeValue,
}


pub struct NodeArena {
    parser: ParserWeak,
    pub nodes: SlotMap<NodeId, Node>,
    pub root_id: NodeId,
}


impl NodeArena {
    // Creates new node arena with a root node.
    pub fn new(parser: ParserWeak) -> Self {
        let mut nodes: SlotMap<NodeId, Node> = SlotMap::with_key();

        let root_id = nodes.insert_with_key(|node_id| Node {
            ctx: Some(NodeContext::new(node_id, node_id, parser.clone())),
            value: NodeValue::None,
        });

        NodeArena { parser: parser, nodes: nodes, root_id: root_id }
    }

    // Fetch read-only root node.
    pub fn root(&self) -> &Node {
        &self.nodes[self.root_id]
    }

    // Fetch mutable root node.
    pub fn root_mut(&mut self) -> &mut Node {
        &mut self.nodes[self.root_id]
    }

    pub fn get(&self, id: NodeId) -> Option<&Node> {
        self.nodes.get(id)
    }

    pub fn get_mut(&mut self, id: NodeId) -> Option<&mut Node> {
        self.nodes.get_mut(id)
    }
}


impl Display for NodeValue {
    fn fmt(&self, f: &mut Formatter<'_>) -> Result {
        match self {
            NodeValue::None => write!(f, "None"),
            NodeValue::Integer(v) => write!(f, "{}", v),
            NodeValue::Unsigned(v) => write!(f, "{}", v),
            NodeValue::Float(v) => write!(f, "{}", v),
            NodeValue::Str(v) => write!(f, "{}", v),
            NodeValue::Bytes(v) => {
                for byte in v.iter() {
                    write!(f, "\\x{:02x}", byte)?;
                }
                Ok(())
            },
            NodeValue::Node(_v) => {
                // TODO: Implement for real.
                write!(f, "NodeRc")
            },
            NodeValue::List(v) => {
                // TODO: Implement for real.
                write!(f, "List<NodeValue> Len: {}", v.len())
            },
            NodeValue::Map(v) => {
                // TODO: Implement for real.
                write!(f, "BTreeMap<Box<str>, NodeValue> Len: {}", v.len())
            }
        }
    }
}