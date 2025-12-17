'''
def register(subparsers):
    p = subparsers.add_parser("foo", help="Foo command")
    p.add_argument("--x", type=int, required=True)
    p.set_defaults(func=run)

def run(args):
    print(args.x * 2)
'''

from thirdparty.pparse.cli.registry import get_commands, load_entrypoint_plugins

def register_pparse(subparsers):
    pparse_parser = subparsers.add_parser("pparse", help="pparse command")
    pparse_parser.add_argument("--breakpoint",
        dest="breakpoint",
        action="store_true",
        help="breakpoint() after operation"
    )
    pparse_subparser = pparse_parser.add_subparsers(dest="pparse_command", required=True)


    # Load the entrypoints
    load_entrypoint_plugins("pparse_command")

    # Load plugins
    for registrar in get_commands():
        registrar(pparse_subparser)

def run(args):
    print("Running safetensors_parser command")