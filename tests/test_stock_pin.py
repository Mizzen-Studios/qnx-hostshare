"""Host-only tests; never launch QEMU or acquire the native lock."""
import hashlib,importlib.util,json,os,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('stock_pin',ROOT/'tools/stock_pin.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class StockPinTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  (ROOT/'.local').mkdir(exist_ok=True)
 def check_pin(self,data):
  with tempfile.TemporaryDirectory(dir=ROOT/'.local') as d:
   p=Path(d)/'pin.json';p.write_text(data);return module.load_stock_pin(p)
 def test_valid_exact_schema(self):
  self.assertEqual(self.check_pin(json.dumps(module.HISTORICAL_STOCK)),module.HISTORICAL_STOCK)
 def test_bad_schemas_fail_closed(self):
  good=module.HISTORICAL_STOCK
  cases=['null','[]','{}','{',json.dumps({'ifs.bin':good['ifs.bin']}),json.dumps(dict(good,extra='a')),
         json.dumps(dict(good,**{'ifs.bin':None})),json.dumps(dict(good,**{'ifs.bin':'0'*64})),
         json.dumps(dict(good,**{'ifs.bin':'not-a-real-hash'})),json.dumps(dict(good,**{'ifs.bin':good['ifs.bin'].upper()})),
         json.dumps(good)[:-1]+',"ifs.bin":"'+good['ifs.bin']+'"}', ' '*4097]
  for case in cases:
   with self.subTest(case=case[:40]),self.assertRaises((ValueError,TypeError)):self.check_pin(case)
 def test_invalid_pin_exits_before_guest_prerequisites(self):
  with tempfile.TemporaryDirectory(dir=ROOT/'.local') as d:
   p=Path(d)/'bad.json';p.write_text('{}')
   result=subprocess.run(['python3',str(ROOT/'tools/run-native-suite.py'),'--image-kind','stock','--run-id','host-test','--stock-pin',str(p)],capture_output=True,text=True,env={'PATH':os.environ['PATH']})
   self.assertNotEqual(result.returncode,0);self.assertIn('stock pin requires',result.stderr)
 def test_stock_only_option(self):
  result=subprocess.run(['python3',str(ROOT/'tools/run-native-suite.py'),'--image-kind','historical','--run-id','host-test','--stock-pin','missing'],capture_output=True,text=True)
  self.assertEqual(result.returncode,2)
 def test_shell_absolute_lock_validation_without_systemd(self):
  env={'PATH':os.environ['PATH'],'HS_ELF':__file__,'HS_IFS':__file__,'HS_DISK':__file__,'HS_BUILD_MANIFEST':__file__,'HS_LOCK':'relative'}
  result=subprocess.run(['sh',str(ROOT/'tools/run-native-suite.sh')],capture_output=True,text=True,env=env)
  self.assertEqual(result.returncode,2);self.assertIn('HS_LOCK must be absolute',result.stderr)

 def test_real_file_hashes_and_mismatch(self):
  with tempfile.TemporaryDirectory(dir=ROOT/'.local') as d:
   image=Path(d)/'ifs.bin';disk=Path(d)/'disk-qemu'
   image.write_bytes(b'synthetic image');disk.write_bytes(b'synthetic disk')
   pin={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [image,disk]}
   module.verify_stock_files(image,disk,pin)
   disk.write_bytes(b'changed')
   with self.assertRaises(ValueError):module.verify_stock_files(image,disk,pin)
