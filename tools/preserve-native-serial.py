"""Keep exact raw logs locally; Git gets text receipts without embedded ELF."""
from pathlib import Path
import json,hashlib,shutil
root=Path(__file__).resolve().parents[1];base=root/'docs/acceptance/native-20261113';local=root/'.local/native-20261113';result=[]
for attempt in sorted(base.glob('attempt*')):
 p=attempt/'serial.txt'
 if not p.exists():continue
 data=p.read_bytes();raw=local/(attempt.name+'-serial-raw.txt');raw.write_bytes(data)
 lines=data.splitlines(keepends=True);redacted=0;clean=[]
 for line in lines:
  if b"printf '%b' '" in line and b'>> /data/home/root/hostshare' in line:
   clean.append(b'[OWN ELF UPLOAD CHUNK REDACTED; raw retained locally]'+bytes([10]));redacted+=1
  else:clean.append(line)
 p.write_bytes(b''.join(clean));result.append({'attempt':attempt.name,'raw_path':str(raw),'raw_sha256':hashlib.sha256(data).hexdigest(),'committed_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'redacted_elf_upload_lines':redacted,'reason':'no encoded executable artifacts in Git; exact logs retained local'})
(base/'serial-preservation.json').write_text(json.dumps(result,indent=2)+'\n')
