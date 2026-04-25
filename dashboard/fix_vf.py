#!/usr/bin/env python3
"""Fix the cut vf.py by closing JS string and appending output write, then run it."""
import os, subprocess

with open('/tmp/vf.py', 'r') as f:
    src = f.read()

# Find where the JS string got cut - it ends at the last complete JS line
cut = src.rfind('\nasync function loadSprint')
if cut < 0:
    cut = src.rfind('\nfunction renderTasks')
if cut < 0:
    print("Can't find cut point")
    exit(1)

src_fixed = src[:cut] + '''
"""

with open(OUT, 'a') as f:
    f.write(JS)

print('Part 1 HTML written, size:', os.path.getsize(OUT))
'''

with open('/tmp/vf_fixed.py', 'w') as f:
    f.write(src_fixed)

print("vf_fixed.py written, running it now...")
ret = subprocess.run(['python3', '/tmp/vf_fixed.py'], capture_output=True, text=True)
print(ret.stdout)
if ret.stderr:
    print("STDERR:", ret.stderr[:500])
