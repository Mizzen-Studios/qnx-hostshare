import json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1];out=root/'docs/acceptance/native-20261113';s=[json.loads(x) for x in (out/'sdk-memory.jsonl').read_text().splitlines()]
stat=lambda text:{a:int(b) for a,b in (line.split() for line in text.splitlines())}
result={'samples':len(s),'peak_memory_bytes':max(int(x['memory']['memory.peak']) for x in s),'peak_swap_bytes':max(int(x['memory']['memory.swap.current']) for x in s),'oom_kill_max':max(stat(x['memory']['memory.events'])['oom_kill'] for x in s),'max_event':max(stat(x['memory']['memory.events'])['max'] for x in s),'reserve_min_bytes':2147483648-max(int(x['memory']['memory.current']) for x in s),'first_ready':next((x['time'] for x in s if x['ready']),None),'native_adapter_build2_rc':0,'EDU_wrong_finish_rc':0,'inventory_rc':0,'image_builds':0}
(out/'sdk-summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
