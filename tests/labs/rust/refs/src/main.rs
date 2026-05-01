
/*

Nodes:
  - All parsed data can be represented as a graph of Nodes.
  - Have a value that can be a number, string, bytes, node, list, or map.
  - NodeContext:
    - Have a context object that represents parsing state.
    - Contains: current state machine state, parent node, parser instance ref, and cursor/range from extraction.
    - Context objects (and their references) are expendable once parsing is complete.

  - Once the root node has been initialized by a parser, the parsing is driven by
    the graph itself, not the parser class. This design allows the code to
    heuristically skip large flat data until referenced. It also allows replaying
    parsing when node branches have been omitted or removed to conserve memory.
  - Node graphs are scoped to a specific parser, but may use other parsers
    to parse many formats that are related or coupled by design.

Parser:
  - A parser class defines identification code and parsing code.
  - A parser instance represents the operation to parse an Extraction.
  - Parsers use state machines to parse data into graph nodes.
  - Parser constructor initialized the root node to start the state machine.

Extraction:
  - An extraction is parser output intended for further external parsing.
  - A range of data not tightly bound to current format is an extraction.

Other Types:
  - DataSource - Represents a buffer or file descriptor that can be seeked and read.
  - Cursor - Contains DataSource and Offset.
  - Range - Contains start cursor, current cursor, and length.
  - Reader - Abstract type (trait) of Cursor and Range.
  - View - Concrete set of classes for one-shot parsing of formats.


*/

#![no_std]
#![no_main]
#![allow(dead_code)]

extern crate alloc;

mod pparse;
mod sys;

use crate::sys::cstdlib::{exit, write, STDOUT};

//use crate::pparse::node::{Node, NodeRc, NodeUtl, NodeValue};

//use alloc::vec;
//use alloc::collections::BTreeMap;


// pub struct ParserBase {
//     root: Option<NodeRc>,
// }

// impl ParserBase {
//     fn new() -> Self {
//         ParserBase { root: Some(Node::new_root()) }
//     }

//     // TODO: match_magic(cursor)
//     // TODO: match_extension(fname)

//     pub fn get_root(&self) -> Option<&NodeRc> {
//         self.root.as_ref()
//     }

//     fn get_id() -> &'static str {
//         "unknown"
//     }
// }

#[no_mangle]
pub extern "C" fn main(_argc: i32, _argv: *const *const u8) -> ! {
    let mystr: &str = "formatting works.";
    write(STDOUT, b"Hello using write(STDOUT)\n");
    // breakpoint!();
    println!("Hello using println!: {}", mystr);
    println!("---------------------------------------------");

    // let _parser = ParserBase::new();

    // let root_ref: &NodeRc = _parser.get_root().unwrap();
    // let mut root: NodeUtl = NodeUtl::wrap(root_ref);

    // // --- Create Vec of NodeValues ---
    // let list = vec![
    //     NodeValue::Integer(42),
    //     NodeValue::Str("hello".into()),
    // ];
    // root.set_list(list);
    
    // // Add another item.
    // if root.is_list() {
    //     let list_ref = root.as_mut_list();
    //     if !list_ref.is_none() {
    //         let mut list_ref = list_ref.unwrap();

    //         list_ref.push(NodeValue::Integer(303));
    //     }
    // }
    // println!("Root value (as list): {}", root.value());

    // // --- Create BTreeMap of NodeValues ---
    // let map = BTreeMap::from([
    //     ("a".into(), NodeValue::Integer(42)),
    //     ("b".into(), NodeValue::None),
    // ]);
    // root.set_map(map);

    // if root.is_map() {
    //     let map_ref = root.as_mut_map();
    //     if !map_ref.is_none() {
    //         let mut map_ref = map_ref.unwrap();
    //         // Add entry
    //         map_ref.insert("c".into(), NodeValue::Str("mine".into()));
    //         // Do replace
    //         map_ref.insert("a".into(), NodeValue::Integer(303));
    //         // Remove entry
    //         map_ref.remove("b");
    //     }
    // }

    // println!("Root value (as map): {}", root.value());

    // // --- Create object with root as parent. ---
    // let child_ref = root.new_child();
    // // Assign object to root as child.
    // root.set_node(child_ref);

    // println!("Root value (as node): {}", root.value());

    // if root.is_node() {
    //     let child_ref = root.as_node();
    //     if !child_ref.is_none() {
    //         let child_ref = child_ref.unwrap();

    //         let mut child = NodeUtl::wrap(&child_ref);
    //         child.set_bytes(b"tryit\n");
    //         println!("Child value (as bytes): {}", child.value());
    //     }
    // }

    exit(0);
}




