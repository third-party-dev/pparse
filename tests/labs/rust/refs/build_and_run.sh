#!/usr/bin/env bash

# Install rust:
# curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh


# debug build — fast compile, slow binary
cargo build
./target/debug/reftests

# release build — slow compile, small fast binary
# cargo build --release
# ./target/release/reftests

# check exit code
echo $?


# cargo build --release
# ls -lh target/release/myapp