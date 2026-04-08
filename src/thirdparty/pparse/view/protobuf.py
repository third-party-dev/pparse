#!/usr/bin/env python3

import logging

log = logging.getLogger(__name__)

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lazy.protobuf import make_protobuf_parser
from thirdparty.pparse.lazy.protobuf.meta import PbImport


class Parser:
    def __init__(self):
        self._extraction = None

    def _parse(self, data_source, pbpath, msgtype, fname="unnamed.protobuf.bin"):
        
        from importlib import resources
        from pathlib import Path

        try:
            data_range = pparse.Range(data_source.open(), data_source.length)
            self._extraction = pparse.BytesExtraction(name=fpath, reader=data_range)
            parser = make_protobuf_parser(ext_list=[Path(fpath).suffix], init_msgtype=msgtype, proto=PbImport(pbpath))
            self._extraction.discover_parsers({"protobuf": parser})
            self._extraction._parser['protobuf']._root.load()

        except pparse.EndOfDataException as e:
            print(e)
            pass
        except Exception as e:
            print(e)
            import traceback

            traceback.print_exc()

        return self


    def open_fpath(self, fpath, pbpath, msgtype):
        return self._parse(pparse.FileData(path=fpath), pbpath, msgtype, fname=fpath)


    def from_bytesio(self, bytes_io, pbpath, msgtype, fname="unnamed.protobuf.bin"):
        return self._parse(pparse.BytesIoData(bytes_io=bytes_io), pbpath, msgtype, fname=fname)
