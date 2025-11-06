#!/usr/bin/env python3

from pprint import pprint
from thirdparty.pparse.lib import Data, Artifact, PARSERS
from thirdparty.pparse.parsers.json import JsonParser

PARSERS['json'] = JsonParser

# Data is independent of Artifact/Parser tree.
data = Data(path='test.json')

# Top Artifact has not parent parser.
root = Artifact(data.open()).set_fname('test.json').process_data()

# Dump output for examination.
print("Dumping root to output.txt")
with open("output.txt", "w") as fobj:
    pprint(root, stream=fobj, indent=2)
print("Dump complete.")