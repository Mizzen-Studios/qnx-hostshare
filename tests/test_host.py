import unittest,struct,random
from hostshare.transport import capabilities,negotiate,mount_tag,OneQueue,VERSION_1
from hostshare.protocol import encode,decode,NOTAG,NOFID

def pci():
    b=bytearray(256);b[6]=16;b[0x34]=0x40
    for at,nxt,kind,size,off,length in [(0x40,0x54,1,16,0,56),(0x54,0x68,2,20,128,16),(0x68,0x78,3,16,256,1),(0x78,0,4,16,512,32)]:
        struct.pack_into('<BBBBB3xII',b,at,9,nxt,size,kind,0,off,length)
        if kind==2:struct.pack_into('<I',b,at+16,4)
    return b

class TransportTests(unittest.TestCase):
    def test_modern_capabilities(self):
        r=capabilities(pci(),{0:4096});self.assertEqual(r[2].notify_multiplier,4)
    def test_cycle(self):
        b=pci();b[0x79]=0x40
        with self.assertRaises(ValueError):capabilities(b,{0:4096})
    def test_short_bar(self):
        with self.assertRaises(ValueError):capabilities(pci(),{0:512})
    def test_truncated_vendor(self):
        b=pci();b[0x42]=255
        with self.assertRaises(ValueError):capabilities(b,{0:4096})
    def test_alignment(self):
        b=pci();b[0x34]=0x41
        with self.assertRaises(ValueError):capabilities(b,{0:4096})
    def test_features(self):
        self.assertEqual(negotiate(VERSION_1|1|16),VERSION_1|1)
        for f in (0,1,VERSION_1):
            with self.assertRaises(ValueError):negotiate(f)
    def test_mount_tag(self):
        self.assertEqual(mount_tag(bytes.fromhex('0600663074657374')),'f0test')
        for b in (b'',b'\xff\xffa',b'\x01\x00\x00'):
            with self.assertRaises(ValueError):mount_tag(b)
    def test_queue_pulse(self):
        pulses=[];q=OneQueue(8,pulses.append);t=q.submit(b'request',256)
        with self.assertRaises(RuntimeError):q.submit(b'other',256)
        with self.assertRaises(ValueError):q.complete(t+1,b'bad')
        with self.assertRaises(ValueError):q.complete(t,b'x'*257)
        self.assertEqual(q.complete(t,b'reply'),b'reply');self.assertEqual(pulses,[t])
        with self.assertRaises(ValueError):q.complete(t,b'reply')

class ProtocolTests(unittest.TestCase):
    def test_independent_version_vector(self):
        raw=bytes.fromhex('1500000064ffff0020000008003950323030302e4c')
        self.assertEqual(encode(100,NOTAG,version='9P2000.L',**{'msize':8192}),raw)
        self.assertEqual(decode(raw)[2]['version'],'9P2000.L')
    def test_roundtrips(self):
        cases=[(104,dict(fid=1,uname='test',aname='',n_uname=1000)),(105,dict(qids=[(128,2,3)])),(108,dict(oldtag=1)),(109,{}),(110,dict(fid=1,newfid=2,names=['hello'])),(111,dict(qids=[])),(116,dict(fid=2,offset=0,count=20)),(117,dict(data=b'hello')),(120,dict(fid=2)),(121,{}),(7,dict(errno=2))]
        for kind,fields in cases:
            with self.subTest(kind=kind):
                raw=encode(kind,4,**fields);self.assertEqual(decode(raw)[0:2],(kind,4))
    def test_all_truncations(self):
        raw=encode(110,1,fid=1,newfid=2,names=['hello'])
        for i in range(len(raw)):
            with self.assertRaises(ValueError):decode(raw[:i])
    def test_trailing_data(self):
        raw=bytearray(encode(121,1)+b'x');struct.pack_into('<I',raw,0,len(raw))
        with self.assertRaises(ValueError):decode(raw)
    def test_tags_types(self):
        raw=encode(121,5)
        with self.assertRaises(ValueError):decode(raw,expected_tag=6)
        with self.assertRaises(ValueError):decode(raw,expected_type=117)
        with self.assertRaises(ValueError):encode(121,NOTAG)
    def test_fid_count_bounds(self):
        for f in (-1,NOFID,1<<32):
            with self.assertRaises(ValueError):encode(120,1,fid=f)
        with self.assertRaises(ValueError):encode(110,1,fid=1,newfid=2,names=['..'])
        with self.assertRaises(ValueError):encode(117,1,256,data=b'x'*246)
    def test_inconsistent_read_count(self):
        raw=bytearray(encode(117,1,data=b'abc'));struct.pack_into('<I',raw,7,4)
        with self.assertRaises(ValueError):decode(raw)
    def test_mock_queue_exchange(self):
        q=OneQueue(8,lambda _:None);raw=encode(116,12,fid=2,offset=0,count=5);token=q.submit(raw,8192)
        kind,tag,fields=decode(q.pending[1]);self.assertEqual(fields['count'],5)
        result=q.complete(token,encode(117,tag,data=b'hello'))
        self.assertEqual(decode(result,expected_tag=12,expected_type=117)[2]['data'],b'hello')
    def test_seeded_malformed_frames(self):
        rng=random.Random(20261112)
        for _ in range(1000):
            raw=rng.randbytes(rng.randrange(0,300))
            try:decode(raw,256)
            except ValueError:pass
            else:self.fail('random invalid frame accepted')

if __name__=='__main__':unittest.main()
