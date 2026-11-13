from pathlib import Path
import hashlib,json,socket,shutil
r=Path(__file__).resolve().parents[1];base=r/'docs/acceptance/irq-restart-20261113';shared=Path('/home/ubuntu/qnx-host/guest/shared/hostshare-irq-restart-20261113')
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files={}
for folder in ['core','native']:
 for p in (r/folder).glob('*.[ch]'):
  assert p.read_bytes()==(shared/'source'/folder/p.name).read_bytes();files[str(p.relative_to(r))]=h(p)
(base/'build-source-hashes.json').write_text(json.dumps({'files':files,'elf_sha256':h(shared/'build1/qnx_hostshare'),'installed_headers':{p.name:h(p) for p in (shared/'private').glob('*') if p.is_file()}},indent=2)+'\n')
shutil.copy2(r/'.local/irq-restart-20261113/build1.log',base/'build1.log')
with socket.socket(socket.AF_UNIX) as s:
 s.settimeout(10);s.connect('/home/ubuntu/qnx-host/guest/qmp.sock');f=s.makefile('rwb',buffering=0);f.readline()
 def call(obj):
  f.write((json.dumps(obj)+'\n').encode())
  while True:
   row=json.loads(f.readline())
   if 'return' in row or 'error' in row:return row
 call({'execute':'qmp_capabilities'})
 result=call({'execute':'human-monitor-command','arguments':{'command-line':'info jit'}})
 (base/'sdk-qmp-jit.json').write_text(json.dumps(result,indent=2)+'\n')
(r/'.local/irq-restart-20261113/STOP').touch()
print('SOURCE_BOUND_STOP_REQUESTED')
