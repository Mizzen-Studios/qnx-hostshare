"""Host-only strict 9P2000.L framing subset, not filesystem operations."""
import struct
NOTAG=0xffff
NOFID=0xffffffff
VERSION='9P2000.L'
TYPES={100,101,104,105,108,109,110,111,116,117,120,121,7}

def integer(value, bits):
    if not isinstance(value,int) or isinstance(value,bool) or not 0 <= value < 1<<bits:
        raise ValueError('integer outside wire width')
    return value

def string(value):
    data=value.encode('utf-8',errors='strict')
    if len(data)>65535 or chr(0) in value:
        raise ValueError('invalid protocol string')
    return struct.pack('<H',len(data))+data

def fid(value):
    integer(value,32)
    if value==NOFID: raise ValueError('NOFID not a live fid')
    return struct.pack('<I',value)

class Reader:
    def __init__(self,data): self.data,self.at=data,0
    def take(self,size):
        if size<0 or size>len(self.data)-self.at: raise ValueError('truncated body')
        result=self.data[self.at:self.at+size]; self.at+=size; return result
    def number(self,fmt): return struct.unpack('<'+fmt,self.take(struct.calcsize('<'+fmt)))[0]
    def text(self):
        text=self.take(self.number('H')).decode('utf-8',errors='strict')
        if chr(0) in text: raise ValueError('NUL string')
        return text
    def livefid(self):
        value=self.number('I'); fid(value); return value
    def done(self):
        if self.at!=len(self.data): raise ValueError('trailing bytes')

def body(kind, fields):
    if kind in (100,101):
        m=integer(fields['msize'],32)
        if not 256<=m<=1048576 or fields['version']!=VERSION: raise ValueError('unsupported negotiation')
        return struct.pack('<I',m)+string(VERSION)
    if kind==108: return struct.pack('<H',integer(fields['oldtag'],16))
    if kind in (109,121): return b''
    if kind==120: return fid(fields['fid'])
    if kind==7: return struct.pack('<I',integer(fields['errno'],32))
    if kind==110:
        names=fields['names']
        if len(names)>16 or any(not n or '/' in n or n in ('.','..') for n in names): raise ValueError('invalid walk names')
        return fid(fields['fid'])+fid(fields['newfid'])+struct.pack('<H',len(names))+b''.join(string(n) for n in names)
    if kind==116: return fid(fields['fid'])+struct.pack('<QI',integer(fields['offset'],64),integer(fields['count'],32))
    if kind==117:
        data=bytes(fields['data']); return struct.pack('<I',len(data))+data
    if kind==104:
        afid=integer(fields.get('afid',NOFID),32)
        return fid(fields['fid'])+struct.pack('<I',afid)+string(fields['uname'])+string(fields['aname'])+struct.pack('<I',integer(fields['n_uname'],32))
    if kind in (105,111):
        qids=fields['qids']
        if kind==105 and len(qids)!=1 or kind==111 and len(qids)>16: raise ValueError('invalid qid count')
        raw=b''.join(struct.pack('<BIQ',integer(q[0],8),integer(q[1],32),integer(q[2],64)) for q in qids)
        return (struct.pack('<H',len(qids)) if kind==111 else b'')+raw
    raise ValueError('unsupported type')

def encode(kind,tag,frame_limit=8192,**fields):
    integer(tag,16)
    if not 256<=frame_limit<=1048576 or kind not in TYPES or ((kind in (100,101)) != (tag==NOTAG)):
        raise ValueError('invalid type, tag or msize')
    payload=body(kind,fields)
    if len(payload)+7>frame_limit: raise ValueError('frame exceeds msize')
    return struct.pack('<IBH',len(payload)+7,kind,tag)+payload

def decode(frame,msize=8192,expected_tag=None,expected_type=None):
    if not 256<=msize<=1048576 or not 7<=len(frame)<=msize: raise ValueError('invalid frame bounds')
    length,kind,tag=struct.unpack_from('<IBH',frame)
    if length!=len(frame) or kind not in TYPES or ((kind in (100,101)) != (tag==NOTAG)):
        raise ValueError('invalid header')
    if expected_tag is not None and tag!=expected_tag: raise ValueError('unexpected tag')
    if expected_type is not None and kind not in (expected_type,7): raise ValueError('unexpected response')
    r=Reader(frame[7:]); fields={}
    if kind in (100,101): fields={'msize':r.number('I'),'version':r.text()}
    elif kind==108: fields={'oldtag':r.number('H')}
    elif kind==120: fields={'fid':r.livefid()}
    elif kind==7: fields={'errno':r.number('I')}
    elif kind==110:
        f,n=r.livefid(),r.livefid(); count=r.number('H')
        if count>16: raise ValueError('walk too long')
        fields={'fid':f,'newfid':n,'names':[r.text() for _ in range(count)]}
    elif kind==116: fields={'fid':r.livefid(),'offset':r.number('Q'),'count':r.number('I')}
    elif kind==117: fields={'data':r.take(r.number('I'))}
    elif kind==104: fields={'fid':r.livefid(),'afid':r.number('I'),'uname':r.text(),'aname':r.text(),'n_uname':r.number('I')}
    elif kind in (105,111):
        count=r.number('H') if kind==111 else 1
        if count>16: raise ValueError('too many qids')
        fields={'qids':[(r.number('B'),r.number('I'),r.number('Q')) for _ in range(count)]}
    r.done()
    if body(kind,fields)!=frame[7:]: raise ValueError('noncanonical body')
    return kind,tag,fields
