import time,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1];ready=root/'.local/stock-repeat-20261113/sdk/SDK_READY';out=root/'docs/acceptance/stock-repeat-20261113/sdk'
end=time.monotonic()+620
while not ready.exists():
 if (out/'sdk-owner.json').exists():raise SystemExit('owner ended before ready')
 if time.monotonic()>end:raise SystemExit('ready wait expired')
 time.sleep(2)
r=subprocess.run(['python3','/home/ubuntu/qnx-host/guest/guestctl-capped.py','exec',str(root/'tools/stock-sdk-build.sh'),'240'],stdout=open(root/'.local/stock-repeat-20261113/build.log','w'),stderr=subprocess.STDOUT,timeout=250)
(out/'inventory-exit.txt').write_text(str(r.returncode));print('INVENTORY_RC='+str(r.returncode),flush=True)
