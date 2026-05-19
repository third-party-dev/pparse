# Generally, rerun the parser on same node.
AGAIN = 1
# Generally, run the parser on parent node.
ASCEND = 2

# Generally, rerun the parser on same node (i.e. AGAIN), plus
# pop the state stack if there is more than one state pending.
NEXT = 3