import builtins
import sys

import debugpy
from micropython import * 

# Listen on all interfaces so that it works in Docker
debugpy.listen(("0.0.0.0", 5678))
print("Waiting for debugger attach on 0.0.0.0:5678")
debugpy.wait_for_client()


# builtins.const = const  # type: ignore

script_path = sys.argv[1]
with open(script_path, "r") as f:
    code = f.read()

# Compile allows source code traceability when in debug mode
exec(compile(code, script_path, "exec"), globals())  # pylint: disable=all
