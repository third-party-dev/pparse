def register_pparse_pytorch(subparsers):
    pytorch_parser = subparsers.add_parser("pytorch", help="pytorch command")
    pytorch_subparser = pytorch_parser.add_subparsers(
        dest="pytorch_command", required=True
    )

    pytorch_view_parser = pytorch_subparser.add_parser(
        "view", help="pytorch parse command"
    )
    pytorch_view_parser.add_argument("path")
    pytorch_view_parser.set_defaults(func=pytorch_view)

    pytorch_unpickle_parser = pytorch_subparser.add_parser(
        "unpickle", help="pytorch unpickle command"
    )
    pytorch_unpickle_parser.add_argument("path")
    pytorch_unpickle_parser.set_defaults(func=pytorch_unpickle)

    # Generic "hash" command that implicitly does the "arc hash"
    pytorch_hash_parser = pytorch_subparser.add_parser(
        "hash", help="pytorch hash command"
    )
    # debug argument
    pytorch_hash_parser.add_argument(
        "--hashed_data_path",
        dest="hashed_data_path",
        action="store",
        help="hashed data output",
        default=None,
    )
    pytorch_hash_parser.add_argument(
        "--keep_lm_head",
        dest="keep_lm_head",
        action="store_true",
        help="lm_head is removed without this flag",
        default=False,
    )
    pytorch_hash_parser.add_argument("path")
    pytorch_hash_parser.set_defaults(func=pytorch_hash)

    # Generic "transform" command that implicitly does the "to safetensors" op
    pytorch_transform_parser = pytorch_subparser.add_parser(
        "transform", help="transform pytorch"
    )
    pytorch_transform_parser.add_argument("path")
    pytorch_transform_parser.add_argument(
        "outpath", default="converted_output.safetensors"
    )
    pytorch_transform_parser.set_defaults(func=pytorch_transform)


def pytorch_unpickle(args):
    # TODO: This code needs to be replaced with a view object.
    # from pprintpp import pprint
    import thirdparty.pparse.lib as pparse
    from thirdparty.pparse.lazy.pickle import Parser as LazyPickleParser
    from thirdparty.pparse.utils import pparse_repr

    print(f"Parsing pickle from: {args.path}")

    try:
        #'output/gpt2-pytorch/data.pkl'
        parser_reg = {"pkl": LazyPickleParser}
        data_source = pparse.Data(path=args.path)
        data_range = pparse.Range(data_source.open(), data_source.length)
        root = pparse.BytesExtraction(name=args.path, reader=data_range)
        root.discover_parsers(parser_reg).scan_data()

    except pparse.EndOfDataException as e:
        print(e)
        pass
    except Exception as e:
        print(e)
        import traceback

        traceback.print_exc()

    pkl = root._result["pkl"]
    obj = pkl.value[0].value[0]
    history = root._result["pkl"].value[0].history

    print(pparse_repr(obj))

    if hasattr(args, "breakpoint") and args.breakpoint:
        print(f"Locals: {list(locals().keys())}")
        breakpoint()


def pytorch_view(args):
    from thirdparty.pparse.utils import pparse_repr
    from thirdparty.pparse.view.pytorch import PyTorch

    print(f"Parsing pytorch from: {args.path}")

    try:
        obj = PyTorch().open_fpath(args.path)

        # obj.tensor('lm_head.weight').get_data_bytes()

    except Exception as e:
        print(e)
        import traceback

        traceback.print_exc()

    if hasattr(args, "breakpoint") and args.breakpoint:
        print(f"Locals: {list(locals().keys())}")
        breakpoint()


def pytorch_hash(args):
    from thirdparty.pparse.view.pytorch import PyTorch

    print(f"Hashing pytorch from: {args.path} with: arc")

    try:
        obj = PyTorch().open_fpath(args.path)
        print(
            obj.as_arc_hash(
                hashed_data_path=args.hashed_data_path, keep_lm_head=args.keep_lm_head
            )
        )

    except Exception as e:
        print(e)
        import traceback

        traceback.print_exc()

    if hasattr(args, "breakpoint") and args.breakpoint:
        print(f"Locals: {list(locals().keys())}")
        breakpoint()


def pytorch_transform(args):
    from thirdparty.pparse.view.pytorch import PyTorch

    print(f"Transform pytorch from: {args.path} to: {args.outpath}")

    try:
        obj = PyTorch().open_fpath(args.path)
        obj.as_safetensors(args.outpath)

    except Exception as e:
        print(e)
        import traceback

        traceback.print_exc()

    if hasattr(args, "breakpoint") and args.breakpoint:
        print(f"Locals: {list(locals().keys())}")
        breakpoint()
