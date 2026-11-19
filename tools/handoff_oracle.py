"""Independent byte oracle for actual POSIX-client transcript (not guest hashes)."""
import re

def verify(text,corpus):
    cases={}
    for m in re.finditer(r'^HS_CASE ([01]) (empty|one|4KiB|1MiB) (\d+) (\d+) (\d+) ([0-9a-f]*)-$',text,re.M):
        client,name,offset,count,n,hexbytes=m.groups()
        key=(int(client),name,int(offset),int(count))
        if key in cases: raise ValueError('duplicate byte case')
        actual=bytes.fromhex(hexbytes);expected=(corpus/name).read_bytes()[int(offset):int(offset)+int(count)]
        if len(actual)!=int(n) or actual!=expected: raise ValueError('byte mismatch')
        cases[key]=True
    expected={(c,n,o,k) for c in range(2) for n in ('empty','one','4KiB','1MiB') for o in (0,1,3999,4000,4095,4096,1048575,1048576,1048581) for k in (0,1,17,257)}
    if set(cases)!=expected: raise ValueError('missing byte cases')
    names={p.name for p in corpus.iterdir()}
    for client in range(2):
        for rewind in range(2):
            lines=re.findall(r'^HS_DIR '+str(client)+' '+str(rewind)+r' (.+)$',text,re.M)
            normal=[n for n in lines if n not in ('.','..')]
            if len(normal)!=len(names) or set(normal)!=names: raise ValueError('directory mismatch/duplicate')
            if text.splitlines().count('HS_DIR_END %d %d'%(client,rewind))!=1: raise ValueError('directory incomplete')
    denials=re.findall(r'^HS_DENY (open[0-3]|create) (-?\d+) (\d+)$',text,re.M)
    if len(denials)!=5 or {d[0] for d in denials}!={'open0','open1','open2','open3','create'} or any(int(fd)!=-1 or int(e)==0 for _,fd,e in denials): raise ValueError('mutation not denied')
    if text.splitlines().count('HS_CONFORMANCE_COMPLETE')!=1: raise ValueError('missing completion')
    return {'byte_cases':len(cases),'directory_passes':4,'denied_opens':5}
