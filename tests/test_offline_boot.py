"""HOST-only bounded offline admission negatives; no licensed image construction."""
import hashlib,json,struct,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import offline_boot as o
from qnx6_inspect import BootFS
class Offline(unittest.TestCase):
 def setUp(self):
  (ROOT/'.local').mkdir(exist_ok=True);self.tmp=tempfile.TemporaryDirectory(dir=ROOT/'.local');self.p=Path(self.tmp.name)
 def tearDown(self):self.tmp.cleanup()
 def disk(self):
  b=bytearray(512*10);b[510:512]=bytes([85,170])
  for i in range(3):
   at=446+16*i;b[at]=128 if not i else 0;b[at+4]=177+i;struct.pack_into('<II',b,at+8,1+i*3,3)
  p=self.p/'disk';p.write_bytes(b);return p
 def test_mbr_valid_and_slice(self):
  p=self.disk();a=o.mbr(p);self.assertEqual(a[1],{'type':178,'start':4,'count':3});self.assertEqual(o.slice_hash(p,a[1]),hashlib.sha256(bytes(1536)).hexdigest())
 def test_mbr_negative_matrix(self):
  for at,value in [(510,0),(450,176),(446,0),(466,177),(494,1)]:
   p=self.disk();b=bytearray(p.read_bytes());b[at]=value;p.write_bytes(b)
   with self.assertRaises(ValueError):o.mbr(p)
  for start,count in [(2,3),(4,0),(4,99)]:
   p=self.disk();b=bytearray(p.read_bytes());struct.pack_into('<II',b,470,start,count);p.write_bytes(b)
   with self.assertRaises(ValueError):o.mbr(p)
 def test_symlink_and_size_caps(self):
  p=self.disk();q=self.p/'link';q.symlink_to(p)
  with self.assertRaises(ValueError):o.regular(q)
  with self.assertRaises(ValueError):BootFS(q)
  with p.open('r+b') as f:f.truncate(512*1024*1024+1)
  with self.assertRaises(ValueError):BootFS(p)
 def test_inspector_magic_crc_and_tree_caps(self):
  p=self.disk()
  with self.assertRaises(ValueError):BootFS(p)
  f=BootFS.__new__(BootFS);f.blocks=100000;f.blocksize=4096
  for node in [(1,(0,)*16,3),(17*1024*1024,(0,)*16,0)]:
   with self.assertRaises(ValueError):f.content(node)
 def test_buildfile_required_modes_and_capacity(self):
  s=o.buildfile('/stage/ifs','/stage/driver','/stage/hook')
  self.assertIn('[num_sectors=*4096]',s);self.assertIn('[-optional]',s);self.assertNotIn('+optional',s);self.assertIn('perms=0755] /hsd=',s);self.assertIn('perms=0644] /onboot=',s)
  self.assertEqual(len(s.splitlines()),5)
  for bad in ['/bad path','/stage/../secret','relative']:
   with self.assertRaises(ValueError):o.buildfile(bad,'/driver','/hook')
 def test_original_pin_mismatch_before_inspection(self):
  p=self.disk()
  with self.assertRaisesRegex(ValueError,'original pin'):o.inspect(p,p,p,p,'f0test','/mnt/host')
 def test_native_prepared_pin_never_offline(self):
  p=self.disk();pin=self.p/'pin';pin.write_text(json.dumps({'schema':'hostshare.boot-overlay.v1','sealed':True}))
  with self.assertRaisesRegex(ValueError,'offline pin fields'):o.validate(pin,p,p,p,p,'f0test','/mnt/host')
 def test_runner_distinct_lane_and_passive_gate(self):
  s=(ROOT/'tools/run-native-suite.py').read_text();self.assertIn('offline_boot.validate_overlay',s);self.assertIn('else:boot_handoff.validate_pin',s);self.assertIn('ready_before_any_host_command',s)
