"""Finalize only after every SDK/native process is stopped; preserve all attempts."""
from pathlib import Path
import fcntl,hashlib,json,subprocess,time
r=Path(__file__).resolve().parents[1];b=r/'docs/acceptance/stock-repeat-20261113'
load=lambda p:json.loads(p.read_text())
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert subprocess.run(['pgrep','-f','^qemu-system-'],stdout=subprocess.DEVNULL).returncode==1
lock=open('/home/ubuntu/qnx-host/native-test.lock','a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
sdk=load(b/'sdk/sdk-owner.json');assert sdk['stopped_reaped'] and sdk['peak_cgroup_bytes']<2147483648
build=load(b/'build-source-hashes.json')
for name,digest in build['files'].items():assert h(r/name)==digest
history=subprocess.check_output(['git','diff','28882093e9a15a33dc67aeae5e46ef3f6aa219ed','--name-only','--','docs/acceptance'],cwd=r,text=True).splitlines()
assert all(s.startswith('docs/acceptance/stock-repeat-20261113/') for s in history),history
results={}
for name in ['cold-historical','cold-stock']:
 a=load(b/name/'receipt.json');assert a['stopped_reaped'] and a['native_copy_byte_exact']
 assert a['clean_checkout'] and a['source_files']==build['files'] and a['elf_sha256']==build['elf_sha256']
 assert a['qtest'] is False and a['irq_routing_mutated'] is False
 assert '-qtest' not in a['command'] and 'tcg,tb-size=256' in a['command']
 assert a['caps']=={'cpu.max':'100000 100000','memory.max':'2147483648','memory.swap.max':'0'} and a['nice']>=15
 assert a['memory_peak']+67108864<=2147483648
 assert a['disk_sha256']==a['disk_sha256_after'] and a['image_sha256']==a['image_sha256_after']
 assert all(int(row.split()[1])==0 for row in a['memory_events'].splitlines() if row.split()[0] in ['max','oom','oom_kill'])
 summary=load(b/name/'memory-summary.json')
 assert summary['reserve_violations']==summary['event_violations']==0 and summary['max_current']+67108864<=2147483648
 assert h(Path(summary['raw_path']))==summary['raw_sha256']
 results[name]=a
stock=results['cold-stock'];upstream=load(b/'upstream-handoff.json')
assert stock['image_kind']=='stock'
assert stock['image_sha256']==upstream['artifacts']['ifs.bin']['sha256'] and stock['disk_sha256']==upstream['artifacts']['disk-qemu']['sha256']
for line in (b/'sdk/sdk-memory.jsonl').read_text().splitlines():
 s=json.loads(line);assert int(s['memory']['memory.current'])+67108864<=2147483648
 assert all(int(row.split()[1])==0 for row in s['memory']['memory.events'].splitlines() if row.split()[0] in ['max','oom','oom_kill'])
report={'completed_at':time.time(),'status':'PASS' if all(a['status']=='PASS_READONLY_SUITE' for a in results.values()) else 'PARTIAL_PRECISE_BLOCKED','baseline_accepted':'28882093e9a15a33dc67aeae5e46ef3f6aa219ed N1c/idle-N5 preserved','native_source_sha':results['cold-historical']['source_sha'],'build':build,'cold_reader':load(b/'cold-reader.json'),'runs':{},'N7':{'passed':stock.get('probe',{}).get('passed',False) and stock.get('mount',{}).get('passed',False),'image_provenance':'New hashed stock mkqnximage IFS/disk from EDU be712b27; NOT historical CAN image','SSH':'UNVERIFIED; stock sshd boot fault, serial-only transfer; no repair'},'sdk':sdk,'cleanup':{'all_stopped_reaped':True,'qemu_count':0,'canonical_lease':'FREE'},'restrictions':'Private £0 existing SDK; no install/login/platform repair/EDU retry/routing rewrite/MSIX/CAN/C6/media/public/PR','scope':'Readonly synthetic data only. Explicit diagnostic server read-handler pause before RPC/DMA, actual POSIX errno observation. NOT active-DMA or physical-device crash safety. Previous reduced-privilege/idle results not rerun or expanded.'}
for name,a in results.items():report['runs'][name]={k:a[k] for k in ['status','source_sha','image_kind','image_sha256','disk_sha256','elf_sha256','probe','mount','corpus','host_edit','readonly','normal_stop','midread','remount','memory_peak'] if k in a};report['runs'][name]['blocker']=a.get('blocker',a.get('error'))
(b/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
(b/'MANIFEST.sha256').write_text(''.join(h(p)+'  '+str(p.relative_to(b))+'\n' for p in sorted(b.rglob('*')) if p.is_file() and p.name!='MANIFEST.sha256'))
print(json.dumps(report,indent=2))
