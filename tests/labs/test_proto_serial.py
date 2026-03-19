#!/usr/bin/env python3

"""
Serialize a Person protobuf message using only the compiled person.pb descriptor.
No generated *_pb2.py files needed.

Prerequisites:
    protoc --descriptor_set_out=person.pb --include_imports person.proto
    
    pip install "protobuf==6.33.0"
"""

from google.protobuf import descriptor_pool, descriptor_pb2, message_factory


def load_descriptor(pb_path: str, message_name: str):
    """Load a message class dynamically from a .pb descriptor file."""
    with open(pb_path, "rb") as f:
        file_descriptor_set = descriptor_pb2.FileDescriptorSet.FromString(f.read())

    pool = descriptor_pool.DescriptorPool()
    for file_proto in file_descriptor_set.file:
        pool.Add(file_proto)

    descriptor = pool.FindMessageTypeByName(message_name)
    return message_factory.GetMessageClass(descriptor)


def main():

    # ModelDef = load_descriptor("ge.pb", "ge.proto.ModelDef")
    # # or any other message:
    # OpDef    = load_descriptor("ge.pb", "ge.proto.OpDef")
    # GraphDef = load_descriptor("ge.pb", "ge.proto.GraphDef")

    Person = load_descriptor("person.pb", "Person")

    # --- Serialize ---
    person = Person(
        name="Alice",
        age=30,
        emails=["alice@example.com", "alice@work.com"],
    )
    serialized: bytes = person.SerializeToString()
    print(f"Serialized {len(serialized)} bytes: {serialized.hex()}")

    # Optionally write to a binary file
    with open("person.bin", "wb") as f:
        f.write(serialized)
    print("Written to person.bin")

    # --- Deserialize ---
    person2 = Person()
    person2.ParseFromString(serialized)
    print(f"Round-tripped -> name={person2.name!r}, age={person2.age}, emails={list(person2.emails)}")


if __name__ == "__main__":
    main()