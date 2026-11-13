import os,json,time,subprocess,selectors,fcntl,hashlib,re
from pathlib import Path
root=Path(__file__).resolve().parents[1];base=root/'docs/acceptance/native-20261113';out=base/'attempt2';out.mkdir(exist_ok=False)
lock=open('/home/ubuntu/qnx-host/native-test.lock','a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
assert subprocess.run(['pgrep','-f','^qemu-system-'],stdout=subprocess.DEVNULL).returncode==1
cg=Path('/sys/fs/cgroup')/next(x.split(':',2)[2].strip().lstrip('/') for x in Path('/proc/self/cgroup').read_text().splitlines() if x.startswith('0::'))
caps={k:(cg/k).read_text().strip() for k in ['cpu.max','memory.max','memory.swap.max']};assert caps=={'cpu.max':'100000 100000','memory.max':'1073741824','memory.swap.max':'0'} and os.getpriority(os.PRIO_PROCESS,0)>=15
shared=Path('/home/ubuntu/qnx-host/guest/shared');image=shared/'incident-20261108/incident.ifs';disk=shared/'qnx-native/disk-qemu';elf=shared/'hostshare-native-20261113/build2/qnx_hostshare'
corpus=root/'.local/native-20261113/corpus';corpus.mkdir(exist_ok=True);(corpus/'hello.txt').write_text('HostShare F0 public synthetic test only.\n')
args=['qemu-system-x86_64','-machine','pc,accel=tcg','-cpu','max','-smp','1','-m','512','-display','none','-serial','stdio','-monitor','none','-no-reboot','-kernel',str(image),'-drive','file='+str(disk)+',format=raw,if=ide,snapshot=on','-nic','user,model=virtio-net-pci','-fsdev','local,id=f0,path='+str(corpus)+',security_model=none,readonly=on','-device','virtio-9p-pci,fsdev=f0,mount_tag=f0test,disable-legacy=on']
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'status':'FAIL','source_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'caps':caps,'command':args,'image_sha256':h(image),'disk_sha256':h(disk),'elf_sha256':h(elf),'native_source_sha256':h(root/'native/qnx_hostshare.c'),'corpus_sha256':h(corpus/'hello.txt'),'prebuilt_source_record':(shared/'incident-20261108/source-commit').read_text().strip(),'native_exit_rc':None,'commands':[]}
r=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);sel=selectors.DefaultSelector();sel.register(r.stdout,selectors.EVENT_READ);serial=bytearray()
def until(marker,timeout=90,start=0):
 end=time.monotonic()+timeout
 while time.monotonic()<end:
  if sel.select(.02):
   b=os.read(r.stdout.fileno(),65536)
   if not b:raise RuntimeError('QEMU exit '+str(r.poll()))
   serial.extend(b);(out/'serial.txt').write_bytes(serial)
  if marker in bytes(serial[start:]).replace(bytes([13]),b'').split(bytes([10])):return bytes(serial[start:]).decode(errors='replace')
 raise TimeoutError(marker.decode())
def command(cmd,marker,timeout=30,record=True):
 start=len(serial)
 if record:report['commands'].append(cmd)
 payload=(cmd+chr(10)).encode()
 for at in range(0,len(payload),96):r.stdin.write(payload[at:at+96]);r.stdin.flush();time.sleep(.01)
 return until(marker.encode(),timeout,start)
try:
 until(b'CANOPY_SLM_IMAGE_READY',180)
 command('uname -a; pidin ar; pci-tool -v; echo PROBE_BASE_DONE','PROBE_BASE_DONE')
 command(': > /data/home/root/hostshare; echo COPY_READY','COPY_READY')
 data=elf.read_bytes()
 for i in range(0,len(data),128):
  escaped=''.join(chr(92)+'0'+format(v,'03o') for v in data[i:i+128]);marker='COPY_'+str(i)
  command("printf '%b' '"+escaped+"' >> /data/home/root/hostshare; echo "+marker,marker,20,False)
 report['copy_route']='ksh builtin printf %b octal chunks128 to snapshot data volume; no image build';report['copy_bytes']=len(data)
 start=len(serial)
 command('chmod 700 /data/home/root/hostshare; echo HS_BINARY_BEGIN; cat /data/home/root/hostshare; echo; echo HS_BINARY_END','HS_BINARY_END',30)
 raw=bytes(serial[start:]);begin=raw.index(b'HS_BINARY_BEGIN'+bytes([13,10]))+len(b'HS_BINARY_BEGIN')+2;end=raw.rindex(bytes([13,10])+b'HS_BINARY_END');observed=raw[begin:end]
 # The explicit echo after cat contributes one terminal newline.
 if observed.endswith(bytes([13,10])):observed=observed[:-2]
 expected=data.replace(bytes([10]),bytes([13,10]))
 verified=observed==data or observed==expected
 report['native_copy_byte_exact']=verified;report['copy_verification']='readback cat bytes compared to ELF with explicit tty ONLCR transformation; no target hash utility required'
 (root/'.local/native-20261113/native-readback.bin').write_bytes(observed)
 # Do not commit executable bytes embedded in serial.
 del serial[start:];serial.extend(b'[OWN ELF READBACK REDACTED; byte comparison in receipt]'+bytes([10]))
 if not verified:raise RuntimeError('native ELF readback byte mismatch: '+str(len(observed)))
 text=command('/data/home/root/hostshare; echo HOSTSHARE_APP_RC=$?; echo HOSTSHARE_GATE_DONE','HOSTSHARE_GATE_DONE',60)
 (out/'probe.txt').write_text(text);m=re.search(r'^HOSTSHARE_APP_RC=(\d+)$',text.replace(chr(13),''),re.M)
 report['native_exit_rc']=int(m[1]) if m else None
 if report['native_exit_rc']==0 and 'HOSTSHARE F2 READONLY BYTE_EXACT PASS' in text and 'HOSTSHARE IRQ_PULSE' in text:report['status']='PASS_NATIVE_READONLY_IRQ_PULSE'
except Exception as e:report['error']=repr(e)
finally:
 r.terminate()
 try:r.wait(10)
 except subprocess.TimeoutExpired:r.kill();r.wait()
 report['qemu_exit_rc']=r.returncode;report['stopped_reaped']=True;report['memory_events']=(cg/'memory.events').read_text();report['memory_peak']=(cg/'memory.peak').read_text();(out/'serial.txt').write_bytes(serial);(out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report),flush=True)
