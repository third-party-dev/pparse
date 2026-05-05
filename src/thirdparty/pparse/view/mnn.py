#!/usr/bin/env python3

import logging

log = logging.getLogger(__name__)

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lazy.flatbuffers import make_flatbuffers_parser

class MNN:
    def __init__(self):
        self._extraction = None

    def _parse(self, data_source, fname="unnamed.mnn"):

        import json
        from importlib import resources
        from pathlib import Path

        data_path = resources.files("thirdparty.pparse.data")
        with open(data_path/"fbs"/"mnn"/"MNN.json", "r") as fobj:
            json_schema = json.loads(fobj.read())

        try:
            data_range = pparse.Range(data_source.open(), data_source.length)
            self._extraction = pparse.BytesExtraction(name=fname, reader=data_range)
            parser = make_flatbuffers_parser(ext_list=[Path(fname).suffix], json_schema=json_schema)
            self._extraction.discover_parsers({'flatbuffers': parser})
            self._extraction._parser['flatbuffers']._root.load()

            # TODO: Build out tensor objects.
            # TFlite's looks like this:
            # root_table = self.root_node().value['root_table'].value
            # buffers = root_table['buffers'].value
            # for _entry in root_table['subgraphs'].value[0].value['tensors'].value:
            #     entry = _entry.value
            #     buffer = buffers[entry['buffer']].value
            #     self._tensors[entry['name']] = Tensor(entry, buffer)

        except pparse.EndOfDataException as e:
            print(e)
            pass
        except Exception as e:
            print(e)
            import traceback

            traceback.print_exc()

        return self


    def root_node(self):
        return self._extraction._parser['flatbuffers']._root


    def open_fpath(self, fpath):
        return self._parse(pparse.FileData(path=fpath), fname=fpath)


    def from_bytesio(self, bytes_io, fname="unnamed.mnn"):
        return self._parse(pparse.BytesIoData(bytes_io=bytes_io), fname=fname)

