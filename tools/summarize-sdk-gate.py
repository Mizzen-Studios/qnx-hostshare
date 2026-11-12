import json
from pathlib import Path
p=Path('docs/acceptance/sdk-gate-20261112')
a=[json.loads(s) for s in (p/'memory-series.jsonl').read_text().splitlines()]
for s in [a[0],a[-1]]:
 print(json.dumps({k:s[k] for k in ['time','ready','rss_bytes','anonymous_bytes','ram_resident_bytes','other_anonymous_bytes','ram_candidates','largest_other_anonymous']}))
print('samples',len(a))
