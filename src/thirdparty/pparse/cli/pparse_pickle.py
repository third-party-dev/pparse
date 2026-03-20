

def register_pparse_pickle(subparsers):
    pickle_parser = subparsers.add_parser("pickle", help="pickle command")
    pickle_subparser = pickle_parser.add_subparsers(
        dest="pickle_command", required=True
    )

    pickle_parse_parser = pickle_subparser.add_parser(
        "parse", help="pickle parse command"
    )
    pickle_parse_parser.add_argument("--print", action="store_true", help="print to stdout")
    pickle_parse_parser.add_argument("path")
    pickle_parse_parser.set_defaults(func=pickle_parse)


def pickle_parse(args):
    # TODO: This code needs to be replaced with a view object.
    # from pprintpp import pprint
    from thirdparty.pparse.view.pickle import Pickle
    from thirdparty.pparse.utils import pparse_repr

    print(f"Parsing pickle from: {args.path}")

    try:
        obj = Pickle().open_fpath(args.path)
        pkl = obj._extraction._result["pkl"].value[0].value[0]
        history = obj._extraction._result["pkl"].value[0].history

    except Exception as e:
        print(e)
        import traceback
        traceback.print_exc()

    if args.print:
        print(pparse_repr(pkl))

    if hasattr(args, "breakpoint") and args.breakpoint:
        print(f"Locals: {list(locals().keys())}")
        breakpoint()


