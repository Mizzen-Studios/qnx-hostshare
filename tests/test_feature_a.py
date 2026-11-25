"""Feature A HOST tests. No SDK/QEMU/lease/native execution."""
import ast,hashlib,importlib.util,json,os,re,select,subprocess,sys,tempfile,time,unittest,uuid
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import boot_handoff as boot
from serial_readback import transfer,parse_readback
from recording_transport import match_lines
spec=importlib.util.spec_from_file_location('dev_build',ROOT/'tools/dev-loop.py');dev=importlib.util.module_from_spec(spec);spec.loader.exec_module(dev)
class FeatureA(unittest.TestCase):
 def localtemp(self):
  (ROOT/'.local').mkdir(exist_ok=True)
  return tempfile.TemporaryDirectory(dir=ROOT/'.local')
 def trial(self,payload,fault=None,budget=900):
  child=subprocess.Popen(['/bin/sh'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
  path=Path('/tmp/hs-'+uuid.uuid4().hex[:16]);logs=[];clock=[0.0]
  def exchange(wire,marker,timeout):
   self.assertLessEqual(len(wire),512);self.assertEqual(wire.count(b'\n'),1)
   child.stdin.write(wire);child.stdin.flush();raw=b'';deadline=time.monotonic()+2
   while time.monotonic()<deadline:
    if select.select([child.stdout],[],[],.005)[0]:raw+=os.read(child.stdout.fileno(),65536)
    if marker in match_lines(raw):
     clock[0]+=1
     if fault=='stale':return raw.replace(marker,b'RT_'+b'0'*32+b'_0_0')
     if fault=='duplicate':return raw+marker+b'\n'
     if fault=='echo':return wire
     return raw.replace(marker,b'\x1b[?7h'+marker)
   raise TimeoutError('HOST pipe timeout')
  def readback(destination,timeout):
   self.assertGreater(timeout,0)
   if fault=='missingod':raise RuntimeError('HOST unavailable od')
   if fault=='corrupt':Path(destination).write_bytes(b'corrupted')
   raw=subprocess.check_output(['od','-An','-v','-tx1',destination])
   framed=b'BEGIN\n'+raw+b'END\n'
   return parse_readback(framed,b'BEGIN',b'END')
  try:
   result=transfer(payload,str(path),exchange,logs.append,readback=readback,budget=budget,clock=lambda:clock[0])
   self.assertEqual(result['sha256'],hashlib.sha256(payload).hexdigest());self.assertTrue(result['verified_before_execution'])
   self.assertFalse(result['guest_hash_applet_used']);self.assertEqual(logs[-1]['status'],'VERIFIED')
   return result
  except BaseException:
   self.assertEqual(logs[-1]['status'],'FAILED');raise
  finally:child.terminate();child.wait(3);child.stdin.close();child.stdout.close();path.unlink(missing_ok=True)
 def test_full51528_exact_guest_view_not_acks(self):
  result=self.trial((bytes(range(256))*202)[:51528]);self.assertEqual(result['acks'],807)
 def test_corrupt_bytes_never_verified(self):
  with self.assertRaises(ValueError):self.trial(b'known bytes',fault='corrupt')
 def test_missing_od_fails_closed(self):
  with self.assertRaises(RuntimeError):self.trial(b'known bytes',fault='missingod')
 def test_stale_ack_denied(self):
  with self.assertRaises(ValueError):self.trial(b'x',fault='stale')
 def test_duplicate_ack_denied(self):
  with self.assertRaises(ValueError):self.trial(b'x',fault='duplicate')
 def test_echo_is_not_ack(self):
  with self.assertRaises(ValueError):self.trial(b'x',fault='echo')
 def test_total_budget_not_per_chunk_infinity(self):
  with self.assertRaises(TimeoutError):self.trial(b'x'*128,budget=2)
 def test_empty_and_binary(self):
  for data in (b'',bytes(range(256)),b"'\\\r\n$()"):
   self.trial(data)
 def test_readback_parser_negatives(self):
  for data in (b'BEGIN\nzz\nEND\n',b'BEGIN\n00\n',b'BEGIN\n00\nEND\nBEGIN\n',b'END\nBEGIN\n'):
   with self.assertRaises(ValueError):parse_readback(data,b'BEGIN',b'END')
 def test_hook_default_and_custom_grammar(self):
  for tag,path in [('f0test','/mnt/host'),('dev-inputs','/mnt/dev-inputs')]:
   s=boot.hook(tag,path).decode();self.assertIn('--tag '+tag,s);self.assertIn('--mountpoint '+path,s)
   self.assertEqual(s.count('/boot/hsd --'),1);self.assertNotIn('while ',s);self.assertNotIn('exec ',s)
  with self.assertRaises(ValueError):boot.hook('bad;tag','/mnt/host')
  with self.assertRaises(ValueError):boot.hook('good','/mnt/../etc')
 def test_hook_real_host_shell_starts_once_only(self):
  with self.localtemp() as tmp:
   p=Path(tmp);pid=p/'pid';count=p/'count';driver=p/'driver'
   driver.write_text('#!/bin/sh\necho started >> '+str(count)+'\necho HOST_ONLY_FAKE_MOUNT\n');driver.chmod(0o700)
   script=boot.hook().decode().replace('/boot/hsd',str(driver)).replace('/dev/shmem/hs-boot.pid',str(pid))
   first=subprocess.run(['/bin/sh','-c',script],capture_output=True,text=True);self.assertEqual(first.returncode,0)
   second=subprocess.run(['/bin/sh','-c',script],capture_output=True,text=True);self.assertNotEqual(second.returncode,0)
   self.assertEqual(count.read_text().splitlines(),['started'])
 def test_overlay_backing_collision_symlink_and_pin(self):
  with self.localtemp() as tmp:
   p=Path(tmp);base=p/'base';base.write_bytes(b'HOST_ONLY_BASE');overlay=p/'disk.qcow2';overlay.write_bytes(b'HOST_ONLY_OVERLAY');elf=p/'driver';elf.write_bytes(b'HOST_ONLY_ELF')
   info={'format':'qcow2','full-backing-filename':str(base.resolve()),'backing-filename-format':'raw'}
   with patch.object(boot.subprocess,'check_output',return_value=json.dumps(info)):
    self.assertEqual(boot.overlay_info(overlay,base)['format'],'qcow2')
    pin={'schema':'hostshare.boot-overlay.v1','overlay_sha256':boot.digest(overlay),'base_sha256':boot.digest(base),'elf_sha256':boot.digest(elf),'hook_sha256':hashlib.sha256(boot.hook()).hexdigest(),'tag':'f0test','mountpoint':'/mnt/host','sealed':True}
    pinpath=p/'pin.json';pinpath.write_text(json.dumps(pin));boot.validate_pin(overlay,pinpath,base,elf,'f0test','/mnt/host')
    overlay.write_bytes(b'changed')
    with self.assertRaises(ValueError):boot.validate_pin(overlay,pinpath,base,elf,'f0test','/mnt/host')
   with self.assertRaises(ValueError):boot.create_overlay(overlay,base)
   (p/'link').symlink_to(p,target_is_directory=True)
   with self.assertRaises(ValueError):boot.safe_overlay(p/'link/new')
   info['full-backing-filename']='/untrusted/base'
   with patch.object(boot.subprocess,'check_output',return_value=json.dumps(info)):
    with self.assertRaises(ValueError):boot.overlay_info(overlay,base)
 def test_real_host_build_and_run_not_native(self):
  with self.localtemp() as tmp:
   p=Path(tmp);receipt=dev.build(p/'build',host_test=True);self.assertEqual(receipt['target'],'HOST_ONLY')
   inputfile=p/'input';inputfile.write_bytes(b'Actual host-built client bytes.\n')
   result=subprocess.run([str(p/'build/loop-app'),str(inputfile)],capture_output=True,check=True)
   self.assertEqual(result.stdout,b'HOSTSHARE_DEVLOOP_BEGIN\nActual host-built client bytes.\nHOSTSHARE_DEVLOOP_END\n')
   with self.assertRaises(ValueError):dev.validate(p/'build/loop-app',p/'build/build.json',ROOT)
   with self.assertRaises(FileExistsError):dev.build(p/'build',host_test=True)
 def test_missing_sdk_refused_before_build(self):
  with self.localtemp() as tmp:
   with self.assertRaises(ValueError):dev.build(Path(tmp)/'build',sdk_env='/missing/sdk-env')
   self.assertFalse((Path(tmp)/'build').exists())
 def test_runner_boot_contract_no_manual_mount_or_second_probe(self):
  s=(ROOT/'tools/run-native-suite.py').read_text()
  self.assertLess(s.index("boot_text=until("),s.index("b'echo HS_SUITE_BOOT_READY"))
  self.assertIn('boot mount/read replaces standalone PCI probe',s)
  self.assertIn("if rc(text,'BOOT_SEAL_RC')!=0",s)
  self.assertIn("if readback(copied,60)!=o.dev_app.read_bytes()",s)
  self.assertIn("guest od unavailable/failed",s)
  self.assertNotIn('sha256sum',s)

 def test_actual_runner_readback_callback_host_bytes_and_failure(self):
  source=ast.parse((ROOT/'tools/run-native-suite.py').read_text())
  fn=next(x for x in ast.walk(source) if isinstance(x,ast.FunctionDef) and x.name=='readback')
  code=compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),'actual-readback-callback','exec')
  def command(cmd,marker,timeout,record):
   self.assertFalse(record)
   return subprocess.check_output(['/bin/sh','-c',cmd],stderr=subprocess.STDOUT,timeout=timeout).decode()
  def rc(text,key):
   m=re.search('^'+re.escape(key)+r'=(\d+)$',text,re.M);return int(m[1]) if m else None
  namespace={'os':os,'serial':bytearray(),'command':command,'rc':rc,'parse_readback':parse_readback,'binary_window':None}
  exec(code,namespace)
  with self.localtemp() as tmp:
   p=Path(tmp)/'bytes';p.write_bytes(bytes(range(256)))
   self.assertEqual(namespace['readback'](str(p),2),bytes(range(256)))
   self.assertIsNone(namespace['binary_window'])
   with self.assertRaises(RuntimeError):namespace['readback'](str(p)+'-missing',2)
