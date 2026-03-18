#!/usr/bin/env bash

export PROJ_PATH=$(realpath $(dirname $0)/..)
cd ${PROJ_PATH}

pytest --log-cli-level=INFO
