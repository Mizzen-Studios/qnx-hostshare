import json,re
from pathlib import Path
p=Path('docs/acceptance/sdk-gate-20261112');a=[json.loads(x) for x in (p/'memory-series.jsonl').read_text().splitlines()]
first,last=a[0],a[-1]
for s in a:
 s['executable_anon_resident']=sum(m.get('Anonymous',0) for m in s['largest_other_anonymous'] if 'rwxp' in m['mapping'])
summary={'samples':len(a),'first':{k:first[k] for k in ['time','rss_bytes','ram_resident_bytes','other_anonymous_bytes','executable_anon_resident']},'last':{k:last[k] for k in ['time','ready','rss_bytes','ram_resident_bytes','other_anonymous_bytes','executable_anon_resident']},'peak_cgroup_bytes':max(int(s['memory']['memory.peak']) for s in a),'unique_scope_pids':sorted({v['pid'] for s in a for v in s['processes']}),'interpretation':'QMP pc.ram HVA confirms guest512MiB mapping. A ~1GiB rwxp anonymous mapping grows; QMP info jit independently shows generated code growth. Strong evidence TCG translation cache is a major non-guest-RAM growth contributor; residual allocator ownership and difference from Nov10 remain unproven. No claim that all anonymous memory is TCG.'}
for name in ['qmp-memory-early.json','qmp-memory.json']:
 d=json.loads((p/name).read_text());m=re.search(r'gen code size\s+(\d+)/(\d+)',d['info jit']['return']);summary[name]={'generated_code_bytes':int(m[1]),'capacity_bytes':int(m[2])} if m else None
(p/'analysis.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
