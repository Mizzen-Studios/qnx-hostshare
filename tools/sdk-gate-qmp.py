import socket,json
from pathlib import Path
out=Path('docs/acceptance/sdk-gate-20261112/qmp-memory.json')
with socket.socket(socket.AF_UNIX) as s:
 s.settimeout(10);s.connect('/home/ubuntu/qnx-host/guest/qmp.sock');f=s.makefile('rwb',buffering=0);greeting=json.loads(f.readline())
 def call(obj):
  f.write((json.dumps(obj)+'\n').encode())
  while True:
   r=json.loads(f.readline())
   if 'return' in r or 'error' in r:return r
 call({'execute':'qmp_capabilities'});result={}
 for name in ['info jit','info ramblock','info mtree -f']:
  result[name]=call({'execute':'human-monitor-command','arguments':{'command-line':name}})
 out.write_text(json.dumps(result,indent=2)+'\n')
