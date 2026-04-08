#!/usr/bin/env python3

import logging
import struct

log = logging.getLogger(__name__)

import thirdparty.pparse.lib as pparse


class SafetensorsIndexParsingState(object):
    def parse_data(self, node: pparse.Node):
        raise NotImplementedError()


class SafetensorsIndexParsingComplete(SafetensorsIndexParsingState):
    def parse_data(self, node: pparse.Node):
        return pparse.ASCEND


class SafetensorsIndexParsingTensors(SafetensorsIndexParsingState):
    def parse_data(self, node: pparse.Node):
        ctx = node.ctx()
        parser = ctx.parser()

        node._value['tensors'] = {}
        for stfname in node._value['stfiles']:
            tensors = node._value['stfiles'][stfname].value['header'].value.value
            tensor_data = node._value['stfiles'][stfname]._value['tensors']
            for tname in tensors:
                if tname == "__metadata__":
                    continue
                node._value['tensors'][tname] = {}
                node._value['tensors'][tname]['header'] = tensors[tname]
                node._value['tensors'][tname]['data'] = tensor_data[tname]

        ctx._next_state(SafetensorsIndexParsingComplete)
        return pparse.ASCEND


class SafetensorsIndexParsingShards(SafetensorsIndexParsingState):
    def parse_data(self, node: pparse.Node):
        ctx = node.ctx()
        parser = ctx.parser()

        from thirdparty.pparse.lazy.safetensors import Parser as LazySafeTensorsParser

        # ! Super hacky way to get path to the weight_map files.
        from pathlib import Path
        prefix = Path(parser._root.ctx().reader().cursor()._data._path).parent

        weight_map = node.value['index'].value.value['weight_map'].value
        for tname in weight_map:
            st_fpath = str(prefix / weight_map[tname])
            st_parser = LazySafeTensorsParser.from_fpath(st_fpath, parent=node)
            node._value.setdefault('stfiles', {})[st_fpath] = st_parser._root
            ctx._descendants.append(st_parser._root)

        ctx._next_state(SafetensorsIndexParsingTensors)
        return pparse.AGAIN


class SafetensorsIndexParsingIndex(SafetensorsIndexParsingState):
    def parse_data(self, node: pparse.Node):
        ctx = node.ctx()
        parser = ctx.parser()

        from thirdparty.pparse.lazy.json import Parser as LazyJsonParser
        json_parser = LazyJsonParser.from_reader(node.ctx().reader(), parent=node)

        node._value['index'] = json_parser._root
        node.ctx()._descendants.append(json_parser._root)

        ctx._next_state(SafetensorsIndexParsingShards)

        return pparse.AGAIN
