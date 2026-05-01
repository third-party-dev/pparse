use core::cell::{Ref, RefCell, RefMut};
use alloc::rc::Rc;
use alloc::rc::Weak;
use alloc::vec::Vec;
//use alloc::vec;
use alloc::collections::BTreeMap;

use core::fmt::{Display, Formatter, Result};
use alloc::boxed::Box;

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



// pub struct NodeContext {
//     parent: Option<NodeWeak>,
// }

// pub struct Node {
//     ctx: Option<NodeContext>,
//     pub value: NodeValue,
// }









pub type NodeRc = Rc<RefCell<Node>>;
pub type NodeWeak = Weak<RefCell<Node>>;

pub trait ParsingStateIface {
    fn parse_data(&mut self, node: &NodeRc);
}

pub struct NodeContext {
    parent: Option<NodeWeak>,
    //state
    //reader
    //parser
    //start
    //end
    //descendants
}

pub trait NodeContextIface {
    fn new(parent: Option<NodeWeak>) -> Self;
}

impl NodeContextIface for NodeContext {
    fn new(parent: Option<NodeWeak>) -> Self {
        NodeContext { parent }
    }
}

pub enum NodeValue {
    None,
    Integer(i64),
    Unsigned(u64),
    Float(f64),
    Str(Box<str>),
    Bytes(Box<[u8]>),
    Node(NodeRc),
    List(Vec<NodeValue>),
    Map(BTreeMap<Box<str>, NodeValue>),
}

pub struct Node<CtxType = NodeContext> {
    ctx: Option<CtxType>,
    pub value: NodeValue,
}

impl<CtxType: NodeContextIface> Node<CtxType> {
    fn _new(parent: Option<NodeWeak>) -> Rc<RefCell<Self>> {
        let ctx = CtxType::new(parent);
        Rc::new(RefCell::new(
            Node { ctx: Some(ctx), value: NodeValue::None }
        ))
    }

    pub fn new(parent: &NodeRc) -> Rc<RefCell<Self>> {
        Self::_new(Some(Rc::downgrade(parent)))
    }

    // Hides Option<>.
    pub fn new_root() -> Rc<RefCell<Self>> {
        Self::_new(None)
    }

}

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