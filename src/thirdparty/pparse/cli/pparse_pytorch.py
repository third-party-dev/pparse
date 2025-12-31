def register_pparse_pytorch(subparsers):
    pytorch_parser = subparsers.add_parser("pytorch", help="pytorch command")
    pytorch_subparser = pytorch_parser.add_subparsers(dest="pytorch_command", required=True)

    pytorch_view_parser = pytorch_subparser.add_parser("view", help="pytorch parse command")
    pytorch_view_parser.add_argument("path")
    pytorch_view_parser.set_defaults(func=pytorch_view)

    pytorch_unpickle_parser = pytorch_subparser.add_parser("unpickle", help="pytorch unpickle command")
    pytorch_unpickle_parser.add_argument("path")
    pytorch_unpickle_parser.set_defaults(func=pytorch_unpickle)

def pytorch_unpickle(args):
    # TODO: This code needs to be replaced with a view object.
    #from pprintpp import pprint
    import thirdparty.pparse.lib as pparse 
    from thirdparty.pparse.lazy.pickle import Parser as LazyPickleParser
    from thirdparty.pparse.utils import pparse_repr

    print(f'Parsing pickle from: {args.path}')

    try:
        #'output/gpt2-pytorch/data.pkl'
        parser_reg = {'pkl': LazyPickleParser}
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

    pkl = root._result['pkl']
    obj = pkl.value[0].value[0]
    history = root._result['pkl'].value[0].history

    print(pparse_repr(obj))

    if hasattr(args, "breakpoint") and args.breakpoint:
        print(f'Locals: {list(locals().keys())}')
        breakpoint()

def pytorch_view(args):
    from thirdparty.pparse.view.pytorch import PyTorch
    from thirdparty.pparse.utils import pparse_repr

    print(f'Parsing pytorch from: {args.path}')

    try:
        obj = PyTorch().open_fpath(args.path)
        '''
            pkl = obj._extraction._extractions[0]._result['pkl']
            tensor_dict = pkl.value[0].value[0]
            tensor_list = tensor_dict.keys()
            history = pkl.value[0].history
            print(pparse_repr(tensor_dict['transformer.ln_f.bias']))

            reduce_call = tensor_dict['transformer.ln_f.bias']
            persid_call = reduce_call.arg[0]
            type_tag = persid_call.arg[0]
            type_name = persid_call.arg[1]
            # torch.FloatStorage => dtype=float32
            data_key = persid_call.arg[2]
            data_dest = persid_call.arg[3]
            elem_cnt = persid_call.arg[4]

            #import numpy as np
            #raw = read_bytes_for_id("147")
            #arr = np.frombuffer(raw, dtype=np.float32, count=768)

            # FloatStorage         | torch.float32    | np.float32
            # DoubleStorage        | torch.float64    | np.float64
            # HalfStorage          | torch.float16    | np.float16
            # BFloat16Storage      | torch.bfloat16   | np.dtype("bfloat16")
            # CharStorage          | torch.int8       | np.int18
            # ShortStorage         | torch.int16      | np.int16
            # IntStorage           | torch.int32      | np.int32
            # LongStorage          | torch.int64      | np.int64
            # ByteStorage          | torch.uint8      | np.uint8
            # BoolStorage          | torch.bool       | np.bool_
            # ComplexFloatStorage  | torch.complex64  | np.complex64
            # ComplexDoubleStorage | torch.complex128 | np.complex128
            # QInt8Storage         | torch.qint8      | np.int8
            # QUInt8Storage        | torch.quint8     | np.uint8
            # QInt32Storage        | torch.qint32     | np.int32

            # No UInt16Storage, UInt32Storage, UInt64Storage
        '''
    except Exception as e:
        print(e)
        import traceback
        traceback.print_exc()

    if hasattr(args, "breakpoint") and args.breakpoint:
        print(f'Locals: {list(locals().keys())}')
        breakpoint()