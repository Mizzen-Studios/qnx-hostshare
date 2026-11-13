import os,json,time,subprocess,selectors,fcntl,hashlib,re,socket
from pathlib import Path
root=Path(__file__).resolve().parents[1];base=root/'docs/acceptance/mount-20261113';out=base/'native1';out.mkdir(exist_ok=False)
lock=open('/home/ubuntu/qnx-host/native-test.lock','a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
assert subprocess.run(['pgrep','-f','^qemu-system-'],stdout=subprocess.DEVNULL).returncode==1
cg=Path('/sys/fs/cgroup')/next(x.split(':',2)[2].strip().lstrip('/') for x in Path('/proc/self/cgroup').read_text().splitlines() if x.startswith('0::'))
caps={k:(cg/k).read_text().strip() for k in ['cpu.max','memory.max','memory.swap.max']};assert caps=={'cpu.max':'100000 100000','memory.max':'1073741824','memory.swap.max':'0'} and os.getpriority(os.PRIO_PROCESS,0)>=15
shared=Path('/home/ubuntu/qnx-host/guest/shared');image=shared/'incident-20261108/incident.ifs';disk=shared/'qnx-native/disk-qemu';elf=shared/'hostshare-mount-20261113/build1/qnx_hostshare'
corpus=root/'.local/mount-20261113/corpus';assert corpus.is_dir()
args=['qemu-system-x86_64','-machine','pc,accel=tcg','-cpu','max','-smp','1','-m','512','-display','none','-serial','stdio','-monitor','none','-no-reboot','-kernel',str(image),'-drive','file='+str(disk)+',format=raw,if=ide,snapshot=on','-nic','user,model=virtio-net-pci','-fsdev','local,id=f0,path='+str(corpus)+',security_model=none,readonly=on','-device','virtio-9p-pci,fsdev=f0,mount_tag=f0test,disable-legacy=on']
qpath=root/'.local/hostshare-qtest.sock'
assert not qpath.exists()
args += ['-qtest','unix:'+str(qpath)+',server=on,wait=off']
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'status':'FAIL','source_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'caps':caps,'command':args,'image_sha256':h(image),'disk_sha256':h(disk),'elf_sha256':h(elf),'native_source_sha256':h(root/'native/qnx_hostshare.c'),'source_files':{str(p.relative_to(root)):h(p) for p in list((root/'native').glob('*.[ch]'))+list((root/'core').glob('*.[ch]'))},'corpus_sha256':h(corpus/'hello.txt'),'prebuilt_source_record':(shared/'incident-20261108/source-commit').read_text().strip(),'native_exit_rc':None,'commands':[]}
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
 (root/'.local/mount-20261113/native-readback.bin').write_bytes(observed)
 # Do not commit executable bytes embedded in serial.
 del serial[start:];serial.extend(b'[OWN ELF READBACK REDACTED; byte comparison in receipt]'+bytes([10]))
 if not verified:raise RuntimeError('native ELF readback byte mismatch: '+str(len(observed)))
 report['n1']={};mode=None
 for candidate in ['--pci-line','--msix']:
  text=command('/data/home/root/hostshare '+candidate+'; echo HOSTSHARE_APP_RC=$?; echo HOSTSHARE_GATE_DONE','HOSTSHARE_GATE_DONE',60)
  (out/(candidate[2:]+'.txt')).write_text(text)
  m=re.search(r'^HOSTSHARE_APP_RC=(\d+)$',text.replace(chr(13),''),re.M)
  passed=bool(m and int(m[1])==0 and 'HOSTSHARE F2 READONLY BYTE_EXACT PASS' in text)
  report['n1'][candidate]={'passed':passed,'app_rc':int(m[1]) if m else None,'routing_mutated':False}
  if passed:mode=candidate;break
 if mode is None:
  with socket.socket(socket.AF_UNIX) as qt:
   qt.settimeout(3);qt.connect(str(qpath));f=qt.makefile('rwb',buffering=0)
   def call(cmd):
    f.write((cmd+chr(10)).encode());row=f.readline().decode().strip()
    if not row.startswith('OK'):raise RuntimeError('qtest '+row)
    return row
   def pci(addr,value=None):
    call('outl 0xcf8 '+hex(addr))
    return int(call('inl 0xcfc').split()[-1],16) if value is None else call('outl 0xcfc '+hex(value))
   devices=[{'slot':i,'id':pci(0x80000000+(i<<11)),'irq':pci(0x8000003c+(i<<11))} for i in range(1,8)]
   dev=next(d for d in devices if d['id']==0x10491af4);pin=((dev['irq']>>8)&255)-1
   if not 0<=pin<4:raise RuntimeError('invalid PCI IRQ pin')
   route=(dev['slot']-1+pin)%4;old=pci(0x80000860);new=(old&~(255<<(8*route)))|(10<<(8*route));pci(0x80000860,new)
   assert pci(0x80000860)==new
   report['irq_routing']={'device':dev,'pirq_index':route,'original':old,'updated':new,'irq':10,'scope':'only own9p PIRQ route per existing QNX PC native collector pattern; no CAN device'}
   f.close()
  mode='--pci-api'
 report['mount_mode']=mode
 command('/data/home/root/hostshare '+mode+' --mount > /data/home/root/mount.log 2>&1 & echo HS_MOUNT_PID=$!; sleep 2; cat /data/home/root/mount.log; echo MOUNT_START_DONE','MOUNT_START_DONE',40)
 text=command('cat /mnt/host/hello.txt; echo CAT_RC=$?; ls -1 /mnt/host; echo LS_RC=$?; echo N2_DONE','N2_DONE',60)
 (out/'n2.txt').write_text(text)
 report['n2']={'passed':'HostShare F0 public synthetic test only.' in text.replace(chr(13),'').splitlines() and '\nCAT_RC=0' in text and '\nLS_RC=0' in text and all(name in text.replace(chr(13),'').splitlines() for name in ['hello.txt','empty','one','4KiB','1MiB','nested','unicode-λ.txt'])}
 text=command('echo forbidden > /mnt/host/hello.txt; echo WRITE_RC=$?; echo READONLY_DONE','READONLY_DONE',30)
 (out/'readonly.txt').write_text(text);m=re.search(r'^WRITE_RC=(\d+)$',text.replace(chr(13),''),re.M)
 report['readonly']={'passed':bool(m and int(m[1])!=0 and h(corpus/'hello.txt')==report['corpus_sha256'])}
 manifest=json.loads((base/'corpus.json').read_text());report['n3']={}
 if report['n2']['passed']:
  for name,expected in manifest.items():
   path='/mnt/host/'+name
   text=command("/data/home/root/hostshare --checksum '"+path+"'; echo CHECK_RC=$?; echo CHECK_DONE",'CHECK_DONE',240)
   (out/('checksum-'+name.replace('/','_')+'.txt')).write_text(text)
   m=re.search(r'^HOSTSHARE CHECKSUM (\d+) (\d+) ',text.replace(chr(13),''),re.M)
   report['n3'][name]={'passed':bool(m and int(m[1])==expected['posix_cksum'] and int(m[2])==expected['size'] and '\nCHECK_RC=0' in text),'observed_cksum':int(m[1]) if m else None,'observed_size':int(m[2]) if m else None}
  changed=b'HostShare host edit observed without rebuild.\n';(corpus/'hello.txt').write_bytes(changed);start_edit=time.monotonic()
  text=command('cat /mnt/host/hello.txt; echo EDIT_RC=$?; echo EDIT_DONE','EDIT_DONE',60)
  (out/'n4.txt').write_text(text);report['n4']={'passed':changed.decode().strip() in text and '\nEDIT_RC=0' in text,'elapsed_seconds':time.monotonic()-start_edit,'new_sha256':h(corpus/'hello.txt'),'rebuild':False}
 command('cat /data/home/root/mount.log; echo MOUNT_LOG_DONE','MOUNT_LOG_DONE',60)
 report['status']='PASS_MOUNT_CORPUS' if report['n2']['passed'] and report['readonly']['passed'] and len(report['n3'])==len(manifest) and all(x['passed'] for x in report['n3'].values()) else 'FAIL_MOUNT_GATE'

except Exception as e:report['error']=repr(e)
finally:
 r.terminate()
 try:r.wait(10)
 except subprocess.TimeoutExpired:r.kill();r.wait()
 qpath.unlink(missing_ok=True);report['qemu_exit_rc']=r.returncode;report['stopped_reaped']=True;report['memory_events']=(cg/'memory.events').read_text();report['memory_peak']=(cg/'memory.peak').read_text();(root/'.local/mount-20261113/native-serial-raw.txt').write_bytes(serial);(out/'serial.txt').write_text(re.sub(r"printf '%b' '[^']*' >> /data/home/root/hostshare",'[OWN ELF COPY REDACTED]',serial.decode(errors='replace')));(out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report),flush=True)
