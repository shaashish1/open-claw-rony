import sys, os
sys.path.insert(0, '/app')
os.chdir('/app')
from blueprints.python_strategy import RUNNING_STRATEGIES
print('running_count:', len(RUNNING_STRATEGIES))
for k, v in RUNNING_STRATEGIES.items():
    print(f'  {k}: pid={v.get("pid","?")}')
