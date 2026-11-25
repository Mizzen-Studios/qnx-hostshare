"""HS-local acknowledged staging + actual guest byte readback. No guest hasher.
Canonical vendor remains immutable. This adapter is NOT native-accepted yet.
"""
import base64,hashlib,re,time,uuid
from recording_transport import match_lines

def parse_readback(raw,begin,end):
    lines=match_lines(raw)
    if lines.count(begin)!=1 or lines.count(end)!=1:raise ValueError('readback framing')
    a,b=lines.index(begin),lines.index(end)
    if a>=b:raise ValueError('readback marker order')
    fields=lines[a+1:b]
    if any(not re.fullmatch(rb'(?:[ \t]*[a-f0-9]{2})*[ \t]*',line) for line in fields):raise ValueError('readback nonhex')
    return bytes.fromhex(b' '.join(fields).decode('ascii'))

def transfer(payload,destination,exchange,log,*,readback,chunk_bytes=64,timeout=20,budget=900,clock=time.monotonic):
    if not re.fullmatch(r'/(?:tmp|data/hostshare|boot)/[A-Za-z0-9_-]{1,24}',destination):raise ValueError('destination')
    if not 1<=chunk_bytes<=64 or not 0<timeout<=30 or not 0<budget<=900:raise ValueError('bounds')
    nonce=uuid.uuid4().hex;deadline=clock()+budget;seq=0;maximum=0
    def request(body,offset):
        nonlocal seq,maximum
        marker=('RT_%s_%d_%d'%(nonce,seq,offset)).encode()
        wire=(body+" && printf '\\nRT_%s_%s_%s\\n' '"+nonce+"' '"+str(seq)+"' '"+str(offset)+"'\n").encode()
        if len(wire)>512:raise ValueError('command bound')
        maximum=max(maximum,len(wire));remaining=deadline-clock()
        if remaining<=0:raise TimeoutError('global transfer deadline')
        log({'event':'send','seq':seq,'offset':offset,'raw_b64':base64.b64encode(wire).decode(),'mono':clock()})
        reply=exchange(wire,marker,min(timeout,remaining))
        log({'event':'reply','seq':seq,'raw_b64':base64.b64encode(reply).decode(),'mono':clock()})
        acks=[line for line in match_lines(reply) if re.fullmatch(rb'RT_[a-f0-9]{32}_\d+_\d+',line)]
        if acks!=[marker]:raise ValueError('missing/duplicate/stale ack')
        if clock()>=deadline:raise TimeoutError('global transfer deadline')
        seq+=1
    try:
        request(': > '+destination,0)
        for i in range(0,len(payload),chunk_bytes):
            block=payload[i:i+chunk_bytes];octal=''.join('\\%03o'%b for b in block)
            request("printf '"+octal+"' >> "+destination,i+len(block))
        remaining=min(60,deadline-clock())
        if remaining<=0:raise TimeoutError('readback budget')
        observed=readback(destination,remaining)
        if observed!=payload:raise ValueError('actual guest byte readback mismatch')
        if clock()>=deadline:raise TimeoutError('global transfer deadline')
        result={'bytes':len(observed),'sha256':hashlib.sha256(observed).hexdigest(),'acks':seq,'max_command_bytes':maximum,
                'integrity_method':'guest-od-exact-byte-compare-host-sha256','guest_hash_applet_used':False,
                'verified_before_execution':True,'nonce':nonce,'chunk_bytes':chunk_bytes,'budget_seconds':budget}
        log({'event':'terminal','status':'VERIFIED','result':result,'mono':clock()});return result
    except BaseException as error:
        log({'event':'terminal','status':'FAILED','seq':seq,'error':repr(error),'mono':clock()});raise
