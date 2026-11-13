"""Verify local evidence and write a factual, fail-closed wave receipt."""
from pathlib import Path
import fcntl,hashlib,json,subprocess,time
root=Path(__file__).resolve().parents[1];base=root/'docs/acceptance/mount-20261113'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
a=load(base/'native1/receipt.json');a2=load(base/'native2/receipt.json');b=load(base/'native3/receipt.json')
sdks=[load(base/'sdk-owner.json'),load(base/'sdk2/sdk-owner.json')]
assert all(x['stopped_reaped'] for x in [a,a2,b,*sdks])
assert subprocess.run(['pgrep','-f','^qemu-system-'],stdout=subprocess.DEVNULL).returncode==1
lock=open('/home/ubuntu/qnx-host/native-test.lock','a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
assert subprocess.check_output(['git','diff','790e9b2','--','docs/acceptance/native-20261113','docs/acceptance/f0'],cwd=root)==b''
for name,digest in b['source_files'].items():assert h(root/name)==digest
for name,digest in load(base/'build2-source-hashes.json').items():assert h(root/name)==digest
shared=Path('/home/ubuntu/qnx-host/guest/shared')
assert h(shared/'hostshare-mount-20261113/build2/qnx_hostshare')==b['elf_sha256']
assert h(shared/'incident-20261108/incident.ifs')==b['image_sha256']
assert h(shared/'qnx-native/disk-qemu')==b['disk_sha256']
assert a['command']==a2['command']==b['command']
report={'observed_epoch':time.time(),'baseline_preserved':'790e9b2dc45eaa1de67d6f988394afd1b2e1ec43','source_commit':b['source_sha'],'status':b['status'],'n1':b.get('n1',{}),'n1_evidence':b.get('n1_evidence','native3/receipt.json'),'n2':b.get('n2',{}),'n3':b.get('n3',{}),'n4':b.get('n4',{'status':'NOT_RUN'}),'readonly':b.get('readonly',{}),'routing_workaround_used_final_attempt':'irq_routing' in b,'sdk_sampled_peak_bytes':[s['peak_cgroup_bytes'] for s in sdks],'native_peak_bytes':[int(x['memory_peak']) for x in [a,a2,b]],'cleanup':{'all_guests_stopped_reaped':True,'qemu_count':0,'lease':'FREE','next_slot':'EDU via parent coordination; no EDU repo changes'},'native_command_parity':'identical native1/native2/native3; original attempt3 differs only fresh corpus path','limits':'SDK2GiB/TCG256MiB; native original argv and stricter1GiB; guest512MiB, CPU100%, nice15, smp1, swap cap0, reserve64MiB','external_review':'timed out without findings; not completed review','scope':'bounded synthetic readonly mount; no production filesystem, stock-image, hardware, concurrency, reconnect or broad-coherency claim','proofs':{}}
for p in sorted(base.rglob('*')):
 if p.is_file() and p.name not in ('receipt.json','MANIFEST.sha256'):
  report['proofs'][str(p.relative_to(base))]=h(p)
report['proofs']['native1/receipt.json']=h(base/'native1/receipt.json');report['proofs']['native2/receipt.json']=h(base/'native2/receipt.json');report['proofs']['native3/receipt.json']=h(base/'native3/receipt.json')
(base/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
(base/'MANIFEST.sha256').write_text(''.join(h(p)+'  '+str(p.relative_to(base))+'\n' for p in sorted(base.rglob('*')) if p.is_file() and p.name!='MANIFEST.sha256'))
print(json.dumps({k:v for k,v in report.items() if k!='proofs'},indent=2))
