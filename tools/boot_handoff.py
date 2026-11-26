"""Validated one-shot QNX /boot/onboot integration and private overlay provenance."""
import hashlib,json,re,subprocess
from pathlib import Path
from handoff_preflight import config

def hook(tag='f0test',mountpoint='/mnt/host'):
    config(tag,mountpoint)
    return ("#!/bin/sh\n# One start only. No respawn/recovery/restart.\n"
            "[ ! -e /dev/shmem/hs-boot.pid ] || { echo HOSTSHARE_BOOT_PID_COLLISION; exit 1; }\n"
            "/boot/hsd --pci-line --mount --tag "+tag+" --mountpoint "+mountpoint+" &\n"
            "p=$!\necho \"$p\" > /dev/shmem/hs-boot.pid || exit 1\n"
            "echo HOSTSHARE_BOOT_LAUNCHED\n").encode()

def safe_overlay(path):
    raw=str(path);path=Path(path)
    if not path.is_absolute() or not re.fullmatch(r'/[A-Za-z0-9_./-]+',raw) or any(p in ('.','..') for p in raw.split('/')):raise ValueError('overlay path')
    if any(p.is_symlink() for p in (path,*path.parents)):raise ValueError('overlay symlink')
    return path

def overlay_info(path,base):
    path=safe_overlay(path);base=Path(base)
    if not path.is_absolute() or path.is_symlink() or ',' in str(path) or any(c.isspace() for c in str(path)):raise ValueError('overlay path')
    info=json.loads(subprocess.check_output(['qemu-img','info','--output=json',str(path)],text=True))
    if info.get('format')!='qcow2' or info.get('full-backing-filename')!=str(base.resolve()) or info.get('backing-filename-format')!='raw':raise ValueError('overlay backing mismatch')
    return info

def create_overlay(path,base):
    path=safe_overlay(path)
    if path.exists() or path.is_symlink():raise ValueError('overlay collision')
    if not path.parent.is_dir():raise ValueError('overlay parent missing')
    if not re.fullmatch(r'/[A-Za-z0-9_./-]+',str(path)) or '..' in path.parts:raise ValueError('overlay path')
    subprocess.run(['qemu-img','create','-f','qcow2','-F','raw','-b',str(Path(base).resolve()),str(path)],check=True,capture_output=True)
    return overlay_info(path,base)

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def validate_pin(path,pin,base,elf,tag,mountpoint):
    info=overlay_info(path,base);data=json.loads(Path(pin).read_text())
    expected={'schema':'hostshare.boot-overlay.v1','overlay_sha256':digest(path),'base_sha256':digest(base),'elf_sha256':digest(elf),
              'hook_sha256':hashlib.sha256(hook(tag,mountpoint)).hexdigest(),'tag':tag,'mountpoint':mountpoint,'sealed':True}
    if data!=expected:raise ValueError('boot overlay pin mismatch')
    return info
