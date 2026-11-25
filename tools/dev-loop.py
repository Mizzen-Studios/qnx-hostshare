"""Build client on configured SDK host; no QEMU, install, login or run authority."""
import argparse,hashlib,json,os,re,shutil,subprocess
from pathlib import Path

def build(output,sdk_env=None,host_test=False):
    root=Path(__file__).resolve().parents[1];source=root/'examples/developer-loop.c';output=Path(output).resolve()
    if root not in output.parents or any(p.is_symlink() for p in [output,*output.parents]):raise ValueError('workspace-local nonsymlink output required')
    if host_test and sdk_env:raise ValueError('ambiguous target')
    if not host_test and (not sdk_env or not Path(sdk_env).is_file()):raise ValueError('existing SDK environment required')
    output.mkdir(parents=True,exist_ok=False);elf=output/'loop-app';log=output/'build.txt'
    target='HOST_ONLY' if host_test else 'QNX_x86_64'
    flags=['-std=c11','-Wall','-Wextra','-Werror','-pedantic',str(source),'-o',str(elf)]
    if host_test:command=['cc',*flags]
    else:command=['bash','-c','set -e; source "$1" >/dev/null; shift; exec qcc -Vgcc_ntox86_64 "$@"','hs-build',str(Path(sdk_env).resolve()),*flags]
    compiler=shutil.which('cc') if host_test else subprocess.check_output(['bash','-c','set -e; source "$1" >/dev/null; command -v qcc','hs-compiler',str(Path(sdk_env).resolve())],text=True,timeout=10).strip()
    if not compiler or not Path(compiler).is_file():raise ValueError('compiler unavailable')
    compiler_hash=hashlib.sha256(Path(compiler).read_bytes()).hexdigest()
    receipt={'compiler':compiler,'compiler_sha256':compiler_hash,'sdk_env_sha256':hashlib.sha256(Path(sdk_env).read_bytes()).hexdigest() if sdk_env else None,'schema':'hostshare.dev-build.v1','target':target,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'command':command,'status':'FAIL'}
    try:
        with log.open('w') as f:subprocess.run(command,stdout=f,stderr=subprocess.STDOUT,timeout=120,check=True)
        receipt.update(status='BUILT',elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest())
    finally:(output/'build.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return receipt

def validate(elf,manifest,root):
    data=json.loads(Path(manifest).read_text());h=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    if data.get('schema')!='hostshare.dev-build.v1' or data.get('target')!='QNX_x86_64' or data.get('status')!='BUILT':raise ValueError('not completed QNX build')
    if not re.fullmatch(r'[a-f0-9]{64}',data.get('compiler_sha256','')) or not re.fullmatch(r'[a-f0-9]{64}',data.get('sdk_env_sha256','')):raise ValueError('missing compiler provenance')
    if Path(elf).is_symlink() or h(elf)!=data.get('elf_sha256') or h(Path(root)/'examples/developer-loop.c')!=data.get('source_sha256'):raise ValueError('client build/source mismatch')
    return data

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);p.add_argument('--sdk-env',type=Path);p.add_argument('--host-test',action='store_true');o=p.parse_args()
    print(json.dumps(build(o.out,o.sdk_env,o.host_test)))
