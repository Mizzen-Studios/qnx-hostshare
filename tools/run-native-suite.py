"""Bounded native readonly suite; explicit image kind, no IRQ routing changes."""
import argparse,base64,fcntl,hashlib,json,os,re,select,selectors,subprocess,time
from pathlib import Path
from handoff_oracle import verify as verify_conformance
from handoff_preflight import config
from recording_transport import match_lines,redact_payload_commands
from serial_readback import transfer,parse_readback
import boot_handoff
import importlib.util
_dev_spec=importlib.util.spec_from_file_location("dev_loop",Path(__file__).with_name("dev-loop.py"));dev_loop=importlib.util.module_from_spec(_dev_spec);_dev_spec.loader.exec_module(dev_loop)
from stock_pin import load_stock_pin,HISTORICAL_STOCK,verify_stock_files
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--boot-stage',choices=['prepare','verify'])
p.add_argument('--boot-overlay',type=Path)
p.add_argument('--boot-pin',type=Path)
p.add_argument('--dev-app',type=Path)
p.add_argument('--dev-manifest',type=Path)
p.add_argument('--conformance',action='store_true')
p.add_argument('--tag',default='f0test')
p.add_argument('--mountpoint',default='/mnt/host')
p.add_argument('--run-id',required=True)
p.add_argument('--image-kind',required=True,choices=['historical','stock'])
p.add_argument('--midread',action='store_true',help='Explicit diagnostic pause with client blocked in read, then SIGKILL. Not in-flight DMA.')
p.add_argument('--stock-pin',type=Path,help='Strict JSON SHA256 pins for independently built stock IFS/disk')
o=p.parse_args();config(o.tag,o.mountpoint)
assert re.fullmatch(r'[A-Za-z0-9_-]+',o.run_id)
if o.conformance and o.midread:p.error('--conformance is independent of the legacy death diagnostic')
if o.stock_pin and o.image_kind!='stock':p.error('--stock-pin requires --image-kind stock')
if o.boot_stage and (o.image_kind!='stock' or o.midread or not o.boot_overlay):p.error('boot stages require stock, overlay and no death lane')
if not o.boot_stage and any((o.boot_overlay,o.boot_pin,o.dev_app,o.dev_manifest)):p.error('boot-only options require boot stage')
if o.boot_stage=='verify' and not all((o.boot_pin,o.dev_app,o.dev_manifest,o.conformance)):p.error('verify requires boot pin, built client and conformance')
stock_expected=load_stock_pin(o.stock_pin) if o.stock_pin else HISTORICAL_STOCK
root=Path(__file__).resolve().parents[1]
base=Path(os.environ.get('HS_RECEIPT_BASE',str(root/'.local/user-runs'))).resolve()
assert base==root or root in base.parents,'receipts must remain workspace-local'
base.mkdir(parents=True,exist_ok=True);out=base/o.run_id;out.mkdir(exist_ok=False)
h=lambda q:hashlib.sha256(q.read_bytes()).hexdigest()
elf=Path(os.environ['HS_ELF']);image=Path(os.environ['HS_IFS']);disk=Path(os.environ['HS_DISK'])
build=json.loads(Path(os.environ['HS_BUILD_MANIFEST']).read_text())
assert h(elf)==build['elf_sha256']
assert set(build['files'])=={str(q.relative_to(root)) for folder in ('core','native') for q in (root/folder).glob('*.[ch]')}
for name,digest in build['files'].items():assert h(root/name)==digest,name
assert not subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True).strip(),'Launch requires clean checkout'
assert all(q.is_file() and not q.is_symlink() for q in (elf,image,disk)),'regular artifact files required'
vendor=json.loads((root/'tools/recording_transport/PIN.json').read_text())
assert h(root/'tools/recording_transport/__init__.py')==vendor['sha256'],'shared transport vendor mismatch'
if o.image_kind=='stock':
 expected=stock_expected
 verify_stock_files(image,disk,expected)
lock=open(os.environ.get('HS_LOCK','/home/ubuntu/qnx-host/native-test.lock'),'a')
if os.environ.get('HS_PARENT_LEASE_PID'):
 owner=int(os.environ['HS_PARENT_LEASE_PID'])
 assert Path('/proc/%d/cmdline'%owner).read_bytes().split(b'\0')[1:2]==[str(root/'tools/handoff-sdk-owner.py').encode()] or Path('/proc/%d/cmdline'%owner).read_bytes().split(b'\0')[1:2]==[b'tools/handoff-sdk-owner.py'],'unexpected lease owner'
 # Prove a live exclusive lease still exists; never silently bypass a free lock.
 try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 except BlockingIOError:pass
 else:raise RuntimeError('parent lease not held')
else:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
assert subprocess.run(['pgrep','-f','^qemu-system-'],stdout=subprocess.DEVNULL).returncode==1
available=next(int(x.split()[1]) for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:'))
assert available>=2162688,'host headroom below2GiB+reserve64'
queue=Path('/home/ubuntu/qnx-host/guest/shared/queue')
assert not list(queue.glob('*.sh')),'pending SDK jobs'
if o.boot_stage and root not in o.boot_overlay.absolute().parents:raise ValueError('overlay must remain workspace-local')
if o.boot_stage=='prepare':boot_handoff.create_overlay(o.boot_overlay,disk)
if o.boot_stage=='verify':
 boot_handoff.validate_pin(o.boot_overlay,o.boot_pin,disk,elf,o.tag,o.mountpoint)
 dev_build=dev_loop.validate(o.dev_app,o.dev_manifest,root)
cg=Path('/sys/fs/cgroup')/next(x.split(':',2)[2].strip().lstrip('/') for x in Path('/proc/self/cgroup').read_text().splitlines() if x.startswith('0::'))
caps={k:(cg/k).read_text().strip() for k in ['cpu.max','memory.max','memory.swap.max']}
assert caps=={'cpu.max':'100000 100000','memory.max':'2147483648','memory.swap.max':'0'} and os.getpriority(os.PRIO_PROCESS,0)>=15
corpus=root/'.local'/('corpus-'+o.run_id);corpus.mkdir(parents=True,exist_ok=False)
contents={'hello.txt':b'HostShare F0 public synthetic test only.\n','empty':b'','one':b'x','4KiB':bytes(range(256))*16,'1MiB':bytes(range(256))*4096,'nested/leaf.txt':b'nested actual read\n','unicode-λ.txt':'UTF-8 λ 雪\n'.encode()}
# Preserve original seven-file corpus exactly, including Unicode file content.
record=json.loads((root/'docs/acceptance/mount-20261113/corpus.json').read_text())
# Every generated byte is independently checked against the earlier corpus manifest.
for name,data in contents.items():
 q=corpus/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(data)
manifest={name:{'sha256':h(corpus/name),'size':(corpus/name).stat().st_size,'posix_cksum':int(subprocess.check_output(['cksum',str(corpus/name)],text=True).split()[0])} for name in contents}
assert manifest==record,('synthetic corpus differs',manifest)
if o.conformance:
 for i in range(180):(corpus/('page-%03d.txt'%i)).write_bytes(('page %d\n'%i).encode())
if o.boot_stage=='verify':
 (corpus/'loop-app').write_bytes(o.dev_app.read_bytes())
 loop_input=b'HostShare boot-mounted developer loop verified.\n';(corpus/'loop-input.txt').write_bytes(loop_input)
(out/'corpus-before.json').write_text(json.dumps(manifest,indent=2)+'\n')
args=['qemu-system-x86_64','-machine','pc','-accel','tcg,tb-size=256','-cpu','max','-smp','1','-m','512','-display','none','-serial','stdio','-monitor','none','-no-reboot','-kernel',str(image),'-drive','file='+str(disk)+',format=raw,if=ide,snapshot=on']
if o.boot_stage:
 args[args.index('-drive')+1]='file='+str(o.boot_overlay)+',format=qcow2,if=ide,snapshot=off'
# Explicit documented device topology, not a mid-run rerouting/fallback.
args+=['-nic','none','-device','virtio-rng-pci'] if o.image_kind=='stock' else ['-nic','user,model=virtio-net-pci']
args+=['-fsdev','local,id=f0,path='+str(corpus)+',security_model=none,readonly=on','-device','virtio-9p-pci,fsdev=f0,mount_tag='+o.tag+',disable-legacy=on']
report={'transport_vendor':vendor,'transport_contract':'hs-exact-readback-v1','transfer_budget_seconds':900,'startup_budget_seconds':180,'readback_budget_seconds':60,'conformance_budget_seconds':240,'status':'FAIL','source_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'clean_checkout':True,'caps':caps,'nice':os.getpriority(os.PRIO_PROCESS,0),'command':args,'image_kind':o.image_kind,'image_sha256':h(image),'disk_sha256':h(disk),'elf_sha256':h(elf),'source_files':build['files'],'qtest':False,'irq_routing_mutated':False,'commands':[],'boot_stage':o.boot_stage,'boot_overlay_sha256_before':boot_handoff.digest(o.boot_overlay) if o.boot_stage else None,'handoff':{'tag':o.tag,'mountpoint':o.mountpoint,'conformance_requested':o.conformance},'reserve_bytes':67108864}
(out/'started.json').write_text(json.dumps(report,indent=2)+'\n')
rawpath=root/'.local'/('suite-'+o.run_id+'-raw.bin')
# Private append-only RX/TX events may contain OWN ELF bytes. Never publish these.
eventlog=open(out/'serial-events-private.jsonl','a',buffering=1)
def event(value):
 eventlog.write(json.dumps(value)+'\n');eventlog.flush();os.fsync(eventlog.fileno())

r=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);sel=selectors.DefaultSelector();sel.register(r.stdout,selectors.EVENT_READ);serial=bytearray();samples=[];binary_window=None
def drain(timeout=.05):
 mem=int((cg/'memory.current').read_text());events=(cg/'memory.events').read_text()
 samples.append({'time':time.time(),'current':mem,'peak':int((cg/'memory.peak').read_text()),'events':events})
 if mem+67108864>2147483648 or any(line.split()[0] in ('max','oom','oom_kill') and int(line.split()[1]) for line in events.splitlines()):raise MemoryError('native reserve/events')
 if sel.select(timeout):
  b=os.read(r.stdout.fileno(),65536)
  if not b:raise RuntimeError('QEMU exited '+str(r.poll()))
  event({'event':'rx','mono':time.monotonic(),'raw_b64':base64.b64encode(b).decode()})
  serial.extend(b)
def until(marker,timeout=60,start=0):
 end=time.monotonic()+timeout
 while time.monotonic()<end:
  drain(min(.05,max(0,end-time.monotonic())))
  if marker in match_lines(bytes(serial[start:])):return bytes(serial[start:]).decode(errors='replace')
 raise TimeoutError(marker.decode())
def command(cmd,marker,timeout=60,record=True):
 cmd=cmd.replace('/mnt/host',o.mountpoint)
 start=len(serial)
 if record:report['commands'].append(cmd)
 payload=(cmd+'\n').encode()
 for at in range(0,len(payload),96):r.stdin.write(payload[at:at+96]);r.stdin.flush();event({'event':'tx','mono':time.monotonic(),'raw_b64':base64.b64encode(payload[at:at+96]).decode()});time.sleep(.01)
 return until(marker.encode(),timeout,start)
def save(name,text):
 (out/(name+'.txt')).write_text(text)
 return text.replace('\r','')
def rc(text,key):
 m=re.search(r'^'+re.escape(key)+r'=(\d+)$',text.replace('\r',''),re.M)
 return int(m[1]) if m else None
guest='/data/hostshare';app='/boot/hsd' if o.boot_stage else guest+'/hostshare'
try:
 startup_end=time.monotonic()+180
 if o.boot_stage=='verify':
  # Passive observation: no host serial command is sent to trigger mounting.
  boot_text=until(('HOSTSHARE MOUNT READY '+o.mountpoint+' READONLY').encode(),max(0,startup_end-time.monotonic()))
  save('boot-autostart',boot_text);report['boot_mount']={'ready_before_any_host_command':True,'hook_sha256':boot_handoff.digest(root/'tools/boot_handoff.py'),'transparent_restart':False}
 # Cold stock has no CANOPY marker: prove shell by exact standalone echo, no SSH/login repair.
 end=startup_end;last=0
 while time.monotonic()<end:
  drain(.1)
  if time.monotonic()-last>5:
   r.stdin.write(b'echo HS_SUITE_BOOT_READY\n');r.stdin.flush();event({'event':'tx','mono':time.monotonic(),'raw_b64':base64.b64encode(b'echo HS_SUITE_BOOT_READY\n').decode()});last=time.monotonic()
  if b'HS_SUITE_BOOT_READY' in bytes(serial).replace(b'\r',b'').split(b'\n'):break
 else:raise TimeoutError('serial shell not ready180s')
 save('boot',command('uname -a; mkdir -p '+guest+'; stty -echo; echo HS_PREPARED','HS_PREPARED'))
 data=elf.read_bytes()
 def exchange(wire,marker,timeout):
  start=len(serial);deadline=time.monotonic()+timeout;offset=0
  os.set_blocking(r.stdin.fileno(),False)
  try:
   while offset<len(wire):
    remaining=deadline-time.monotonic()
    if remaining<=0:raise TimeoutError('transfer write deadline')
    if not select.select([],[r.stdin],[],min(.05,remaining))[1]:
     drain(0);continue
    try:n=os.write(r.stdin.fileno(),wire[offset:offset+96])
    except BlockingIOError:continue
    if n<=0:raise RuntimeError('closed serial write')
    event({'event':'transfer_tx','mono':time.monotonic(),'raw_b64':base64.b64encode(wire[offset:offset+n]).decode()})
    offset+=n;drain(min(.01,max(0,deadline-time.monotonic())))
   reply=until(marker,max(0,deadline-time.monotonic()),start)
   # One bounded quiet drain catches duplicates already queued after the ack.
   drain(min(.02,max(0,deadline-time.monotonic())))
   return bytes(serial[start:])
  finally:os.set_blocking(r.stdin.fileno(),True)
 def readback(destination,timeout):
  global binary_window
  nonce=os.urandom(16).hex();begin=('HB_BEGIN_'+nonce).encode();end=('HB_END_'+nonce).encode();done='HB_DONE_'+nonce;status='HB_RC_'+nonce
  start=len(serial);binary_window=start
  text=command("printf '\\n%s\\n' '"+begin.decode()+"'; od -An -v -tx1 "+destination+'; HB_RESULT=$?; echo '+end.decode()+'; echo '+status+'=$HB_RESULT; echo '+done,done,timeout,record=False)
  if rc(text,status)!=0:raise RuntimeError('guest od unavailable/failed')
  observed=parse_readback(text.encode(),begin,end)
  del serial[start:];serial.extend(b'[OWN ELF READBACK REDACTED; bytes captured]\n');binary_window=None
  return observed
 if o.boot_stage=='prepare':
  text=save('boot-slot',command('[ ! -e /boot/hsd ] && [ ! -L /boot/hsd ] && [ ! -e /boot/onboot ] && [ ! -L /boot/onboot ]; echo SLOT_RC=$?; echo SLOT_DONE','SLOT_DONE'))
  if rc(text,'SLOT_RC')!=0:raise RuntimeError('existing boot payload/hook collision; not replaced')
 if o.boot_stage!='verify':
  report['transfer']=transfer(data,app,exchange,event,readback=readback,chunk_bytes=64,timeout=20,budget=900)
  observed=readback(app,60);assert observed==data,'ELF byte mismatch'
  report['native_copy_byte_exact']=True;report['copy_bytes']=len(data)
  report['transfer_route']='ack octal64; actual guest od byte comparison; host SHA256 (no guest hash applet)'
  text=save('exec-mode',command('chmod 700 '+app+'; echo EXEC_MODE_RC=$?; echo HS_EXEC_MODE_READY','HS_EXEC_MODE_READY'))
  if rc(text,'EXEC_MODE_RC')!=0:raise RuntimeError('verified ELF permissions failed')
 if o.boot_stage=='prepare':
  script=boot_handoff.hook(o.tag,o.mountpoint)
  report['boot_hook_transfer']=transfer(script,'/boot/onboot',exchange,event,readback=readback,chunk_bytes=64,timeout=20,budget=120)
  text=save('boot-seal',command('umount /boot; echo BOOT_SEAL_RC=$?; echo BOOT_SEAL_DONE','BOOT_SEAL_DONE'))
  if rc(text,'BOOT_SEAL_RC')!=0:raise RuntimeError('boot filesystem not sealed')
  report['status']='PASS_BOOT_PREPARED'
 else:
  if o.boot_stage=='verify':
   # No second adapter/probe: do not reset the queue of the boot-mounted server.
   report['probe']={'status':'NOT_RUN_BOOT_SERVER_ACTIVE','scope':'boot mount/read replaces standalone PCI probe'}
   text=save('mount',boot_text+command('HS_PID=$(cat /dev/shmem/hs-boot.pid); cat /mnt/host/hello.txt; echo CAT_RC=$?; ls -1 /mnt/host; echo LS_RC=$?; echo MOUNT_DONE','MOUNT_DONE'))
  else:
   text=save('probe',command(app+' --tag '+o.tag+' --pci-line; echo APP_RC=$?; echo PROBE_DONE','PROBE_DONE'))
   report['probe']={'passed':rc(text,'APP_RC')==0 and 'HOSTSHARE F2 READONLY BYTE_EXACT PASS' in text}
   if not report['probe']['passed']:raise RuntimeError('default-route probe failed; no routing fallback')
   text=save('mount',command(app+' --tag '+o.tag+' --mountpoint '+o.mountpoint+' --pci-line --mount > '+guest+'/mount.log 2>&1 & HS_PID=$!; sleep 10; pidin ar; cat '+guest+'/mount.log; cat /mnt/host/hello.txt; echo CAT_RC=$?; ls -1 /mnt/host; echo LS_RC=$?; echo MOUNT_DONE','MOUNT_DONE'))
  listing=re.sub(rb'\\([0-7]{3})',lambda m:bytes([int(m[1],8)]),text.encode()).decode('utf-8')
  report['mount']={'passed':rc(text,'CAT_RC')==0 and rc(text,'LS_RC')==0 and 'HOSTSHARE MOUNT READY' in text and all(name in listing.splitlines() for name in ['hello.txt','empty','one','4KiB','1MiB','nested','unicode-λ.txt'])}
  if not report['mount']['passed']:raise RuntimeError('mount/list gate failed')
  report['corpus']={}
  for name,expected in manifest.items():
   text=save('checksum-'+name.replace('/','_'),command(app+" --checksum '/mnt/host/"+name+"'; echo CHECK_RC=$?; echo CHECK_DONE",'CHECK_DONE',240))
   m=re.search(r'^HOSTSHARE CHECKSUM (\d+) (\d+) ',text,re.M)
   report['corpus'][name]={'passed':bool(m and int(m[1])==expected['posix_cksum'] and int(m[2])==expected['size'] and rc(text,'CHECK_RC')==0),'observed_cksum':int(m[1]) if m else None,'observed_size':int(m[2]) if m else None}
  if o.conformance:
   before={str(q.relative_to(corpus)):h(q) for q in corpus.rglob('*') if q.is_file()}
   text=save('conformance',command(app+' --conformance '+o.mountpoint+'; echo CONFORMANCE_RC=$?; echo CONFORMANCE_DONE','CONFORMANCE_DONE',240))
   report['conformance']=verify_conformance(text,corpus)
   assert rc(text,'CONFORMANCE_RC')==0
   assert before=={str(q.relative_to(corpus)):h(q) for q in corpus.rglob('*') if q.is_file()},'mutation changed host corpus'
   report['conformance']['host_corpus_unchanged']=True
   report['conformance']['pagination_corpus_entries']=len(list(corpus.iterdir()))
  changed=b'HostShare host edit observed without rebuild.\n';(corpus/'hello.txt').write_bytes(changed);start_edit=time.monotonic()
  text=save('host-edit',command('cat /mnt/host/hello.txt; echo EDIT_RC=$?; echo EDIT_DONE','EDIT_DONE'))
  report['host_edit']={'passed':changed.decode().strip() in text.splitlines() and rc(text,'EDIT_RC')==0,'elapsed_seconds':time.monotonic()-start_edit,'sha256':h(corpus/'hello.txt'),'rebuild':False}
  text=save('readonly',command('echo forbidden > /mnt/host/hello.txt; echo WRITE_RC=$?; echo WRITE_DONE','WRITE_DONE'))
  report['readonly']={'passed':rc(text,'WRITE_RC') not in (None,0) and (corpus/'hello.txt').read_bytes()==changed}
  if o.boot_stage=='verify':
   copied=guest+'/loop-app'
   text=save('developer-copy',command('cat '+o.mountpoint+'/loop-app > '+copied+'; echo LOOP_COPY_RC=$?; echo LOOP_COPY_DONE','LOOP_COPY_DONE'))
   if rc(text,'LOOP_COPY_RC')!=0:raise RuntimeError('client copy failed')
   if readback(copied,60)!=o.dev_app.read_bytes():raise RuntimeError('built client guest readback mismatch')
   text=save('developer-loop',command('chmod 700 '+copied+' && '+copied+' '+o.mountpoint+'/loop-input.txt; echo LOOP_RC=$?; echo LOOP_DONE','LOOP_DONE'))
   expected='HOSTSHARE_DEVLOOP_BEGIN\n'+loop_input.decode()+'HOSTSHARE_DEVLOOP_END'
   if expected not in text or rc(text,'LOOP_RC')!=0:raise RuntimeError('host-built client did not read boot-mounted input')
   report['developer_loop']={'passed':True,'build':dev_build,'guest_byte_exact':True,'input_sha256':h(corpus/'loop-input.txt'),'source':'examples/developer-loop.c'}
   text=save('normal-stop',command('kill -TERM $HS_PID; echo STOP_SIGNAL_RC=$?; sleep 2; kill -0 $HS_PID; echo STILL_ALIVE_RC=$?; echo NORMAL_STOP_DONE','NORMAL_STOP_DONE'))
   report['normal_stop']={'passed':rc(text,'STOP_SIGNAL_RC')==0 and rc(text,'STILL_ALIVE_RC') not in (None,0) and 'HOSTSHARE MOUNT TERM_DETACHED' in text,'exit_status':'not a child of serial shell; signal/detach/process absence observed'}
  else:
   text=save('normal-stop',command('kill -TERM $HS_PID; wait $HS_PID; echo STOP_RC=$?; cat '+guest+'/mount.log; echo NORMAL_STOP_DONE','NORMAL_STOP_DONE'))
   report['normal_stop']={'passed':rc(text,'STOP_RC')==0 and 'HOSTSHARE MOUNT TERM_DETACHED' in text}
  # Restore only the explicitly disposable exported fixture; never source/image state.
  (corpus/'hello.txt').write_bytes(contents['hello.txt'])
  if o.midread:
   text=save('midread-start',command(app+' --pci-line --mount-pause-read > '+guest+'/pause.log 2>&1 & PAUSE_PID=$!; sleep 2; cat '+guest+'/pause.log; '+app+' --read-once /mnt/host/1MiB > '+guest+'/client.log 2>&1 & CLIENT_PID=$!; sleep 1; cat '+guest+'/pause.log; cat '+guest+'/client.log; echo MIDREAD_PENDING','MIDREAD_PENDING'))
   pending='HOSTSHARE MIDREAD_HANDLER_ENTER' in text and 'HOSTSHARE READ_ONCE CALL_BEGIN' in text and 'HOSTSHARE READ_ONCE RESULT' not in text
   report['midread']={'handler_pending_before_kill':pending,'scope':'Explicit diagnostic pause in read handler before RPC; actual blocked POSIX read. NOT active virtio DMA safety.'}
   if pending:
    text=save('midread-result',command('kill -KILL $PAUSE_PID; wait $PAUSE_PID; echo SERVER_WAIT_RC=$?; wait $CLIENT_PID; echo CLIENT_WAIT_RC=$?; cat '+guest+'/client.log; cat '+guest+'/pause.log; echo MIDREAD_RESULT_DONE','MIDREAD_RESULT_DONE',30))
    m=re.search(r'^HOSTSHARE READ_ONCE RESULT n=(-?\d+) errno=(\d+) EIO=(\d+) elapsed_seconds=([0-9.]+)$',text,re.M)
    report['midread'].update({'server_wait_rc':rc(text,'SERVER_WAIT_RC'),'client_wait_rc':rc(text,'CLIENT_WAIT_RC'),'observed_read_n':int(m[1]) if m else None,'observed_errno':int(m[2]) if m else None,'EIO_constant':int(m[3]) if m else None,'elapsed_seconds':float(m[4]) if m else None,'passed':bool(m and int(m[1])==-1 and int(m[2])==int(m[3]) and rc(text,'CLIENT_WAIT_RC')==0 and rc(text,'SERVER_WAIT_RC')==137)})
   else:
    report['midread']['passed']=False
    save('midread-abort',command('kill -KILL $PAUSE_PID $CLIENT_PID; wait $PAUSE_PID; wait $CLIENT_PID; echo MIDREAD_ABORTED','MIDREAD_ABORTED'))
   text=save('remount',command(app+' --tag '+o.tag+' --mountpoint '+o.mountpoint+' --pci-line --mount > '+guest+'/remount.log 2>&1 & AGAIN_PID=$!; sleep 2; cat '+guest+'/remount.log; cat /mnt/host/hello.txt; echo REMOUNT_CAT_RC=$?; '+app+' --checksum /mnt/host/1MiB; echo REMOUNT_CHECK_RC=$?; kill -TERM $AGAIN_PID; wait $AGAIN_PID; echo REMOUNT_STOP_RC=$?; cat '+guest+'/remount.log; echo REMOUNT_DONE','REMOUNT_DONE',240))
   report['remount']={'passed':rc(text,'REMOUNT_CAT_RC')==0 and rc(text,'REMOUNT_CHECK_RC')==0 and rc(text,'REMOUNT_STOP_RC')==0 and 'HOSTSHARE CHECKSUM 2572415250 1048576 /mnt/host/1MiB' in text}
  route_pass=report['boot_mount']['ready_before_any_host_command'] if o.boot_stage=='verify' else report['probe']['passed']
  gates=[route_pass,report['mount']['passed'],len(report['corpus'])==7,all(v['passed'] for v in report['corpus'].values()),report['host_edit']['passed'],report['readonly']['passed'],report['normal_stop']['passed']]
  if o.midread:gates += [report['midread']['passed'],report['remount']['passed']]
  report['status']='PASS_READONLY_SUITE' if all(gates) else 'BLOCKED_GATE'
  if o.midread and not report['midread']['passed']:report['blocker']='Pending-read death did not produce observed n=-1 errno=EIO; actual result retained, no translation/inference.'
except Exception as e:
 report['error']=repr(e)
finally:
 r.terminate()
 try:r.wait(10)
 except subprocess.TimeoutExpired:r.kill();r.wait()
 report.update(qemu_exit_rc=r.returncode,stopped_reaped=True,memory_events=(cg/'memory.events').read_text(),memory_peak=int((cg/'memory.peak').read_text()),disk_sha256_after=h(disk),image_sha256_after=h(image))
 if report['qemu_exit_rc']!=0:report.update(status='FAIL',error='owned QEMU nonzero termination')
 if report['disk_sha256_after']!=report['disk_sha256'] or report['image_sha256_after']!=report['image_sha256']:report.update(status='FAIL',error='base artifact changed')
 if o.boot_stage=='prepare' and report['status']=='PASS_BOOT_PREPARED':
  pin={'schema':'hostshare.boot-overlay.v1','overlay_sha256':boot_handoff.digest(o.boot_overlay),'base_sha256':h(disk),'elf_sha256':h(elf),'hook_sha256':__import__('hashlib').sha256(boot_handoff.hook(o.tag,o.mountpoint)).hexdigest(),'tag':o.tag,'mountpoint':o.mountpoint,'sealed':True}
  (out/'boot-overlay-pin.json').write_text(json.dumps(pin,indent=2)+'\n')
 if report['disk_sha256_after']!=report['disk_sha256'] or report['image_sha256_after']!=report['image_sha256']:report.update(status='FAIL',error='base artifact changed')
 event({'event':'runner_terminal','status':report['status'],'qemu_exit_rc':r.returncode,'stopped_reaped':True,'mono':time.monotonic()})
 eventlog.close()
 rawpath.write_bytes(serial)
 if binary_window is not None:del serial[binary_window:];serial.extend(b'[FAILED ELF READBACK REDACTED]\n')
 (out/'serial.txt').write_text(redact_payload_commands(serial.decode(errors='replace')))
 (out/'memory.jsonl').write_text(''.join(json.dumps(v)+'\n' for v in samples))
 (out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report),flush=True)
raise SystemExit(0 if report['status'] in ('PASS_READONLY_SUITE','PASS_BOOT_PREPARED') else 1)
