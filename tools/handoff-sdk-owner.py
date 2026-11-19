"""One bounded SDK compile attempt; lease retained through STOP/reap. No image build."""
import fcntl,hashlib,json,os,shutil,subprocess,time
from pathlib import Path
root=Path(__file__).resolve().parents[1]
out=root/'.local/developer-handoff-20261119-build2';out.mkdir(parents=True,exist_ok=False)
guest=Path('/home/ubuntu/qnx-host/guest');ctl=guest/'guestctl-capped.py'
shared=guest/'shared/hostshare-handoff-20261119-build2'
r={'schema':'hostshare.handoff-build.v1','native_accepted':False,'reserve_bytes':67108864,'status':'PREFLIGHT'}
lock=open('/home/ubuntu/qnx-host/native-test.lock','a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
child=None;pid=None;cg=None;job=None
try:
 r['foreign_qemu']=subprocess.run(['pgrep','-af','^qemu-system-'],capture_output=True,text=True).stdout
 r['pending_queue']=[p.name for p in (guest/'shared/queue').glob('*.sh')]
 r['running_markers']=[p.name for p in (guest/'shared/queue').glob('*.running')]
 # running markers survive dead SDK jobs; preserve, do not requeue/delete them.
 r['host_memavailable_kib']=next(int(s.split()[1]) for s in Path('/proc/meminfo').read_text().splitlines() if s.startswith('MemAvailable:'))
 if r['host_memavailable_kib']<2162688:raise MemoryError('host headroom below2GiB+reserve64')
 if r['foreign_qemu'] or r['pending_queue']:raise RuntimeError('foreign QEMU or pending queue')
 shared.mkdir(exist_ok=False)
 for folder in ('core','native'):shutil.copytree(root/folder,shared/'source'/folder)
 script=out/'compile.sh'
 script.write_text('#!/bin/bash\nset -eo pipefail\nexport HOME=/home/qnx\nsource /home/qnx/qnx800/qnxsdp-env.sh >/dev/null\ns=/mnt/host/hostshare-handoff-20261119-build2/source\no=/mnt/host/hostshare-handoff-20261119-build2/build\nmkdir "$o"\nqcc -Vgcc_ntox86_64 -std=gnu11 -O0 -g0 -Wall -Wextra -Werror -Wno-misleading-indentation -I"$s/core" "$s/native/qnx_hostshare.c" "$s/native/mount_checksum.c" "$s/native/conformance.c" "$s/core/transport.c" "$s/core/protocol.c" -o "$o/qnx_hostshare" -lpci\nsha256sum "$o/qnx_hostshare"\n')
 env=os.environ.copy();env['EDU_SDK_MEMORY_MIB']='1024'
 child=subprocess.Popen(['python3',str(ctl),'start'],env=env,stdout=open(out/'launch.txt','w'),stderr=subprocess.STDOUT)
 start=time.monotonic()
 while time.monotonic()-start<900:
  if child.poll() is not None:raise RuntimeError('SDK exited before compile completion')
  try:
   if pid is None:
    candidate=int((guest/'qemu.pid').read_text());cmd=Path('/proc/%d/cmdline'%candidate).read_bytes();pid=candidate
    if b'tb-size=256' not in cmd:pid=None;time.sleep(1);continue
    cg=Path('/sys/fs/cgroup')/next(s.split(':',2)[2].strip().lstrip('/') for s in Path('/proc/%d/cgroup'%pid).read_text().splitlines() if s.startswith('0::'))
    r['caps']={k:(cg/k).read_text().strip() for k in ('cpu.max','memory.max','memory.swap.max')};r['nice']=os.getpriority(os.PRIO_PROCESS,pid);r['qemu_command']=cmd.replace(b'\0',b' ').decode()
    assert r['caps']=={'cpu.max':'100000 100000','memory.max':'2147483648','memory.swap.max':'0'} and r['nice']==15
   current=int((cg/'memory.current').read_text());events=(cg/'memory.events').read_text()
   sample={'current':current,'peak':int((cg/'memory.peak').read_text()),'events':events,'time':time.time()}
   with open(out/'memory.jsonl','a') as f:f.write(json.dumps(sample)+'\n')
   if current+67108864>2147483648:raise MemoryError('reserve64 breach: current='+str(current))
   if any(s.split()[0] in ('oom','oom_kill') and int(s.split()[1]) for s in events.splitlines()):raise MemoryError('OOM event')
   if (guest/'shared/ready').exists() and job is None:
    job=subprocess.Popen(['python3',str(ctl),'exec',str(script),'600'],stdout=open(out/'compile.txt','w'),stderr=subprocess.STDOUT)
   if job is not None and job.poll() is not None:
    r['compile_rc']=job.returncode
    if job.returncode:raise RuntimeError('compile failed or queue timeout; original job retained')
    elf=shared/'build/qnx_hostshare';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    files={str(p.relative_to(root)):h(p) for folder in ('core','native') for p in (root/folder).glob('*.[ch]')}
    for name in files:assert h(shared/'source'/name)==files[name]
    binding={'files':files,'elf_sha256':h(elf)}
    (out/'build-source-hashes.json').write_text(json.dumps(binding,indent=2)+'\n');r['elf_sha256']=h(elf);r['status']='BUILD_PASS';break
  except FileNotFoundError:
   if cg is None:pid=None
  time.sleep(1)
 else:raise TimeoutError('SDK attempt deadline')
except Exception as e:r['status']='BLOCKED';r['blocker']=repr(e)
finally:
 if child and child.poll() is None:
  try:r['stop_rc']=subprocess.run(['python3',str(ctl),'stop'],stdout=open(out/'stop.txt','w'),stderr=subprocess.STDOUT,timeout=150).returncode
  except Exception as e:r['stop_error']=repr(e)
 if child:
  try:r['owner_rc']=child.wait(timeout=30)
  except Exception as e:r['reap_error']=repr(e)
 if job:
  try:job.wait(timeout=5)
  except subprocess.TimeoutExpired:job.terminate();job.wait()
 r['stopped_reaped']=child is None or child.poll() is not None
 r['remaining_qemu']=subprocess.run(['pgrep','-af','^qemu-system-'],capture_output=True,text=True).stdout
 (out/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
 fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
print(json.dumps(r),flush=True)
