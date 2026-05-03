
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

use alloc::vec;
use alloc::collections::BTreeMap;
use alloc::rc::Rc;
use alloc::boxed::Box;

use crate::sys::cstdlib::{
  exit,
  write,
  STDOUT,
};

use crate::pparse::{
  //Cursor,
  //Data,
  FileData,
  DataUtl,
};

use crate::pparse::node::{
    NodeId,
    Node,
    NodeValue,
};

use crate::pparse::parser::{
  Parser,
  //ParserWeak,
  new_node,
  ParserBase,
  ParserBaseExt, // Required for with_node_r
};

use crate::pparse::lazy::json::parser::JsonParser;


fn test_cstdlib() {
  println!("---------------------------------------------\nTEST: cstdlib");
  let mystr: &str = "formatting works.";
  write(STDOUT, b"Hello using write(STDOUT)\n");
  // breakpoint!();
  println!("Hello using println!: {}", mystr);
}

fn test_node_arena() {
  println!("---------------------------------------------\nTEST: node_arena");
  let parser_rc = Parser::<()>::_new();
  let parser_weak = parser_rc.borrow().parser_weak();
  
  let rootid = parser_rc.root_id(); //rootid_with_parser(&parser_weak);
  println!("Root node id: {}", rootid);

  parser_rc.with_node_mut(rootid, &mut |root_node: &mut Node| {
    root_node.value = NodeValue::Integer(67);
  });

  // node_with_parser_mut(&parser_weak, rootid, |root_node| {
  //   root_node.value = NodeValue::Integer(67);
  // });

  let child_nodeid: NodeId = new_node(&parser_weak, rootid);

  //node_with_parser_mut(&parser_weak, rootid, |root_node| {
  parser_rc.with_node_mut(rootid, &mut |root_node: &mut Node| {
    root_node.value = NodeValue::NodeId(child_nodeid);
  });

  // let nodeid = node_with_parser(&parser_weak, rootid, |root_node| {
  // // let nodeid = parser_rc.with_node::<NodeId>(rootid, |root_node: &Node| {
  //   root_node.as_nodeid().unwrap()
  // });

  //let nodeid = node_with_parser(&parser_weak, rootid, |node| node.as_nodeid().unwrap();
  let nodeid = parser_rc.with_node_r(rootid, |node| node.as_nodeid().unwrap()).unwrap();

  parser_rc.with_node_mut(nodeid, &mut |node| {
  //node_with_parser_mut(&parser_weak, nodeid, |node| {
    node.value = NodeValue::Integer(123);
  });

  parser_rc.with_node(nodeid, &mut |node| {
  //node_with_parser(&parser_weak, nodeid, |node| {
    println!("child value {}", node.value);
  });

  parser_rc.with_node_mut(nodeid, &mut |node| {
  //node_with_parser_mut(&parser_weak, nodeid, |node| {
    let list = vec![
        NodeValue::Integer(42),
        NodeValue::Str("hello".into()),
    ];
    node.set_list(list);
    //node.value = NodeValue::Integer(123);
    println!("child value {}", node.value);

    if node.is_list() {
        let list_ref = node.as_list_mut();
        if !list_ref.is_none() {
            let list_ref = list_ref.unwrap();

            list_ref.push(NodeValue::Integer(313));
        }
    }
    println!("Node value (as list): {}", node.value);
  });


  parser_rc.with_node_mut(nodeid, &mut |node| {
  //node_with_parser_mut(&parser_weak, nodeid, |node| {
    let map = BTreeMap::from([
      ("a".into(), NodeValue::Integer(42)),
      ("b".into(), NodeValue::None),
    ]);
    node.set_map(map);
    //node.value = NodeValue::Integer(123);
    println!("child value {}", node.value);

    if node.is_map() {
      let map_ref = node.as_map_mut();
      if !map_ref.is_none() {
        let map_ref = map_ref.unwrap();
        // Add entry
        map_ref.insert("c".into(), NodeValue::Str("mine".into()));
        // Do replace
        map_ref.insert("a".into(), NodeValue::Integer(303));
        // Remove entry
        map_ref.remove("b");
      }
    }

    println!("Node value (as map): {}", node.value);
  });

  parser_rc.with_node_mut(rootid, &mut |node| {
  //node_with_parser_mut(&parser_weak, rootid, |node| {
    // ! No ref counting leaks child node permanently.
    node.value = NodeValue::None;
    println!("Node value: {}", node.value);
  });

  { // Dump all entries in Arena.
    let parser = parser_rc.borrow();
    let arena = parser.arena.as_ref().unwrap();
    println!("Key: Value for Arena\n--------------------------");
    for (key, node) in &arena.nodes {
      println!("{}: {}", key, node.value);
    }
  };
}

fn test_json_parser() {
  println!("---------------------------------------------\nTEST: json_parser");


  let data_source = Rc::new(FileData::open(Box::from("path/to/file")));
  //let cursor = Cursor::new(data_source, 0);
  let cursor = DataUtl::open(data_source, 0);


  let json_parser = JsonParser::new();
  json_parser.borrow().test();

  let mine: &[u8] = b"asdf\0";
  //let _:()=mine;

  // TODO: Create cursor
  // TODO: Create range
  // TODO: Create BytesExtraction (and add parser)
  // TODO: Setup parser with source Extraction
  // TODO: json_parser.root.load()
}


#[no_mangle]
pub extern "C" fn main(_argc: i32, _argv: *const *const u8) -> ! {
  test_cstdlib();
  test_node_arena();
  test_json_parser();
  println!("---------------------------------------------");
  println!("Exit without error.");
  println!("---------------------------------------------");
  exit(0);
}



























































// Downcast Rc<dyn ParserBase> → &RefCell<Parser<JsonExt>>
  // let json_parser = parser_rc
  //     .as_any()
  //     .downcast_ref::<RefCell<JsonParser>>()
  //     .expect("node does not belong to a JsonParser");




// fn node_with_node<R>(current_node: &Node, nodeid: NodeId, f: impl FnOnce(&Node) -> R) -> R {
//     let parser = current_node.ctx.as_ref().unwrap().parser().upgrade().unwrap();
//     let mut result: Option<R> = None;

//     let mut f_opt = Some(f);
//     parser.with_node(nodeid, &mut |node| {
//         result = Some(f_opt.take().unwrap()(node));
//     });
//     result.unwrap()
    
// }

// fn node_with_node_mut<R>(current_node: &Node, nodeid: NodeId, f: impl FnOnce(&mut Node) -> R) -> R {
//     let parser = current_node.ctx.as_ref().unwrap().parser().upgrade().unwrap();
//     let mut result: Option<R> = None;
//     let mut f_opt = Some(f);
//     parser.with_node_mut(nodeid, &mut |node| {
//         result = Some(f_opt.take().unwrap()(node));
//     });
//     result.unwrap()
// }

// fn node_with_parser<R>(parser_weak: &ParserWeak, nodeid: NodeId, f: impl FnOnce(&Node) -> R) -> R {
//     let parser = parser_weak.upgrade().unwrap();
//     let mut result: Option<R> = None;
//     let mut f_opt = Some(f);
//     parser.with_node(nodeid, &mut |node| {
//         result = Some(f_opt.take().unwrap()(node));
//     });
//     result.unwrap()
// }

// fn node_with_parser_mut<R>(parser_weak: &ParserWeak, nodeid: NodeId, f: impl FnOnce(&mut Node) -> R) -> R {
//     let parser = parser_weak.upgrade().unwrap();
//     let mut result: Option<R> = None;
//     let mut f_opt = Some(f);
//     parser.with_node_mut(nodeid, &mut |node| {
//         result = Some(f_opt.take().unwrap()(node));
//     });
//     result.unwrap()
// }

// fn rootid_with_parser(parser_weak: &ParserWeak) -> NodeId {
//     parser_weak.upgrade().unwrap().root_id()
// }