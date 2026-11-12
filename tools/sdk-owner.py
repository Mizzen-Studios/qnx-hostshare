import fcntl, subprocess, time, json, os
from pathlib import Path
root=Path(__file__).resolve().parents[1]; out=root/'docs/acceptance/f0'
lock=open('/home/ubuntu/qnx-host/native-test.lock','a'); fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
ctl='/home/ubuntu/qnx-host/guest/guestctl-capped.py'
child=None; report={}
try:
 assert not list(Path('/home/ubuntu/qnx-host/guest/shared/queue').glob('*.sh')), 'pending trusted queue'
 env=os.environ.copy(); env.pop('CAN_SDK_MEMORY_MIB',None)
 child=subprocess.Popen(['python3',ctl,'start'],env=env,stdout=open(out/'sdk-launch.log','w'),stderr=subprocess.STDOUT)
 deadline=time.monotonic()+300
 while not Path('/home/ubuntu/qnx-host/guest/shared/ready').exists():
  if child.poll() is not None: raise RuntimeError('SDK exited before ready')
  if time.monotonic()>deadline: raise TimeoutError('SDK ready')
  time.sleep(2)
 pid=int(Path('/home/ubuntu/qnx-host/guest/qemu.pid').read_text())
 cg=Path('/sys/fs/cgroup')/next(x.split(':',2)[2].strip().lstrip('/') for x in Path('/proc/%s/cgroup'%pid).read_text().splitlines() if x.startswith('0::'))
 report['caps']={k:(cg/k).read_text().strip() for k in ['cpu.max','memory.max','memory.swap.max']}; report['qemu_pid']=pid
 report['cmdline']=Path('/proc/%s/cmdline'%pid).read_bytes().replace(b'\0',b' ').decode()
 assert report['caps']=={'cpu.max':'100000 100000','memory.max':'1073741824','memory.swap.max':'0'}
 r=subprocess.run(['python3',ctl,'exec',str(root/'tools/sdk-inventory.sh'),'300'],stdout=open(out/'sdk-inventory.log','w'),stderr=subprocess.STDOUT,timeout=310)
 report['inventory_rc']=r.returncode
finally:
 r=subprocess.run(['python3',ctl,'stop'],stdout=open(out/'sdk-stop.log','w'),stderr=subprocess.STDOUT,timeout=150); report['stop_rc']=r.returncode
 if child: report['owner_child_rc']=child.wait(timeout=30)
 report['stopped_reaped']=True
 (out/'sdk-owner.json').write_text(json.dumps(report,indent=2))
