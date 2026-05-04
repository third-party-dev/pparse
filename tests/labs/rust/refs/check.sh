#!/bin/sh

cargo check --color always 2>&1 | head -n 50
