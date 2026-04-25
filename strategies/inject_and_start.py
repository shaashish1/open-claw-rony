"""
Inject strategies into OpenAlgo's Python runner and start them.
Run inside the container: python3 /tmp/inject_and_start.py
"""
import sys, os, json, shutil
from pathlib import Path
from datetime import datetime

os.chdir('/app')
sys.path.insert(0, '/app')

# Copy strategies to OpenAlgo's scripts directory
scripts_dir = Path('/app/strategies/scripts')
scripts_dir.mkdir(parents=True, exist_ok=True)

yukti_dir = Path('/app/strategies/yukti')
strategies = sorted(yukti_dir.glob('strategy_*.py'))

print(f"Found {len(strategies)} strategies to inject")

# Load or create config file
config_file = Path('/app/strategies/strategy_configs.json')
if config_file.exists():
    with open(config_file) as f:
        configs = json.load(f)
else:
    configs = {}

API_KEY = os.getenv('OPENALGO_API_KEY', '')

new_ids = []
for strat_file in strategies:
    # Copy to scripts dir
    dest = scripts_dir / strat_file.name
    shutil.copy2(strat_file, dest)
    
    strategy_id = strat_file.stem  # e.g. strategy_01
    
    # Create config entry
    configs[strategy_id] = {
        'name': strategy_id,
        'filename': strat_file.name,
        'user_id': 'ashish.sharma14@gmail.com',
        'created_at': datetime.now().isoformat(),
        'exchange': 'NSE',
        'start_time': '09:15',
        'stop_time': '15:15',
        'squareoff_time': '15:10',
        'is_active': True,
        'trading_days': 'MON,TUE,WED,THU,FRI',
        'status': 'stopped'
    }
    new_ids.append(strategy_id)
    print(f"  Injected: {strategy_id} -> {dest}")

# Save config
with open(config_file, 'w') as f:
    json.dump(configs, f, indent=2)
print(f"\nConfig saved: {config_file}")

# Now start each strategy using OpenAlgo's start_strategy_process
try:
    from blueprints.python_strategy import start_strategy_process, RUNNING_STRATEGIES, ensure_directories
    ensure_directories()
    
    print(f"\nStarting {len(new_ids)} strategies via OpenAlgo runner...")
    for sid in new_ids:
        try:
            result = start_strategy_process(sid)
            print(f"  {sid}: {result}")
        except Exception as e:
            print(f"  {sid} ERROR: {e}")
    
    import time
    time.sleep(5)
    print(f"\nRunning strategies: {list(RUNNING_STRATEGIES.keys())}")
    
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback: launch directly
    import subprocess
    logs_dir = Path('/app/log/strategies')
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    env = os.environ.copy()
    env['OPENALGO_API_KEY'] = API_KEY
    env['HOST_SERVER'] = 'http://127.0.0.1:5000'
    env['WEBSOCKET_URL'] = 'ws://127.0.0.1:8765'
    
    procs = []
    for sid in new_ids:
        script = scripts_dir / f'{sid}.py'
        log_path = logs_dir / f'{sid}.log'
        with open(log_path, 'w') as logf:
            p = subprocess.Popen(
                [sys.executable, str(script)],
                env=env,
                stdout=logf,
                stderr=subprocess.STDOUT,
            )
            procs.append((sid, p.pid))
            print(f"  Started {sid} -> PID {p.pid}")
    
    import time; time.sleep(8)
    for sid, pid in procs:
        log_path = logs_dir / f'{sid}.log'
        try:
            lines = log_path.read_text().strip().split('\n')[-3:]
            print(f"\n--- {sid} ---\n" + '\n'.join(lines))
        except:
            pass
