"""One owned SDK boot. No retry; bounded monitor and mandatory cleanup."""
import fcntl,json,os,subprocess,time,re,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1];out=root/'docs/acceptance/sdk-gate-20261112';local=root/'.local/sdk-gate-20261112'
guest=Path('/home/ubuntu/qnx-host/guest');ctl=str(guest/'guestctl-capped.py')
lock=open('/home/ubuntu/qnx-host/native-test.lock','a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
assert subprocess.run(['pgrep','-f','^qemu-system-'],stdout=subprocess.DEVNULL).returncode==1
assert not list((guest/'shared/queue').glob('*.sh'))
assert not (out/'BOOT_STARTED').exists(),'one boot already consumed'
report={'source_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'controller_sha256':hashlib.sha256(Path(ctl).read_bytes()).hexdigest(),'boot_attempts':1,'reserve_bytes':67108864,'start_command':['python3',ctl,'start'],'inventory':'NOT_RUN','native':'NOT_RUN','status':'RUNNING'}
serial_offset=(guest/'serial.log').stat().st_size
samples=[];child=None;pid=None;cg=None

def sample():
 global pid,cg
 if pid is None:
  try:
   p=int((guest/'qemu.pid').read_text());cmd=Path('/proc/%s/cmdline'%p).read_bytes()
   if b'qemu-system' not in cmd:return
   pid=p;cg=Path('/sys/fs/cgroup')/next(x.split(':',2)[2].strip().lstrip('/') for x in Path('/proc/%s/cgroup'%pid).read_text().splitlines() if x.startswith('0::'))
   report.update(qemu_pid=pid,cmdline=cmd.replace(bytes([0]),b' ').decode(),nice=os.getpriority(os.PRIO_PROCESS,pid),cgroup=str(cg))
   report['effective_caps']={k:(cg/k).read_text().strip() for k in ['cpu.max','memory.max','memory.swap.max']}
   assert report['effective_caps']=={'cpu.max':'100000 100000','memory.max':'2147483648','memory.swap.max':'0'}
   assert report['nice']==15 and '-m 512 ' in report['cmdline'] and '-smp 1 ' in report['cmdline']
  except FileNotFoundError:return
 if not Path('/proc/%s'%pid).exists():return
 s={'time':time.time(),'ready':(guest/'shared/ready').exists(),'memory':{},'processes':[]}
 for k in ['memory.current','memory.peak','memory.stat','memory.events','memory.swap.current']:
  s['memory'][k]=(cg/k).read_text()
 for f in [cg,*[x for x in cg.rglob('*') if x.is_dir()]]:
  try:ids=(f/'cgroup.procs').read_text().split()
  except OSError:continue
  for p in ids:
   try:
    status=Path('/proc/'+p+'/status').read_text();s['processes'].append({'pid':int(p),'cmdline':Path('/proc/'+p+'/cmdline').read_bytes().replace(bytes([0]),b' ').decode(),'status':status})
   except OSError:pass
 smaps=Path('/proc/%s/smaps'%pid).read_text();maps=[];current=None
 for line in smaps.splitlines():
  if re.match(r'^[0-9a-f]+-[0-9a-f]+ ',line):
   current={'mapping':line};maps.append(current)
  elif current is not None:
   m=re.match(r'^(Size|Rss|Anonymous|AnonHugePages|Private_Dirty):\s+(\d+) kB',line)
   if m:current[m[1]]=int(m[2])*1024
 ram=[m for m in maps if m.get('Size')==536870912 and m['mapping'].split()[1]=='rw-p']
 s['ram_candidates']=ram;s['rss_bytes']=sum(m.get('Rss',0) for m in maps);s['anonymous_bytes']=sum(m.get('Anonymous',0) for m in maps)
 s['ram_resident_bytes']=sum(m.get('Rss',0) for m in ram);s['other_anonymous_bytes']=s['anonymous_bytes']-sum(m.get('Anonymous',0) for m in ram)
 s['largest_other_anonymous']=sorted([m for m in maps if m not in ram],key=lambda m:m.get('Anonymous',0),reverse=True)[:8]
 s['host_meminfo']=Path('/proc/meminfo').read_text();samples.append(s)
 with open(out/'memory-series.jsonl','a') as f:f.write(json.dumps(s)+'\n')
 # Full maps kept outside git; no SDK content.
 (local/'last-smaps.txt').write_text(smaps)
 if int(s['memory']['memory.current'])+67108864>2147483648:raise MemoryError('64MiB reserve exhausted')
 if 'oom_kill 0' not in s['memory']['memory.events']:raise MemoryError('OOM event')

try:
 (out/'BOOT_STARTED').write_text(str(time.time()))
 env=os.environ.copy();env['CAN_SDK_MEMORY_MIB']='512'
 child=subprocess.Popen(['python3',ctl,'start'],env=env,stdout=open(out/'launch.log','w'),stderr=subprocess.STDOUT)
 deadline=time.monotonic()+420;ready_at=None
 while time.monotonic()<deadline:
  sample()
  if child.poll() is not None:raise RuntimeError('SDK owner exited before gate')
  if (guest/'shared/ready').exists():
   if ready_at is None:ready_at=time.monotonic();report['boot_ready']=True
   if time.monotonic()-ready_at>=20:break
  time.sleep(2)
 if not ready_at:raise TimeoutError('SDK never ready')
 # No inference that anonymous mappings are TCG cache. Unattributed growth is
 # explicitly unclear and fails the inventory gate pending parent review.
 last=samples[-1]
 report['growth_diagnosis']={'ram_mapping_candidates':len(last['ram_candidates']),'ram_resident_bytes':last['ram_resident_bytes'],'other_anonymous_bytes':last['other_anonymous_bytes'],'interpretation':'Smaps separates candidate guest RAM from other anonymous allocations; allocator/TCG ownership of other anonymous mappings is not proven.'}
 report['status']='STOP_GROWTH_CAUSE_UNCLEAR'
except Exception as e:report['status']='STOP_FAILURE';report['error']=repr(e)
finally:
 try:
  if child and child.poll() is None:
   report['stop_command']=['python3',ctl,'stop'];r=subprocess.run(report['stop_command'],stdout=open(out/'stop.log','w'),stderr=subprocess.STDOUT,timeout=150);report['stop_rc']=r.returncode
  if child:report['owner_child_rc']=child.wait(timeout=30)
 except Exception as e:report['cleanup_error']=repr(e)
 report['samples']=len(samples)
 if samples:
  report['peak_sample_current_bytes']=max(int(s['memory']['memory.current']) for s in samples)
  report['peak_cgroup_bytes']=max(int(s['memory']['memory.peak']) for s in samples)
  report['last_events']=samples[-1]['memory']['memory.events']
 data=(guest/'serial.log').read_bytes();(out/'serial.txt').write_bytes(data[serial_offset:] if len(data)>=serial_offset else data)
 report['pgrep_exit_code']=subprocess.run(['pgrep','-f','^qemu-system-'],stdout=open(out/'remaining-qemu.txt','w')).returncode
 report['stopped_reaped']=child is not None and child.poll() is not None
 (out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report),flush=True)
