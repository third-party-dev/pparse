def register_pparse_safetensors(subparsers):
    safetensors_parser = subparsers.add_parser("safetensors", help="safetensors command")
    safetensors_subparser = safetensors_parser.add_subparsers(dest="safetensors_command", required=True)

    safetensors_header_parser = safetensors_subparser.add_parser("header", help="safetensors header command")
    safetensors_header_parser.add_argument("path")
    safetensors_header_parser.set_defaults(func=raw_header)

    safetensors_header_parser = safetensors_subparser.add_parser("pheader", help="safetensors header command")
    safetensors_header_parser.add_argument("path")
    safetensors_header_parser.set_defaults(func=pparse_pheader)

def raw_header(args):
    import struct
    import json

    print(f'Parsing header from: {args.path}')

    with open(args.path, "rb") as fobj:
        header_length = struct.unpack("<Q", fobj.read(8))[0]
        hdr_json = json.dumps(json.loads(fobj.read(header_length).decode()), indent=4)
        print(hdr_json)

    if hasattr(args, "breakpoint") and args.breakpoint:
        print(f'Locals: {list(locals().keys())}')
        breakpoint()

def pparse_pheader(args):
    # TODO: This needs some UX work.
    print(f'Parsing header from: {args.path}')

    from thirdparty.pparse.view import SafeTensors
    from pprint import pprint

    obj = SafeTensors().open_fpath(args.path)
    pprint(obj.header())

    if hasattr(args, "breakpoint") and args.breakpoint:
        print(f'Locals: {list(locals().keys())}')
        breakpoint()
    
    #tensor = obj.tensor('transformer.ln_f.bias')
    #nparr = tensor.as_numpy()