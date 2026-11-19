"""Cache behavior.counts for every capture: beh_cache.json {replay_id: {player: counts}}"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import behavior
DIRS = ['/mnt/user-data/uploads/data', '/mnt/user-data/uploads/SF6-Claude-Coaching/replays']
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'beh_cache.json')
cache = {}
for d in DIRS:
    for f in sorted(os.listdir(d)):
        if f.endswith('.json') and len(f) == 14 and f[:9].isalnum() and f[:9] not in cache:
            try: cache[f[:9]] = behavior.counts(os.path.join(d, f))
            except Exception as e: print('skip', f, e)
json.dump(cache, open(out, 'w'))
print(len(cache), 'replays')
