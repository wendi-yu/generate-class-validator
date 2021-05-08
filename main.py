import sys

import class_validator as val

if len(sys.argv) != 2:
    exit(
        f"script expects one argument, the path to the desired file. Received {len(sys.argv) - 1}.")

fpath = sys.argv[1]

print(val.build(fpath))
