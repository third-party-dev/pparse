from ._native import ParseTree, ParseError, NULL_INDEX

tree = ParseTree()
try:
    tree.open_file("/data/huge_file.dat")
    tree.parse()
    tree.close_file()

    root = tree.root()
    print(f"nodes: {tree.node_count()}")
    print(f"root children: {tree.node_child_count(root)}")

    i = 0
    while i < tree.node_child_count(root):
        child = tree.node_child(root, i)
        print(f"  [{i}] kind={tree.node_kind(child)} "
              f"start={tree.node_start(child)} "
              f"end={tree.node_end(child)}")
        i += 1

except ParseError as e:
    print(f"parse error {e.code}: {e}")
finally:
    tree.close_file()