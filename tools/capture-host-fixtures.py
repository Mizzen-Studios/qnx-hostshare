"""Synthetic host mock capture, never QEMU/native evidence."""
import json,hashlib
from pathlib import Path
from hostshare.protocol import encode
from hostshare.transport import OneQueue
request=encode(116,12,fid=2,offset=0,count=5)
q=OneQueue(8,lambda _:None);token=q.submit(request,8192)
response=q.complete(token,encode(117,12,data=b'hello'))
result={'provenance':'synthetic in-process mock, not live server/QNX/QEMU capture','frames':[{'direction':d,'hex':b.hex(),'sha256':hashlib.sha256(b).hexdigest()} for d,b in [('request',request),('response',response)]]}
Path('docs/acceptance/followup-20261112/mock-frames.json').write_text(json.dumps(result,indent=2)+'\n')
