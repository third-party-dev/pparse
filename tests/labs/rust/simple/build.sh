# Install rust:
# curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh


# debug build — fast compile, slow binary
cargo build
./target/debug/myapp

# release build — slow compile, small fast binary
cargo build --release
./target/release/myapp

# check exit code
echo $?


# cargo build --release
# ls -lh target/release/myapp