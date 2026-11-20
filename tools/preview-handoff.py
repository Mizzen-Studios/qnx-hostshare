#!/usr/bin/env python3
"""HOST-only illustrative handoff template. No files validated, no guest launched."""
import argparse,shlex,sys
from handoff_preflight import config
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--tag',default='dev-inputs');parser.add_argument('--mountpoint',default='/mnt/dev-inputs')
args=parser.parse_args()
try:config(args.tag,args.mountpoint)
except ValueError as error:print('BLOCKED: '+str(error),file=sys.stderr);raise SystemExit(2)
print('PREVIEW ONLY — NOT VALIDATED, NOT EXECUTABLE AS A COMPLETE LAUNCH.')
print('No SDK, ELF, image, export directory, file hashes or lease inspected. No guest started.')
print('The export tag is a shared folder label: QEMU and the QNX driver must match it.')
print('Template add-on (replace $HS_EXPORT only after the strict handoff-command.py gate):')
print('-fsdev local,id=hostshare,path=$HS_EXPORT,security_model=none,readonly=on')
print(shlex.join(['-device','virtio-9p-pci,fsdev=hostshare,mount_tag='+args.tag+',disable-legacy=on']))
print('Guest-side template, NOT executed:')
print(shlex.join(['/data/hostshare','--pci-line','--mount','--tag',args.tag,'--mountpoint',args.mountpoint]))
print('For real inputs use handoff-command.py: unchanged strict source/ELF/stock/export validation is mandatory.')
