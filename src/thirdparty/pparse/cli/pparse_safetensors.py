import traceback
from pprint import pprint


def register_pparse_safetensors(subparsers):
    safetensors_parser = subparsers.add_parser(
        "safetensors", help="safetensors command"
    )
    safetensors_subparser = safetensors_parser.add_subparsers(
        dest="safetensors_command", required=True
    )

    safetensors_header_parser = safetensors_subparser.add_parser(
        "header", help="safetensors header command"
    )
    safetensors_header_parser.add_argument("path")
    safetensors_header_parser.set_defaults(func=raw_header)

    safetensors_pheader_parser = safetensors_subparser.add_parser(
        "pheader", help="safetensors header command"
    )
    safetensors_pheader_parser.add_argument("path")
    safetensors_pheader_parser.set_defaults(func=pparse_pheader)

    safetensors_hash_parser = safetensors_subparser.add_parser(
        "hash", help="safetensors hash command"
    )
    # debug argument
    safetensors_hash_parser.add_argument("--hashed_data_path",
        dest="hashed_data_path",
        action="store",
        help="hashed data output",
        default=None
    )
    safetensors_hash_parser.add_argument("path")
    safetensors_hash_parser.set_defaults(func=safetensors_hash)


def raw_header(args):
    import json
    import struct

    print(f"Parsing header from: {args.path}")

    with open(args.path, "rb") as fobj:
        header_length = struct.unpack("<Q", fobj.read(8))[0]
        hdr_json = json.dumps(json.loads(fobj.read(header_length).decode()), indent=4)
        print(hdr_json)

    if hasattr(args, "breakpoint") and args.breakpoint:
        print(f"Locals: {list(locals().keys())}")
        breakpoint()


def pparse_pheader(args):
    from thirdparty.pparse.view import SafeTensors

    # TODO: This needs some UX work.
    print(f"Parsing header from: {args.path}")

    obj = SafeTensors().open_fpath(args.path)
    pprint(obj.header())

    if hasattr(args, "breakpoint") and args.breakpoint:
        print(f"Locals: {list(locals().keys())}")
        breakpoint()

    # tensor = obj.tensor('transformer.ln_f.bias')
    # nparr = tensor.as_numpy()


def safetensors_hash(args):
    from thirdparty.pparse.view import SafeTensors

    print(f"Hashing safetensors from: {args.path} with: arc")

    try:
        obj = SafeTensors().open_fpath(args.path)
        print(obj.as_arc_hash(hashed_data_path=args.hashed_data_path))

    except Exception as e:
        print(e)
        traceback.print_exc()

    if hasattr(args, "breakpoint") and args.breakpoint:
        print(f"Locals: {list(locals().keys())}")
        breakpoint()
