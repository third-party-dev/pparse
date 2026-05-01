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


pub struct NodeContext {
    this_id: NodeId,
    // If this_id == parent_id, we're root.
    parent_id: NodeId,
    _parser: ParserWeak,
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
            _parser: parser,
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

    pub fn parser(&self) -> ParserWeak {
        self._parser.clone()
    }
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











/*
// Short-Lived Helper Struct
pub struct NodeUtl<'a> {
    node: &'a NodeRc,
}
// Short-Lived Helper Impl
impl<'a> NodeUtl<'a> {

    pub fn wrap(node: &'a NodeRc) -> Self {
        NodeUtl { node }
    }

    pub fn new_child(&self) -> NodeRc {
        Node::new(&self.node)
    }

    pub fn ctx(&self) -> Option<RefMut<'_, NodeContext>> {
        let node = self.node.borrow_mut();
        if node.ctx.is_none() {
            return None;
        }
        Some(RefMut::map(node, |n| n.ctx.as_mut().unwrap()))
    }

    //     pub fn clear_ctx(&mut self) {
    //         self.ctx = None;
    //     }

    pub fn value(&self) -> Ref<'_, NodeValue> {
        Ref::map(self.node.borrow(), |n| &n.value)
    }
    pub fn set_value(&mut self, val: NodeValue) {
        self.node.borrow_mut().value = val;
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


    pub fn is_node(&self) -> bool {
        matches!(self.node.borrow().value, NodeValue::Node(_))
    }
    pub fn as_node(&self) -> Option<Ref<'_, NodeRc>> {
        Ref::filter_map(self.node.borrow(), |n| {
            if let NodeValue::Node(rc) = &n.value { Some(rc) } else { None }
        }).ok()
    }
    pub fn as_mut_node(&self) -> Option<RefMut<'_, NodeRc>> {
        RefMut::filter_map(self.node.borrow_mut(), |n| {
            if let NodeValue::Node(v) = &mut n.value { Some(v) } else { None }
        }).ok()
    }
    pub fn set_node(&mut self, val: NodeRc) {
        self.set_value(NodeValue::Node(val))
    }


    pub fn is_list(&self) -> bool {
        matches!(self.node.borrow().value, NodeValue::List(_))
    }
    pub fn as_list(&self) -> Option<Ref<'_, Vec<NodeValue>>> {
        Ref::filter_map(self.node.borrow(), |n| {
            if let NodeValue::List(v) = &n.value { Some(v) } else { None }
        }).ok()
    }
    pub fn as_mut_list(&self) -> Option<RefMut<'_, Vec<NodeValue>>> {
        RefMut::filter_map(self.node.borrow_mut(), |n| {
            if let NodeValue::List(v) = &mut n.value { Some(v) } else { None }
        }).ok()
    }
    pub fn set_list(&mut self, val: Vec<NodeValue>) {
        self.set_value(NodeValue::List(val))
    }


    pub fn is_map(&self) -> bool {
        matches!(self.node.borrow().value, NodeValue::Map(_))
    }
    pub fn as_map(&self) -> Option<Ref<'_, BTreeMap<Box<str>, NodeValue>>> {
        Ref::filter_map(self.node.borrow(), |n| {
            if let NodeValue::Map(v) = &n.value { Some(v) } else { None }
        }).ok()
    }
    pub fn as_mut_map(&self) -> Option<RefMut<'_, BTreeMap<Box<str>, NodeValue>>> {
        RefMut::filter_map(self.node.borrow_mut(), |n| {
            if let NodeValue::Map(v) = &mut n.value { Some(v) } else { None }
        }).ok()
    }
    pub fn set_map(&mut self, val: BTreeMap<Box<str>, NodeValue>) {
        self.set_value(NodeValue::Map(val))
    }

}
*/