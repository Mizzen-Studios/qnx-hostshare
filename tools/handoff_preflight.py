"""Read-only handoff validation. No guest launch or credential access."""
import hashlib,json,re,stat
from pathlib import Path

def config(tag,mountpoint):
    if not re.fullmatch(r'[A-Za-z0-9_.-]{1,31}',tag) or tag in ('.','..'):
        raise ValueError('invalid export tag')
    parts=mountpoint.split('/')
    if (not mountpoint.startswith('/mnt/') or len(mountpoint)>255 or
        any(not re.fullmatch(r'[A-Za-z0-9_.-]{1,63}',p) or p in ('.','..') for p in parts[1:])):
        raise ValueError('invalid mountpoint')
    return tag,mountpoint

def export_directory(path):
    path=Path(path)
    if not path.is_absolute() or any(part in ('.','..') for part in path.parts) or not re.fullmatch(r'/[A-Za-z0-9_./-]+',str(path)):
        raise ValueError('export needs absolute QEMU-safe path')
    for p in (path,*path.parents):
        if p.is_symlink(): raise ValueError('symlink export ancestor')
    if not path.is_dir(): raise ValueError('missing export directory')
    for p in path.rglob('*'):
        mode=p.lstat().st_mode
        if not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
            raise ValueError('only ordinary files/directories in export')
    return path

def binding(root,elf,manifest):
    root=Path(root); elf=Path(elf)
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    data=json.loads(Path(manifest).read_text())
    expected={str(p.relative_to(root)) for folder in ('core','native') for p in (root/folder).glob('*.[ch]')}
    if set(data['files'])!=expected: raise ValueError('incomplete source binding')
    if digest(elf)!=data['elf_sha256']: raise ValueError('ELF mismatch')
    for name in expected:
        if digest(root/name)!=data['files'][name]: raise ValueError('source mismatch: '+name)
    return data
