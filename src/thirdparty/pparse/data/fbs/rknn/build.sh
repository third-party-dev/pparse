#!/usr/bin/env bash

flatc -o . --binary --schema schema.fbs
flatc -o . --strict-json --json ../reflection.fbs -- ./schema.bfbs

