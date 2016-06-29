#!/usr/bin/env python

import sys
import json

data = json.load(sys.stdin)
output = data["check"]["output"]

if "Last check execution was" not in output:
  sys.stdout.write(output)
sys.exit(0)