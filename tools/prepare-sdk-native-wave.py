from pathlib import Path
import shutil,hashlib,subprocess
root=Path(__file__).resolve().parents[1];out=root/'docs/acceptance/native-20261113';out.mkdir(parents=True,exist_ok=True)
local=root/'.local/native-20261113';local.mkdir(parents=True,exist_ok=True)
p=Path('/home/ubuntu/qnx-host/guest/guestctl-capped.py');before=p.read_text();shutil.copy2(p,local/'controller.before.py')
assert before.count("'q35,accel=tcg'")==1
p.write_text(before.replace("'q35,accel=tcg'","'q35','-accel','tcg,tb-size=256'"))
with open(out/'controller.diff','w') as f:subprocess.run(['diff','-u',str(local/'controller.before.py'),str(p)],stdout=f)
(out/'controller-hashes.txt').write_text('before '+hashlib.sha256(before.encode()).hexdigest()+'\nafter '+hashlib.sha256(p.read_bytes()).hexdigest()+'\n')
