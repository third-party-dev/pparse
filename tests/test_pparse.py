#!/usr/bin/env python3

from importlib import resources
import logging

log = logging.getLogger(__name__)

def test_init():
    path = resources.files("tests.data.models.gpt2").joinpath("sample.txt")
    log.info(path)