"""Validate existing artifacts/export and print a read-only QEMU add-on. Never launches."""
import argparse,json,shlex
from pathlib import Path
from handoff_preflight import config,export_directory,binding
from stock_pin import load_stock_pin,verify_stock_files
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--tag',default='f0test');p.add_argument('--mountpoint',default='/mnt/host')
p.add_argument('--export',dest='export_path',type=Path,required=True)
p.add_argument('--elf',type=Path,required=True);p.add_argument('--manifest',type=Path,required=True)
p.add_argument('--ifs',type=Path,required=True);p.add_argument('--disk',type=Path,required=True);p.add_argument('--stock-pin',type=Path,required=True)
o=p.parse_args();config(o.tag,o.mountpoint);export_directory(o.export_path)
binding(Path(__file__).resolve().parents[1],o.elf,o.manifest)
verify_stock_files(o.ifs,o.disk,load_stock_pin(o.stock_pin))
print('# Add to your already bounded, leased stock QEMU command; no launch performed:')
print(shlex.join(['-fsdev','local,id=hostshare,path='+str(o.export_path)+',security_model=none,readonly=on','-device','virtio-9p-pci,fsdev=hostshare,mount_tag='+o.tag+',disable-legacy=on']))
print('# In QNX, after transferring this exact verified ELF to /data/hostshare:')
print(shlex.join(['/data/hostshare','--pci-line','--mount','--tag',o.tag,'--mountpoint',o.mountpoint]))
