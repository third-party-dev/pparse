def register_pparse_onnx(subparsers):
    onnx_parser = subparsers.add_parser("onnx", help="onnx command")
    onnx_subparser = onnx_parser.add_subparsers(dest="onnx_command", required=True)

    onnx_view_parser = onnx_subparser.add_parser("view", help="onnx parse command")
    onnx_view_parser.add_argument("path")
    onnx_view_parser.set_defaults(func=onnx_view)

    # Generic "hash" command that implicitly does the "arc hash"
    onnx_hash_parser = onnx_subparser.add_parser("hash", help="onnx hash command")
    # debug argument
    onnx_hash_parser.add_argument(
        "--hashed_data_path",
        dest="hashed_data_path",
        action="store",
        help="hashed data output",
        default=None,
    )
    onnx_hash_parser.add_argument(
        "--keep_lm_head",
        dest="keep_lm_head",
        action="store_true",
        help="lm_head is removed without this flag",
        default=False,
    )
    onnx_hash_parser.add_argument("path")
    onnx_hash_parser.set_defaults(func=onnx_hash)

    # Generic "transform" command that implicitly does the "to safetensors" op
    onnx_transform_parser = onnx_subparser.add_parser(
        "transform", help="transform pytorch"
    )
    onnx_transform_parser.add_argument(
        "--keep_lm_head",
        dest="keep_lm_head",
        action="store_true",
        help="lm_head is removed without this flag",
        default=False,
    )
    onnx_transform_parser.add_argument("path")
    onnx_transform_parser.add_argument(
        "outpath", default="converted_output.safetensors"
    )
    onnx_transform_parser.set_defaults(func=onnx_transform)


"""
Event code 103 (KEY_UP)
    Event code 104 (KEY_PAGEUP)
    Event code 105 (KEY_LEFT)
    Event code 106 (KEY_RIGHT)
    Event code 107 (KEY_END)
    Event code 108 (KEY_DOWN)


    Up
    Event: time 1768662096.034911, type 4 (EV_MSC), code 4 (MSC_SCAN), value 7005d
    Event: time 1768662096.034911, type 1 (EV_KEY), code 76 (KEY_KP5), value 1
    Left
    Event: time 1768662105.481773, type 4 (EV_MSC), code 4 (MSC_SCAN), value 70059
    Event: time 1768662105.481773, type 1 (EV_KEY), code 79 (KEY_KP1), value 1
    Right
    Event: time 1768662106.702784, type 4 (EV_MSC), code 4 (MSC_SCAN), value 7005b
    Event: time 1768662106.702784, type 1 (EV_KEY), code 81 (KEY_KP3), value 1
    Down
    Event: time 1768662107.481918, type 4 (EV_MSC), code 4 (MSC_SCAN), value 7005a
    Event: time 1768662107.481918, type 1 (EV_KEY), code 80 (KEY_KP2), value 1



    # /etc/udev/hwdb.d/90-numpad-arrows.hwdb
    evdev:input:b0003v32ACp0014*
     KEYBOARD_KEY_7005d=up
     KEYBOARD_KEY_70059=left
     KEYBOARD_KEY_7005a=down
     KEYBOARD_KEY_7005b=right

    sudo systemd-hwdb update
    sudo udevadm trigger
"""


def onnx_view(args):
    from thirdparty.pparse.utils import pparse_repr
    from thirdparty.pparse.view.onnx import Onnx

    print(f"Parsing onnx from: {args.path}")

    # try:
    #     obj = Onnx().open_fpath(args.path)

    #     # obj.tensor('lm_head.weight').get_data_bytes()

    # except Exception as e:
    #     print(e)
    #     import traceback

    #     traceback.print_exc()

    # if hasattr(args, "breakpoint") and args.breakpoint:
    #     print(f"Locals: {list(locals().keys())}")
    #     breakpoint()


def onnx_hash(args):
    from thirdparty.pparse.view.onnx import Onnx

    print(f"Hashing onnx from: {args.path} with: arc")

    # try:
    #     obj = Onnx().open_fpath(args.path)
    #     print(
    #         obj.as_arc_hash(
    #             hashed_data_path=args.hashed_data_path, keep_lm_head=args.keep_lm_head
    #         )
    #     )

    # except Exception as e:
    #     print(e)
    #     import traceback

    #     traceback.print_exc()

    # if hasattr(args, "breakpoint") and args.breakpoint:
    #     print(f"Locals: {list(locals().keys())}")
    #     breakpoint()


def onnx_transform(args):
    from thirdparty.pparse.view.onnx import Onnx

    print(f"Transform pytorch from: {args.path} to: {args.outpath}")

    # try:
    #     obj = Onnx().open_fpath(args.path)
    #     obj.as_safetensors(args.outpath, keep_lm_head=args.keep_lm_head)

    # except Exception as e:
    #     print(e)
    #     import traceback

    #     traceback.print_exc()

    # if hasattr(args, "breakpoint") and args.breakpoint:
    #     print(f"Locals: {list(locals().keys())}")
    #     breakpoint()
