import fcntl,subprocess,time,json,os
from pathlib import Path
root=Path(__file__).resolve().parents[1];out=root/'docs/acceptance/mount-20261113';control=root/'.local/mount-20261113';guest=Path('/home/ubuntu/qnx-host/guest');ctl=str(guest/'guestctl-capped.py')
lock=open('/home/ubuntu/qnx-host/native-test.lock','a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
assert not list((guest/'shared/queue').glob('*.sh'))
assert subprocess.run(['pgrep','-f','^qemu-system-'],stdout=subprocess.DEVNULL).returncode==1
assert not (out/'BOOT_STARTED').exists()
(out/'BOOT_STARTED').write_text(str(time.time()));r={'status':'RUNNING','boot_attempts':1,'reserve_bytes':67108864};child=None;cg=None;pid=None;samples=[]
try:
 env=os.environ.copy();env['CAN_SDK_MEMORY_MIB']='512'
 child=subprocess.Popen(['python3',ctl,'start'],env=env,stdout=open(out/'sdk-launch.log','w'),stderr=subprocess.STDOUT)
 begin=time.monotonic()
 while time.monotonic()-begin<2400:
  if child.poll() is not None:raise RuntimeError('SDK exited')
  try:
   if pid is None:
    p=int((guest/'qemu.pid').read_text());cmd=Path('/proc/%s/cmdline'%p).read_bytes()
    if b'tb-size=256' not in cmd:time.sleep(1);continue
    pid=p;cg=Path('/sys/fs/cgroup')/next(x.split(':',2)[2].strip().lstrip('/') for x in Path('/proc/%s/cgroup'%pid).read_text().splitlines() if x.startswith('0::'))
    r.update(pid=pid,cmdline=cmd.replace(bytes([0]),b' ').decode(),nice=os.getpriority(os.PRIO_PROCESS,pid),caps={k:(cg/k).read_text().strip() for k in ['cpu.max','memory.max','memory.swap.max']})
    assert r['caps']=={'cpu.max':'100000 100000','memory.max':'2147483648','memory.swap.max':'0'} and r['nice']==15
   s={'time':time.time(),'ready':(guest/'shared/ready').exists(),'memory':{k:(cg/k).read_text().strip() for k in ['memory.current','memory.peak','memory.stat','memory.events','memory.swap.current']},'processes':(cg/'cgroup.procs').read_text(),'qemu_status':Path('/proc/%s/status'%pid).read_text()};samples.append(s)
   with open(out/'sdk-memory.jsonl','a') as f:f.write(json.dumps(s)+'\n')
   if int(s['memory']['memory.current'])+67108864>2147483648:raise MemoryError('reserve')
   if 'oom_kill 0' not in s['memory']['memory.events']:raise MemoryError('OOM')
   if s['ready']:
    (control/'SDK_READY').write_text(str(time.time()))
   if (control/'STOP').exists():r['status']='REQUESTED_STOP';break
   if time.monotonic()-begin>600 and not s['ready']:raise TimeoutError('SDK boot not ready600s')
  except FileNotFoundError:pass
  time.sleep(2)
 else:r['status']='OWNERSHIP_DEADLINE_STOP'
except Exception as e:r['status']='FAIL';r['error']=repr(e)
finally:
 if child:
  if child.poll() is None:
   try:r['stop_rc']=subprocess.run(['python3',ctl,'stop'],stdout=open(out/'sdk-stop.log','w'),stderr=subprocess.STDOUT,timeout=150).returncode
   except Exception as e:r['stop_error']=repr(e)
  try:r['owner_child_rc']=child.wait(timeout=30)
  except Exception as e:r['reap_error']=repr(e)
 r['samples']=len(samples);r['peak_cgroup_bytes']=max([int(s['memory']['memory.peak']) for s in samples] or [0]);r['stopped_reaped']=child is not None and child.poll() is not None
 (out/'sdk-owner.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r),flush=True)
