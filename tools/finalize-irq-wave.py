from pathlib import Path
import fcntl,hashlib,json,subprocess,time
root=Path(__file__).resolve().parents[1];base=root/'docs/acceptance/irq-restart-20261113'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
old=load(base/'intx-clean/receipt.json');b=load(base/'msix-clean/receipt.json');a=load(base/'intx-fixed/receipt.json');sdk=load(base/'sdk-owner.json');sdk2=load(base/'sdk2/sdk-owner.json');build=load(base/'build2-source-hashes.json');build1=load(base/'build-source-hashes.json')
assert all(x['stopped_reaped'] for x in [a,b,old,sdk,sdk2])
assert subprocess.run(['pgrep','-f','^qemu-system-'],stdout=subprocess.DEVNULL).returncode==1
lock=open('/home/ubuntu/qnx-host/native-test.lock','a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
assert old['command']==b['command']
assert [(i,v) for i,v in enumerate(a['command']) if i!=a['command'].index('-fsdev')+1]==[(i,v) for i,v in enumerate(b['command']) if i!=b['command'].index('-fsdev')+1]
assert all('-qtest' not in x['command'] and x.get('qtest') is False and x.get('irq_routing_mutated') is False for x in [a,b])
for name,digest in build['files'].items():assert h(root/name)==digest
assert old['source_files']==b['source_files']==build1['files'] and old['elf_sha256']==b['elf_sha256']==build1['elf_sha256']
assert a['source_files']==build['files'] and a['elf_sha256']==build['elf_sha256']
for x in [a,b,old]:
 assert not any(int(line.split()[1]) for line in x['memory_events'].splitlines() if line.split()[0] in ['max','oom','oom_kill'])
 assert x['native_copy_byte_exact']
assert a['image_sha256']==b['image_sha256'] and a['disk_sha256']==b['disk_sha256']
assert subprocess.check_output(['git','diff','c4e4f25','--','docs/acceptance/mount-20261113','docs/acceptance/native-20261113','docs/acceptance/f0'],cwd=root)==b''
report={'kind':'hostshare-irq-restart-wave-v1','observed_epoch':time.time(),'source_commit':a['source_sha'],'baseline_preserved':'c4e4f258acc992378f14e88fc88f98f80ce11b2e','n1c_intx':a.get('n1c',{'status':'BLOCKED','error':a.get('error')}),'intx_mount':a.get('mount',{'status':'NOT_RUN'}),'clean_msix':b.get('n1c',{'status':'BLOCKED','error':b.get('error')}),'clean_msix_scope':'clean boot only msix, Memory Space before installed API; its original ELF, no retest claimed for cleanup-only corrected ELF','n5_idle_sigkill':a.get('n5_stop',{'status':'NOT_RUN'}),'n5_privilege_remount':a.get('n5_drop_remount',{'status':'NOT_RUN'}),'n5_cooperative_stop':a.get('drop_cleanup',{'status':'NOT_RUN'}),'n6':{'user_visible_launcher':'tools/run-native-readonly.sh','instructions':'docs/RUN_NATIVE.md','actual_clean_detached_checkout':a['source_sha'],'demo':'docs/DEMO_DRAFT.md','recorded':False,'published':False},'n7':load(base/'N7.json'),'qtest_or_routing_writes':False,'sdk':[sdk,sdk2],'native_peak_bytes':[int(x['memory_peak']) for x in [old,b,a]],'preserved_failure':'intx-clean/receipt.json (wrong checksum assertion plus real post-detach rc139)', 'msix_evidence_build':b['source_sha'],'source_files':build['files'],'elf_sha256':build['elf_sha256'],'image_sha256':a['image_sha256'],'disk_sha256':a['disk_sha256'],'cleanup':{'all_guests_stopped_reaped':True,'qemu_count':0,'exclusive_lease':'FREE','handoff':'Parent owns next authorization. Wave STOPPED for review.'},'limits':'SDK host2GiB/cache256MiB; native existing stricter1GiB/original pc accel argv; guest512MiB,CPU100,nice15,smp1,swap0,reserve64MiB. No install/login/repair/imagebuild/EDUretry/CAN/C6/public/media/PR.','scope':'Synthetic readonly fixture on historical custom image. Least-privilege observations only; INTERRUPT retained and no exhaustive ability audit. SIGKILL idle only, not active/in-flight DMA safety. Reduced cleanup verifies virtio status0/queue0 but skips PCI backend and does NOT verify bus-master disable/restore.'}
(base/'receipt.json').write_text(json.dumps(report,indent=2)+chr(10))
(base/'MANIFEST.sha256').write_text(''.join(h(p)+'  '+str(p.relative_to(base))+chr(10) for p in sorted(base.rglob('*')) if p.is_file() and p.name!='MANIFEST.sha256'))
print(json.dumps(report,indent=2))
