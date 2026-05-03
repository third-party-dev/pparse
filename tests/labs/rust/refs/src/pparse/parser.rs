
use crate::pparse::node::{
    NodeId,
    Node,
    NodeContext,
    NodeArena,
    NodeValue,
};
use core::cell::RefCell;
use alloc::rc::{
    Rc,
    Weak,
};
use core::any::{
    Any,
    //TypeId
};



pub trait ParserBase {
    fn as_any(&self) -> &dyn Any;
    fn as_any_mut(&mut self) -> &mut dyn Any;
    fn new_node(&self, parent_id: NodeId) -> NodeId;
    fn with_node(&self, id: NodeId, f: &mut dyn FnMut(&Node));
    fn with_node_mut(&self, id: NodeId, f: &mut dyn FnMut(&mut Node));
    fn root_id(&self) -> NodeId;
}

pub type ParserWeak = Weak<dyn ParserBase>;

pub fn new_node(parser_weak: &ParserWeak, parent_id: NodeId) -> NodeId {
    let parser = parser_weak.upgrade().unwrap();
    parser.new_node(parent_id)
}



pub struct Parser<E = ()> {
    pub arena: Option<NodeArena>,
    pub ext: E,
}

impl<E: 'static> Parser<E> {
    pub fn _new() -> Rc<RefCell<Parser<E>>> where E: Default {
        let parser_rc: Rc<RefCell<Parser<E>>> = Rc::new(RefCell::new(Parser { arena: None, ext: E::default() }));
        let parser_dyn: Rc<dyn ParserBase> = parser_rc.clone();
        let parser_weak: ParserWeak = Rc::downgrade(&parser_dyn);
        parser_rc.borrow_mut().arena = Some(NodeArena::new(parser_weak));
        parser_rc
    }

    pub fn parser_weak(&self) -> ParserWeak {
        self.arena.as_ref().unwrap().parser.clone()
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

impl<E: 'static> ParserBase for RefCell<Parser<E>> {
    fn as_any(&self) -> &dyn Any { self }
    fn as_any_mut(&mut self) -> &mut dyn Any { self }

    fn new_node(&self, parent_id: NodeId) -> NodeId {
        let mut parser = self.borrow_mut();
        let arena = parser.arena.as_ref().unwrap();
        let parser_weak = arena.parser.clone();
        let arena = parser.arena.as_mut().unwrap();
        arena.nodes.insert_with_key(|node_id| Node {
            ctx: Some(NodeContext::new(node_id, parent_id, parser_weak.clone())),
            value: NodeValue::None,
        })
    }

    fn with_node(&self, id: NodeId, f: &mut dyn FnMut(&Node)) {
        let parser = self.borrow();
        if let Some(node) = parser.arena.as_ref().unwrap().nodes.get(id) {
            f(node);
        }
    }

    fn with_node_mut(&self, id: NodeId, f: &mut dyn FnMut(&mut Node)) {
        let mut parser = self.borrow_mut();
        if let Some(node) = parser.arena.as_mut().unwrap().nodes.get_mut(id) {
            f(node);
        }
    }

    fn root_id(&self) -> NodeId {
        self.borrow().arena.as_ref().unwrap().root_id
    }
}


pub trait ParserBaseExt: ParserBase {
    fn with_node_r<R>(&self, id: NodeId, f: impl FnOnce(&Node) -> R) -> Option<R> {
        let mut result = None;
        let mut f = Some(f);
        self.with_node(id, &mut |node| {
            result = Some(f.take().unwrap()(node));
        });
        result
    }

    fn with_node_mut_r<R>(&self, id: NodeId, f: impl FnOnce(&mut Node) -> R) -> Option<R> {
        let mut result = None;
        let mut f = Some(f);
        self.with_node_mut(id, &mut |node| {
            result = Some(f.take().unwrap()(node));
        });
        result
    }
}

impl<T: ParserBase + ?Sized> ParserBaseExt for T {}


