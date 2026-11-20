"""Portable HOST-tested acknowledged transport; never executes or retries payloads."""
import base64
import hashlib
import re
import time
import uuid
CSI = re.compile(rb'\x1b\[[0-?]*[ -/]*[@-~]')
def match_lines(raw):
    """CSI-normalized matching view ONLY; original raw bytes are retained."""
    return CSI.sub(b'', raw.replace(b'\r', b'')).split(b'\n')
def write_all(write, wire):
    offset = 0
    while offset < len(wire):
        n = write(wire[offset:])
        if not isinstance(n, int) or n <= 0 or n > len(wire)-offset:
            raise RuntimeError('invalid/closed partial write')
        offset += n

def transfer(payload, destination, exchange, log, *, nonce=None, chunk_bytes=64,
             timeout=20, budget=900, toolbox='/proc/boot/toybox', clock=time.monotonic):
    """exchange must honor deadline for writes/reads, log raw RX even on failure.
    log appends durably. No payload chmod/exec or retransmission occurs here.
    """
    if not re.fullmatch(r'/(?:tmp|data/hostshare)/[A-Za-z0-9_-]{1,24}', destination):
        raise ValueError('unsafe/long destination')
    if not 1 <= chunk_bytes <= 64 or not 0 < timeout <= 30 or not 0 < budget <= 900:
        raise ValueError('chunk/timeout/budget bound')
    if toolbox not in ('/proc/boot/toybox', 'HOST_TEST'):
        raise ValueError('toolbox')
    nonce = nonce or uuid.uuid4().hex
    if not re.fullmatch('[a-f0-9]{32}', nonce):
        raise ValueError('nonce')
    prefix = '' if toolbox == 'HOST_TEST' else toolbox+' '
    deadline = clock()+budget
    seq = 0
    maximum_wire = 0
    digest = hashlib.sha256(payload).hexdigest()
    def request(body, offset, expected=None):
        nonlocal seq, maximum_wire
        marker = ('RT_%s_%d_%d' % (nonce, seq, offset)).encode()
        command = body+" && printf '\\nRT_%s_%s_%s\\n' '"+nonce+"' '"+str(seq)+"' '"+str(offset)+"'"
        wire = (command+'\n').encode()
        if len(wire) > 512:
            raise ValueError('command exceeds512 bytes')
        maximum_wire = max(maximum_wire, len(wire))
        remaining = deadline-clock()
        if remaining <= 0:
            raise TimeoutError('global transfer budget')
        log({'event':'send','seq':seq,'offset':offset,'raw_b64':base64.b64encode(wire).decode(),'mono':clock()})
        reply = exchange(wire, marker, min(timeout, remaining))
        log({'event':'reply','seq':seq,'raw_b64':base64.b64encode(reply).decode(),'mono':clock()})
        if clock() >= deadline:
            raise TimeoutError('global transfer budget')
        lines = match_lines(reply)
        acks = [line for line in lines if re.fullmatch(rb'RT_[a-f0-9]{32}_\d+_\d+', line)]
        if acks != [marker]:
            raise RuntimeError('missing/duplicate/stale/wrong ack '+str(seq))
        if expected and not expected(lines):
            raise RuntimeError('guest size/hash mismatch')
        seq += 1
    try:
        request(': > '+destination, 0)
        for i in range(0, len(payload), chunk_bytes):
            block = payload[i:i+chunk_bytes]
            octal = ''.join('\\%03o' % x for x in block)
            request("printf '"+octal+"' >> "+destination, i+len(block))
        body = ('RT_H=$('+prefix+'sha256sum '+destination+') && RT_N=$('+prefix+'wc -c < '+destination+
                ') && printf \'\\nRH_'+nonce+' %s\\nRN_'+nonce+' %s\\n\' "$RT_H" "$RT_N"')
        def integrity(lines):
            hashes = [x for x in lines if x.startswith(('RH_'+nonce+' ').encode())]
            sizes = [x for x in lines if x.startswith(('RN_'+nonce+' ').encode())]
            return (len(hashes)==1 and bool(re.fullmatch(('RH_'+nonce+' '+digest+'  '+re.escape(destination)).encode(), hashes[0]))
                    and len(sizes)==1 and bool(re.fullmatch(('RN_'+nonce+r'\s+'+str(len(payload))).encode(), sizes[0])))
        request(body, len(payload), integrity)
        result = {'bytes':len(payload),'sha256':digest,'acks':seq,'verified_before_execution':True,
                  'nonce':nonce,'max_command_bytes':maximum_wire,'chunk_bytes':chunk_bytes,'budget_seconds':budget}
        log({'event':'terminal','status':'VERIFIED','result':result,'mono':clock()})
        return result
    except BaseException as error:
        log({'event':'terminal','status':'FAILED','seq':seq,'error':repr(error),'mono':clock()})
        raise

def redact_payload_commands(text):
    """Sanitized PUBLIC view; private append-only events retain exact raw bytes."""
    text = re.sub(r"printf '%b' '[^']*' >> [^;\n]*", '[OWN ELF COPY REDACTED]', text)
    return re.sub(r"printf '(?:\\[0-7]{3})+' >> [^;\n&]*", '[OWN ELF COPY REDACTED]', text)
