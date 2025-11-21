This pickle parser is multi phased.
- In the first phase, we parse out each of the OpCodes.
- Once we have a listing of OpCode objects to work with, we go through the list and attempt to construct a higher level node tree that more closely represents the python object the pickle data represents.

Both of these phases are manged by a single 'Parser' class.

A view object can then be used to reference the node tree in a more pythonic manner.

Note: No external code will be executed in the parsing of the pickle. All external code execution is deferred.

