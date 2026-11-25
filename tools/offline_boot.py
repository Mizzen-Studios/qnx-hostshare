"""HOST-only offline-derived provenance. No guest launch or filesystem writer."""
import hashlib,json,re,struct
from pathlib import Path
from qnx6_inspect import BootFS
from stock_pin import HISTORICAL_STOCK
from boot_handoff import hook,overlay_info,digest
TOOLS={'mkqnx6fsimg':'bfd530ca2a944f42162491600c34cb6dea9f47e560fe4ff295b049e0284467ab','diskimage':'d73cd6cf64b9956948d2d7bc6fdfe0b041ad0e44d4bc0df4c940771940c75d2e'}

def regular(path,limit=512*1024*1024):
 p=Path(path)
 if any(x.is_symlink() for x in (p,*p.parents)) or not p.is_file() or not 0<p.stat().st_size<=limit:raise ValueError('regular bounded file required')
 return p

def mbr(path):
 p=regular(path);length=p.stat().st_size
 with p.open('rb') as f:b=f.read(512)
 if len(b)!=512 or b[510:]!=bytes([85,170]):raise ValueError('MBR signature')
 result=[]
 for i in range(4):
  e=b[446+16*i:462+16*i];start,count=struct.unpack_from('<II',e,8)
  if i==3:
   if any(e):raise ValueError('unexpected fourth partition')
   continue
  if e[4]!=(177,178,179)[i] or e[0]!=(128,0,0)[i] or not count or start<1 or (start+count)*512>length:raise ValueError('partition type/active/bounds')
  if result and start<result[-1]['start']+result[-1]['count']:raise ValueError('partition overlap')
  result.append({'type':e[4],'start':start,'count':count})
 return result

def slice_hash(path,part):
 with regular(path).open('rb') as f:
  f.seek(part['start']*512);left=part['count']*512;h=hashlib.sha256()
  while left:
   b=f.read(min(left,1024*1024))
   if not b:raise ValueError('truncated partition')
   h.update(b);left-=len(b)
 return h.hexdigest()

def buildfile(ifs,driver,onboot):
 paths=[str(x) for x in (ifs,driver,onboot)]
 if any(not re.fullmatch('/[A-Za-z0-9_./-]+',p) or '..' in Path(p).parts for p in paths):raise ValueError('unsafe source path')
 return '\n'.join(['[num_sectors=*4096]','[-optional]','[uid=0 gid=0 perms=0644] /.boot/qnx_sdp.ifs='+paths[0],'[uid=0 gid=0 perms=0755] /hsd='+paths[1],'[uid=0 gid=0 perms=0644] /onboot='+paths[2],''])

def inspect(original,derived,image,driver,tag,mountpoint):
 for p in (original,derived,image,driver):regular(p)
 if digest(original)!=HISTORICAL_STOCK['disk-qemu'] or digest(image)!=HISTORICAL_STOCK['ifs.bin']:raise ValueError('original pin mismatch')
 old=mbr(original);new=mbr(derived)
 for i in (1,2):
  if old[i]['count']!=new[i]['count'] or slice_hash(original,old[i])!=slice_hash(derived,new[i]):raise ValueError('preserved partition mismatch')
 fs=BootFS(derived)
 try:
  summary=fs.summary()
 finally:fs.close()
 expected={'.boot/qnx_sdp.ifs':(image,0o100644),'hsd':(driver,0o100755),'onboot':(None,0o100644)}
 if set(summary['files'])!=set(expected):raise ValueError('boot file set')
 for name,(p,mode) in expected.items():
  b=Path(p).read_bytes() if p else hook(tag,mountpoint);a=summary['files'][name]
  if a!={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'mode':oct(mode)}:raise ValueError('boot payload/mode mismatch')
 spare=summary['metadata_free_blocks']*summary['blocksize']
 if spare<1024*1024 or new[0]['count']<=old[0]['count']:raise ValueError('insufficient spare capacity')
 return {'files':summary['files'],'partitions':new,'preserved_partition_sha256':[slice_hash(derived,new[i]) for i in (1,2)],'metadata_spare_bytes':spare,'capacity_not_runtime_allocation_guarantee':True}

def validate(pin,original,derived,image,driver,tag,mountpoint):
 p=regular(pin,65536);data=json.loads(p.read_text())
 if set(data)!={'schema','original_sha256','derived_sha256','ifs_sha256','driver_sha256','hook_sha256','tag','mountpoint','tools','ipl_sha256','build_source_sha','evidence','inspection'}:raise ValueError('offline pin fields')
 expected={'schema':'hostshare.offline-derived.v1','original_sha256':digest(original),'derived_sha256':digest(derived),'ifs_sha256':digest(image),'driver_sha256':digest(driver),'hook_sha256':hashlib.sha256(hook(tag,mountpoint)).hexdigest(),'tag':tag,'mountpoint':mountpoint,'tools':TOOLS}
 if any(data[k]!=v for k,v in expected.items()):raise ValueError('offline binding mismatch')
 if not re.fullmatch('[0-9a-f]{64}',data['ipl_sha256']) or not re.fullmatch('[0-9a-f]{40}',data['build_source_sha']):raise ValueError('offline provenance')
 if not isinstance(data['evidence'],dict) or not data['evidence']:raise ValueError('missing licensed build evidence')
 for name,h in data['evidence'].items():
  if not re.fullmatch('[A-Za-z0-9_.-]+',name) or digest(regular(p.parent/name,400000))!=h:raise ValueError('build evidence mismatch')
 if data['inspection']!=inspect(original,derived,image,driver,tag,mountpoint):raise ValueError('offline inspection mismatch')
 return data

def validate_overlay(overlay,pin,original,derived,image,driver,tag,mountpoint):
 info=overlay_info(overlay,derived)
 # The runtime overlay MUST be pristine; do not reuse a failed/modified overlay.
 p=regular(pin,65536);binding=json.loads(p.read_text())
 if set(binding)!={'schema','offline_pin_sha256','overlay_sha256'} or binding['schema']!='hostshare.offline-overlay.v1':raise ValueError('offline overlay pin')
 provenance=p.with_name('offline-derived.json')
 if binding['offline_pin_sha256']!=digest(provenance) or binding['overlay_sha256']!=digest(overlay):raise ValueError('offline overlay binding')
 validate(provenance,original,derived,image,driver,tag,mountpoint)
 return info
