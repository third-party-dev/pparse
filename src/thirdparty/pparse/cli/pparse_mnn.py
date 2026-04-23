
import logging
log = logging.getLogger(__name__)

def register_pparse_mnn(subparsers):
    mnn_parser = subparsers.add_parser("mnn", help="mnn command")
    mnn_subparser = mnn_parser.add_subparsers(dest="mnn_command", required=True)


    mnn_view_parser = mnn_subparser.add_parser("view", help="mnn view command")
    mnn_view_parser.add_argument("--print", action="store_true", help="print to stdout")
    mnn_view_parser.add_argument("path")
    mnn_view_parser.set_defaults(func=mnn_view)


def mnn_view(args):
    from thirdparty.pparse.utils import activate_logging
    activate_logging(args)
    
    from thirdparty.pparse.view.mnn import MNN

    print(f"Parsing mnn from: {args.path}")

    try:
        obj = MNN().open_fpath(args.path)
        mnn = obj._extraction._result['flatbuffers'].value

        if args.print:
            print(mnn.dumps())
            #obj.root_node().dump()

    except Exception as e:
        print(e)
        import traceback
        traceback.print_exc()

    if hasattr(args, "breakpoint") and args.breakpoint:
        print(f"Locals: {list(locals().keys())}")
        breakpoint()


