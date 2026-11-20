"""HOST-only integration/provenance guards. No SDK, guest or lease actions."""
import ast,hashlib,importlib.util,json,os,select,selectors,subprocess,time,unittest,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Integration(unittest.TestCase):
 def test_vendor_and_shared_tests_pinned(self):
  pin=json.loads((ROOT/'tools/recording_transport/PIN.json').read_text())
  for path,key in [('tools/recording_transport/__init__.py','sha256'),('tests/test_serial_transport.py','shared_tests_sha256')]:
   self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),pin[key])
  self.assertRegex(pin['canonical_commit'],r'^[a-f0-9]{40}$')
 def test_hash_then_byte_readback_then_execute(self):
  source=(ROOT/'tools/run-native-suite.py').read_text()
  self.assertLess(source.index("report['transfer']=transfer("),source.index("'chmod 700 '"))
  self.assertLess(source.index("assert observed==data"),source.index("save('probe'"))
  self.assertIn('budget=900',source);self.assertIn('timeout=20',source)
  self.assertIn('os.set_blocking(r.stdin.fileno(),False)',source)
  self.assertIn('time.monotonic()+timeout',source)
 def test_raw_append_logs_and_owned_cleanup(self):
  source=(ROOT/'tools/run-native-suite.py').read_text()
  self.assertLess(source.index("eventlog=open("),source.index('r=subprocess.Popen('))
  self.assertIn("'a',buffering=1",source)
  self.assertIn("'event':'runner_terminal'",source)
  self.assertIn('r.terminate()',source);self.assertIn('r.kill();r.wait()',source)
  self.assertIn('redact_payload_commands(serial.decode',source)
  self.assertIn('match_lines(bytes(serial[start:]))',source)
 def test_no_native_source_change_in_vendor_contract(self):
  pin=json.loads((ROOT/'tools/recording_transport/PIN.json').read_text())
  self.assertEqual(pin['native_status'],'HOST_ONLY_NOT_QNX_VERIFIED')

 def test_actual_runner_exchange_on_host_shell(self):
  spec=importlib.util.spec_from_file_location('transport_integration',ROOT/'tools/recording_transport/__init__.py')
  module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  tree=ast.parse((ROOT/'tools/run-native-suite.py').read_text())
  fn=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='exchange')
  code=compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),'actual-runner-exchange','exec')
  child=subprocess.Popen(['/bin/sh'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
  sel=selectors.DefaultSelector();sel.register(child.stdout,selectors.EVENT_READ);serial=bytearray();events=[]
  def drain(timeout=.05):
   if sel.select(timeout):
    data=os.read(child.stdout.fileno(),65536)
    if not data:raise RuntimeError('HOST shell exited')
    events.append({'rx':data});serial.extend(data)
  def until(marker,timeout,start):
   deadline=time.monotonic()+timeout
   while time.monotonic()<deadline:
    drain(min(.01,max(0,deadline-time.monotonic())))
    if marker in module.match_lines(bytes(serial[start:])):return bytes(serial[start:]).decode()
   raise TimeoutError('HOST actual caller deadline')
  scope={'r':child,'serial':serial,'os':os,'select':select,'time':time,'event':events.append,'base64':__import__('base64'),'drain':drain,'until':until}
  exec(code,scope);path=Path('/tmp/rt-'+uuid.uuid4().hex[:16])
  try:
   result=module.transfer(bytes(range(256)),str(path),scope['exchange'],events.append,toolbox='HOST_TEST',budget=10)
   self.assertTrue(result['verified_before_execution']);self.assertEqual(path.read_bytes(),bytes(range(256)))
   self.assertTrue(any(e.get('event')=='transfer_tx' for e in events))
  finally:
   child.terminate();child.wait(3);child.stdin.close();child.stdout.close();sel.close();path.unlink(missing_ok=True)
