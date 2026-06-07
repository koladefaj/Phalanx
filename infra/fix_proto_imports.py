"""Fix bare pb2 imports in generated gRPC stubs.

grpc_tools.protoc emits `import foo_pb2 as foo__pb2` which breaks when the
generated files are installed inside the aegis_shared package. This script
rewrites those imports to the fully-qualified form so they resolve correctly
both locally and inside Docker containers.

Run automatically by `make proto`.
"""
import re
import pathlib

GEN_DIR = pathlib.Path(__file__).parent.parent / "shared" / "aegis_shared" / "generated"
PATTERN = re.compile(r"^import (\w+_pb2) as (\w+)$", re.MULTILINE)
REPLACEMENT = r"from aegis_shared.generated import \1 as \2"

for grpc_file in GEN_DIR.glob("*_pb2*.py"):
    original = grpc_file.read_text()
    fixed = PATTERN.sub(REPLACEMENT, original)
    if fixed != original:
        grpc_file.write_text(fixed)
        print(f"  fixed imports: {grpc_file.name}")
