import os,json,time,subprocess,selectors,fcntl,hashlib,re,argparse
from pathlib import Path
parser=argparse.ArgumentParser(description='Read-only native smoke run; no qtest or routing writes.')
parser.add_argument('--irq-mode',choices=['pci-line','msix'],default='pci-line')
parser.add_argument('--run-id',required=True)
options=parser.parse_args()
root=Path(__file__).resolve().parents[1];base=Path(os.environ.get('HS_RECEIPT_BASE',str(root/'.local/user-runs')));base.mkdir(parents=True,exist_ok=True)
assert re.fullmatch(r'[A-Za-z0-9_-]+',options.run_id)
out=base/options.run_id;out.mkdir(exist_ok=False)
lock=open('/home/ubuntu/qnx-host/native-test.lock','a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
assert subprocess.run(['pgrep','-f','^qemu-system-'],stdout=subprocess.DEVNULL).returncode==1
cg=Path('/sys/fs/cgroup')/next(x.split(':',2)[2].strip().lstrip('/') for x in Path('/proc/self/cgroup').read_text().splitlines() if x.startswith('0::'))
caps={k:(cg/k).read_text().strip() for k in ['cpu.max','memory.max','memory.swap.max']};assert caps=={'cpu.max':'100000 100000','memory.max':'1073741824','memory.swap.max':'0'} and os.getpriority(os.PRIO_PROCESS,0)>=15
shared=Path('/home/ubuntu/qnx-host/guest/shared');image=Path(os.environ['HS_IFS']);disk=Path(os.environ['HS_DISK']);elf=Path(os.environ['HS_ELF'])
corpus=root/'.local/irq-restart-20261113/corpus';corpus.mkdir(parents=True,exist_ok=True)
(corpus/'hello.txt').write_text('HostShare F0 public synthetic test only.\n')
args=['qemu-system-x86_64','-machine','pc,accel=tcg','-cpu','max','-smp','1','-m','512','-display','none','-serial','stdio','-monitor','none','-no-reboot','-kernel',str(image),'-drive','file='+str(disk)+',format=raw,if=ide,snapshot=on','-nic','user,model=virtio-net-pci','-fsdev','local,id=f0,path='+str(corpus)+',security_model=none,readonly=on','-device','virtio-9p-pci,fsdev=f0,mount_tag=f0test,disable-legacy=on']
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'status':'FAIL','source_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'caps':caps,'command':args,'image_sha256':h(image),'disk_sha256':h(disk),'elf_sha256':h(elf),'native_source_sha256':h(root/'native/qnx_hostshare.c'),'source_files':{str(p.relative_to(root)):h(p) for p in list((root/'native').glob('*.[ch]'))+list((root/'core').glob('*.[ch]'))},'corpus_sha256':h(corpus/'hello.txt'),'image_provenance':'external prebuilt, NOT clean stock','native_exit_rc':None,'commands':[]}
r=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);sel=selectors.DefaultSelector();sel.register(r.stdout,selectors.EVENT_READ);serial=bytearray()
def until(marker,timeout=90,start=0):
 end=time.monotonic()+timeout
 while time.monotonic()<end:
  mem=int((cg/'memory.current').read_text());events=(cg/'memory.events').read_text()
  if mem+67108864>int(caps['memory.max']) or any(line.split()[0] in ('oom','oom_kill') and int(line.split()[1]) for line in events.splitlines()):raise MemoryError('native reserve/OOM: '+str(mem)+' '+events)
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
 (root/'.local/irq-restart-20261113/readback.bin').write_bytes(observed)
 # Do not commit executable bytes embedded in serial.
 del serial[start:];serial.extend(b'[OWN ELF READBACK REDACTED; byte comparison in receipt]'+bytes([10]))
 if not verified:raise RuntimeError('native ELF readback byte mismatch: '+str(len(observed)))
 mode='--'+options.irq_mode
 report['irq_routing_mutated']=False;report['qtest']=False
 text=command('/data/home/root/hostshare '+mode+'; echo HOSTSHARE_APP_RC=$?; echo PROBE_DONE','PROBE_DONE',60)
 (out/'probe.txt').write_text(text)
 m=re.search(r'^HOSTSHARE_APP_RC=(\d+)$',text.replace(chr(13),''),re.M)
 report['n1c']={'passed':bool(m and int(m[1])==0 and 'HOSTSHARE F2 READONLY BYTE_EXACT PASS' in text),'app_rc':int(m[1]) if m else None,'mode':options.irq_mode}
 if report['n1c']['passed']:
  text=command('/data/home/root/hostshare '+mode+' --mount > /data/home/root/mount.log 2>&1 & HS_PID=$!; echo HS_PID=$HS_PID; sleep 2; cat /data/home/root/mount.log; cat /mnt/host/hello.txt; echo MOUNT_CAT_RC=$?; ls -1 /mnt/host; echo MOUNT_DONE','MOUNT_DONE',60)
  (out/'mount.txt').write_text(text);report['mount']={'passed':'HostShare F0 public synthetic test only.' in text.replace(chr(13),'').splitlines() and '\nMOUNT_CAT_RC=0' in text}
  text=command('kill -KILL $HS_PID; wait $HS_PID; echo KILL_WAIT_RC=$?; cat /data/home/root/mount.log; cat /mnt/host/hello.txt; echo AFTER_STOP_RC=$?; echo STOP_DONE','STOP_DONE',60)
  (out/'stop.txt').write_text(text);report['n5_stop']={'passed':bool(re.search(r'^KILL_WAIT_RC=[1-9][0-9]*$',text.replace(chr(13),''),re.M)) and bool(re.search(r'^AFTER_STOP_RC=[1-9][0-9]*$',text.replace(chr(13),''),re.M)),'signal':'SIGKILL after idle completed reads. No DMA quiesce by killed process; remounter resets. No active/in-flight crash safety claim.'}
  text=command('/data/home/root/hostshare '+mode+' --mount-drop > /data/home/root/drop.log 2>&1 & HS_DROP_PID=$!; echo HS_DROP_PID=$HS_DROP_PID; sleep 2; cat /data/home/root/drop.log; cat /mnt/host/hello.txt; echo DROP_CAT_RC=$?; /data/home/root/hostshare --checksum /mnt/host/hello.txt; echo DROP_CHECK_RC=$?; pidin -p $HS_DROP_PID info; echo DROP_DONE','DROP_DONE',60)
  (out/'drop.txt').write_text(text);report['n5_drop_remount']={'passed':'HostShare F0 public synthetic test only.' in text.replace(chr(13),'').splitlines() and '\nDROP_CAT_RC=0' in text and '\nDROP_CHECK_RC=0' in text and 'HOSTSHARE PRIVILEGE uid=65534 euid=65534' in text and bool(re.search(r'^HOSTSHARE CHECKSUM 838956572 41 /mnt/host/hello.txt$',text.replace(chr(13),''),re.M)),'least_privilege_scope':'exact ability drops and IO reacquire denial only, not a security audit'}
  text=command('kill -TERM $HS_DROP_PID; wait $HS_DROP_PID; echo DROP_TERM_RC=$?; cat /data/home/root/drop.log; echo FINAL_DONE','FINAL_DONE',60)
  (out/'drop-stop.txt').write_text(text);report['drop_cleanup']={'passed':'\nDROP_TERM_RC=0' in text and 'HOSTSHARE MOUNT TERM_DETACHED' in text}
 report['status']='PASS_DEFAULT_ROUTE_MOUNT_RESTART_DROP' if report['n1c']['passed'] and all(report.get(k,{}).get('passed') for k in ['mount','n5_stop','n5_drop_remount','drop_cleanup']) else 'FAIL_BOUNDED_GATE'
except Exception as e:report['error']=repr(e)
finally:
 r.terminate()
 try:r.wait(10)
 except subprocess.TimeoutExpired:r.kill();r.wait()
 report['qemu_exit_rc']=r.returncode;report['stopped_reaped']=True;report['memory_events']=(cg/'memory.events').read_text();report['memory_peak']=(cg/'memory.peak').read_text()
 (root/('.local/irq-restart-20261113/'+options.run_id+'-serial-raw.txt')).write_bytes(serial)
 (out/'serial.txt').write_text(re.sub(r"printf '%b' '[^']*' >> /data/home/root/hostshare",'[OWN ELF COPY REDACTED]',serial.decode(errors='replace')))
 (out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report),flush=True)
raise SystemExit(0 if report['status']=='PASS_DEFAULT_ROUTE_MOUNT_RESTART_DROP' else 1)
