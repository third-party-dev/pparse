import sys
import os
import pathlib

import logging
log = logging.getLogger(__name__)

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lazy.json import Parser as LazyJsonParser
from thirdparty.pparse.lazy.safetensors import Parser as LazySafetensorsParser

# TODO: 1. Do JSON parse and save its result
# TODO: 2. Get all uniq children and create Extractions
# TODO: 3. _scan_children with safetensors parser.


class Parser(pparse.Parser):

    @staticmethod
    def match_extension(fname: str):
        if not fname:
            return False
        for ext in ['.json']:
            if fname.endswith(ext):
                return True
        return False


    @staticmethod
    def match_magic(cursor: pparse.Cursor):
        return False

    
    def __init__(self, source: pparse.Extraction, id: str):
        super().__init__(source, id)

        source = self.source()
        self.json_extn = pparse.BytesExtraction(name=source.name(), reader=source.open())


    def _scan_children(self):
        try:
            # TODO: Determine a better way to manage the parser registry.
            parser_reg = {'safetensors': LazySafetensorsParser,}
            for extraction in self.source()._extractions:
                extraction.discover_parsers(parser_reg).scan_data()
        except pparse.EndOfDataException:
            log.debug("END OF DATA")
            pass
        except Exception as e:
            log.debug(e)
            import traceback
            traceback.print_exc()

    
    def scan_data(self):

        try:
            # Do JSON parse and save its result
            # NOTE: Assuming the parent of this parser is not also doing JSON.
            self.json_extn.discover_parsers({'json': LazyJsonParser}).scan_data()
            self.source()._result[self._id] = self.json_extn._result['json']

            shard_files = {}
            for entry in self.json_extn._result['json'].value.value['weight_map'].value.values():
                shard_files[entry] = True
            shard_files = shard_files.keys()

            # TODO: Can this be more clean?
            idx_prefix = pathlib.Path(self.source().name()).parents[0]

            # Add the shard files as children extractions.
            for shard_file in shard_files:
                shard_fpath = str(idx_prefix.joinpath(shard_file))
                shard_data = pparse.Data(path=shard_fpath)
                shard_range = pparse.Range(shard_data.open(), shard_data.length)
                shard_extn = pparse.BytesExtraction(name=shard_file, reader=shard_range)
                self.source()._extractions.append(shard_extn)

            
        except pparse.EndOfNodeException as e:
            pass
        except pparse.EndOfDataException as e:
            pass
        except pparse.UnsupportedFormatException:
            raise

        # Scan all the extractions.
        self._scan_children()

        log.debug("DONE SCANNING CHILDREN")

        # TODO: Consider traversing all tensors in safetensors and creating
        # nodes that point to tensor data in the original Data

        return self