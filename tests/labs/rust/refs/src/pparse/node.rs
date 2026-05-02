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

//use crate::println;
//use crate::breakpoint;


new_key_type! {
    // Effectively: pub struct NodeId(slotmap::KeyData); with the macro.
    pub struct NodeId;
}


impl Display for NodeId {
    fn fmt(&self, f: &mut Formatter<'_>) -> Result {
        write!(f, "NodeId({:?})", self.0)
    }
}

pub trait NodeState {
    fn parse_data(&mut self, node: &mut Node);
}

pub struct Parser {
    pub arena: Option<NodeArena>,
}


impl Parser {
    pub fn new() -> Rc<RefCell<Parser>> {
        // Note: Acceptable to have Parser with arena = None, but
        //       never accept Arena without parser. Therefore we create
        //       the parser first and then use its ref to create arena.
        let parser_ref = Rc::new(RefCell::new(Parser { arena: None }));
        let parser_weak = Rc::downgrade(&parser_ref);
        parser_ref.borrow_mut().arena = Some(NodeArena::new(parser_weak));
        parser_ref
    }

    pub fn new_node(parser_weak: &ParserWeak, parent_id: NodeId) -> NodeId {
        let parser_rc = parser_weak.upgrade();
        let parser = parser_rc.unwrap();

        //breakpoint!();

        let mut parser = parser.borrow_mut();
        
        parser.arena.as_mut().unwrap().nodes.insert_with_key(|node_id| Node {
            ctx: Some(NodeContext::new(node_id, parent_id, parser_weak.clone())),
            value: NodeValue::None,
        })
    }

    pub fn root_node(&self) -> &Node {
        let arena = self.arena.as_ref().unwrap();
        arena.root()
    }

    pub fn root_node_mut(&mut self) -> &mut Node {
        let arena = self.arena.as_mut().unwrap();
        arena.root_mut()
    }

    pub fn node(&self, id: NodeId) -> Option<&Node> {
        let arena = self.arena.as_ref().unwrap();
        arena.get(id)
    }

    pub fn node_mut(&mut self, id: NodeId) -> Option<&mut Node> {
        let arena = self.arena.as_mut().unwrap();
        arena.get_mut(id)
    }
}


pub type ParserWeak = Weak<RefCell<Parser>>;


// enum DefaultNodeState { None }
// impl NodeState for DefaultNodeState {
//     fn parse_data(&mut self, node: &mut Node) {
//         match self {
//             _ => ParseDataResult::Ascend
//         }
//     }
// }


pub struct NodeContext {
    this_id: NodeId,
    // If this_id == parent_id, we're root.
    parent_id: NodeId,
    _parser: ParserWeak,
    _attr: BTreeMap<TypeId, Box<dyn Any>>,
    _state: Option<Box<dyn NodeState>>,
    // TODO: TBD if we need this.
    _next_state: Option<Box<dyn NodeState>>,

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
            _parser: parser,

            _attr: BTreeMap::new(),
            _state: None,
            _next_state: None,
            start: 0,
            end: 0,
            descendants: Vec::new(),
        }
    }

    pub fn has_state(&self) -> bool {
        self._state.is_none()
    }
    pub fn state(&self) -> &Box<dyn NodeState> {
        self._state.as_ref().unwrap()
    }
    pub fn state_mut(&mut self) -> &mut Box<dyn NodeState> {
        self._state.as_mut().unwrap()
    }
    // Example: node.next_state(JsonNodeState::Object);
    fn next_state<S: NodeState + 'static>(&mut self, state: S) {
        self._next_state = Some(Box::new(state));
    }

    pub fn insert_attr<T: Any>(&mut self, val: T) {
        self._attr.insert(TypeId::of::<T>(), Box::new(val));
    }
    pub fn attr<T: Any>(&self) -> Option<&T> {
        self._attr.get(&TypeId::of::<T>()).and_then(|v| v.downcast_ref())
    }
    pub fn attr_mut<T: Any>(&mut self) -> Option<&mut T> {
        self._attr.get_mut(&TypeId::of::<T>()).and_then(|v| v.downcast_mut())
    }

    pub fn parser(&self) -> ParserWeak {
        self._parser.clone()
    }

    /*
    fn step(&mut self) {
        // run current state
        self.state.parse_data(self);

        // apply transition if requested
        if let Some(next) = self.next_state.take() {
            self.state = next;
        }
    }
    */

}

#[macro_export]
macro_rules! new_state_generator {
    ($macro_name:ident, $enum_name:ident, $prefix:ident) => {
        macro_rules! $macro_name {
            ($enum_name::$variant:ident) => {
                paste::paste! {
                    $enum_name::$variant([<$prefix $variant>]::new())
                }
            };
        }
    };
}

enum ParseDataResult {
    Again,
    Ascend,
}

pub enum NodeValue {
    None,
    Integer(i64),
    Unsigned(u64),
    Float(f64),
    Str(Box<str>),
    Bytes(Box<[u8]>),
    NodeId(NodeId),
    List(Vec<NodeValue>),
    Map(BTreeMap<Box<str>, NodeValue>),
}


pub struct Node {
    pub ctx: Option<NodeContext>,
    pub value: NodeValue,
}


impl Node {
    pub fn id(&self) -> NodeId {
        self.ctx.as_ref().unwrap().this_id
    }

    pub fn set_value(&mut self, value: NodeValue) {
        self.value = value;
    }

    pub fn set_none(&mut self) {
        self.set_value(NodeValue::None);
    }
    // copy as bytes
    pub fn set_bytes(&mut self, val: &[u8]) {
        self.set_value(NodeValue::Bytes(Box::from(val)));
    }
    // implicit copy as bytes
    pub fn set_boxstr(&mut self, val: Box<str>) {
        self.set_value(NodeValue::Str(val));
    }
    // scalar
    pub fn set_uint(&mut self, val: u64) {
        self.set_value(NodeValue::Unsigned(val));
    }
    // scalar
    pub fn set_int(&mut self, val: i64) {
        self.set_value(NodeValue::Integer(val));
    }
    // scalar
    pub fn set_float(&mut self, val: f64) {
        self.set_value(NodeValue::Float(val));
    }

    pub fn is_nodeid(&self) -> bool {
        matches!(self.value, NodeValue::NodeId(_))
    }
    pub fn as_nodeid(&self) -> Option<NodeId> {
        if let NodeValue::NodeId(id) = &self.value { Some(*id) } else { None }
    }
    pub fn as_nodeid_mut(&mut self) -> Option<NodeId> {
        if let NodeValue::NodeId(id) = &self.value { Some(*id) } else { None }
    }
    pub fn set_nodeid(&mut self, val: NodeId) {
        self.set_value(NodeValue::NodeId(val))
    }


    pub fn is_list(&self) -> bool {
        matches!(self.value, NodeValue::List(_))
    }
    pub fn as_list(&self) -> Option<&Vec<NodeValue>> {
        if let NodeValue::List(v) = &self.value { Some(v) } else { None }
    }
    pub fn as_list_mut(&mut self) -> Option<&mut Vec<NodeValue>> {
        if let NodeValue::List(v) = &mut self.value { Some(v) } else { None }
    }
    pub fn set_list(&mut self, val: Vec<NodeValue>) {
        self.set_value(NodeValue::List(val))
    }


    pub fn is_map(&self) -> bool {
        matches!(self.value, NodeValue::Map(_))
    }
    pub fn as_map(&self) -> Option<&BTreeMap<Box<str>, NodeValue>> {
        if let NodeValue::Map(v) = &self.value { Some(v) } else { None }
    }
    pub fn as_map_mut(&mut self) -> Option<&mut BTreeMap<Box<str>, NodeValue>> {
        if let NodeValue::Map(v) = &mut self.value { Some(v) } else { None }
    }
    pub fn set_map(&mut self, val: BTreeMap<Box<str>, NodeValue>) {
        self.set_value(NodeValue::Map(val))
    }
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


// TODO: When we remove edges in the graph, it leaves orphaned nodes.
// TODO: An example garbage collector to clean up arena:

// use alloc::collections::{BTreeSet, VecDeque};

// fn garbage_collect(arena: &mut SlotMap<NodeId, Node>, roots: &[NodeId]) {
//     let mut reachable: BTreeSet<NodeId> = BTreeSet::new();
//     let mut queue: VecDeque<NodeId> = VecDeque::from(roots.to_vec());

//     while let Some(id) = queue.pop_front() {
//         if reachable.insert(id) {  // returns false if already present
//             if let Some(node) = arena.get(id) {
//                 for &child in &node.children {
//                     queue.push_back(child);
//                 }
//             }
//         }
//     }

//     arena.retain(|key, _| reachable.contains(&key));
// }


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
            NodeValue::NodeId(_v) => {
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



