# Partial Parser

## PParse (as in "partial parser")

`pparse` aims to:

- Provide an interface for forensic analysis of various file formats.

- Enable parsing of very large files that do not fit on a single machine's memory.

- Parse model files that have been truncated (corrupted). In this context, pparse aims to parse up to the point where the file becomes invalid and keeps all of the parsed state to that point without crashing. (Quite annoying when you know a piece of software has 90% of the file and dies because it can't verify something I never asked it to verify!)
