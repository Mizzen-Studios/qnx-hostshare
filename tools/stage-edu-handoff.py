import json,hashlib,shutil
from pathlib import Path
src=Path('/home/ubuntu/.openclaw/workspace/.openclaw/tmp/edu-stock-20261113');meta=json.loads((src/'handoff.json').read_text());dest=Path('/home/ubuntu/qnx-host/guest/shared/hostshare-native-20261113/edu-handoff');dest.mkdir(exist_ok=False)
for name,h in {**meta['sources'],'compile-lesson-PLAN.sh':meta['compile_plan_sha256']}.items():
 assert hashlib.sha256((src/name).read_bytes()).hexdigest()==h,name
 shutil.copy2(src/name,dest/name)
print(json.dumps({'source_commit':meta['source_commit'],'verified':True,'dest':str(dest)}))
