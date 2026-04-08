#!/usr/bin/env python3

import logging

log = logging.getLogger(__name__)

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lazy.protobuf import make_protobuf_parser
from thirdparty.pparse.lazy.protobuf.meta import PbImport
from thirdparty.pparse.lazy.om import Parser as LazyOmParser

class Om:
    def __init__(self):
        self._extraction = None


    def _parse(self, data_source, header_only=False, fname="unnamed.om"):
        try:
            log.info("Parsing the OM container file.")
            data_range = pparse.Range(data_source.open(), data_source.length)
            self._extraction = pparse.BytesExtraction(name=fpath, reader=data_range)
            self._extraction.discover_parsers({ "om": LazyOmParser })
            self._extraction.scan_data()

            if not header_only:
                log.info("Parsing the OM (Protobuf) ModelDef")
                from importlib import resources
                data_path = resources.files("thirdparty.pparse") / "data"
                proto = PbImport(data_path / "proto" / "ge_ir.pb")

                # ! Assuming MODEL_DEF is 2nd partition for now.
                part = self._extraction._result['om'].value['partitions'].value[1]
                part_off = 0x100
                modeldef_hdrsz = 0x80
                true_offset = part.value['offset'] + part_off + modeldef_hdrsz
                true_size = part.value['size'] - modeldef_hdrsz

                pb_range = pparse.Range(data_source.open(true_offset), true_size)
                pb_extraction = pparse.BytesExtraction(name="modeldef.pb", reader=pb_range)
                # Manually shove the extraction where its intended to be.
                self._extraction._extractions.append(pb_extraction)
                parser = make_protobuf_parser(ext_list=[".pb"], init_msgtype=".ge.proto.ModelDef", proto=proto)
                pb_extraction.discover_parsers({"protobuf": parser}).scan_data()

        except pparse.EndOfDataException as e:
            print(e)
            pass
        except Exception as e:
            print(e)
            import traceback

            traceback.print_exc()

        return self


    def open_fpath(self, fpath, header_only=False):
        return self._parse(pparse.FileData(path=fpath), header_only=header_only, fname=fpath)


    def from_bytesio(self, bytes_io, header_only=False, fname="unnamed.om"):
        return self._parse(pparse.BytesIoData(bytes_io=bytes_io), header_only=header_only, fname=fname)
