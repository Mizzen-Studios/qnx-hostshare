import os,subprocess,fcntl,time,json,selectors,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1]; out=root/'docs/acceptance/f0'
lock=open('/home/ubuntu/qnx-host/native-test.lock','a'); fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
assert not subprocess.check_output(['pgrep','-f','^qemu-system-']).strip() if subprocess.run(['pgrep','-f','^qemu-system-'],stdout=subprocess.DEVNULL).returncode==0 else True
cg=Path('/sys/fs/cgroup')/next(x.split(':',2)[2].strip().lstrip('/') for x in Path('/proc/self/cgroup').read_text().splitlines() if x.startswith('0::'))
caps={k:(cg/k).read_text().strip() for k in ['cpu.max','memory.max','memory.swap.max']}
assert caps=={'cpu.max':'100000 100000','memory.max':'1073741824','memory.swap.max':'0'}
assert os.getpriority(os.PRIO_PROCESS,0)>=15
shared=Path('/home/ubuntu/qnx-host/guest/shared')
image=shared/'incident-20261108/incident.ifs';disk=shared/'qnx-native/disk-qemu'
corpus=root/'.local/f0-corpus';corpus.mkdir(parents=True,exist_ok=True);(corpus/'hello.txt').write_text('HostShare F0 public synthetic test only.\n')
args=['qemu-system-x86_64','-machine','pc,accel=tcg','-cpu','max','-smp','1','-m','512','-display','none','-serial','stdio','-monitor','none','-no-reboot','-kernel',str(image),'-drive','file='+str(disk)+',format=raw,if=ide,snapshot=on','-nic','user,model=virtio-net-pci','-fsdev','local,id=f0,path='+str(corpus)+',security_model=none,readonly=on','-device','virtio-9p-pci,fsdev=f0,mount_tag=f0test']
report={'caps':caps,'nice':os.getpriority(os.PRIO_PROCESS,0),'command':args,'image':str(image),'image_sha256':hashlib.sha256(image.read_bytes()).hexdigest(),'disk':str(disk),'disk_sha256':hashlib.sha256(disk.read_bytes()).hexdigest(),'prebuilt_source_sha':(shared/'incident-20261108/source-commit').read_text().strip(),'elf_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (shared/'incident-20261108').iterdir() if p.name in ['incident_recorder','prereq_containment','ability_lesson']},'native_enumeration':'NOT_RUN','status':'FAIL'}
r=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);report['qemu_pid']=r.pid; sel=selectors.DefaultSelector();sel.register(r.stdout,selectors.EVENT_READ);serial=bytearray()
def until(marker,timeout):
 end=time.monotonic()+timeout
 while time.monotonic()<end:
  if sel.select(.1):
   b=os.read(r.stdout.fileno(),65536)
   if not b:raise RuntimeError('QEMU exited '+str(r.poll()))
   serial.extend(b);(out/'native-serial.txt').write_bytes(serial)
  if marker in serial:return
 raise TimeoutError(marker.decode())
try:
 until(b'CANOPY_SLM_IMAGE_READY',180)
 cmd='echo F0_NATIVE_BEGIN; uname -a; pidin ar; ls /proc/boot/*pci*; pci-tool -v; echo PCI_TOOL_RC=$?; pci -v; echo PCI_RC=$?; echo F0_NATIVE_DONE'
 report['guest_command']=cmd
 for i in range(0,len(cmd)+1,80):r.stdin.write((cmd+chr(10))[i:i+80].encode());r.stdin.flush();time.sleep(.05)
 until(b'F0_NATIVE_DONE\r\n',60)
 report['native_enumeration']='CAPTURED_REVIEW_REQUIRED';report['status']='CAPTURED'
except Exception as e:report['error']=str(e)
finally:
 r.terminate()
 try:r.wait(10)
 except subprocess.TimeoutExpired:r.kill();r.wait()
 report['exit_rc']=r.returncode;report['stopped_reaped']=True;(out/'native-serial.txt').write_bytes(serial);(out/'native.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
