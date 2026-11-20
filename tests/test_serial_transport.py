"""HOST PTY/shell proof, never native acceptance or payload execution."""
import base64,fcntl,hashlib,importlib.util,json,os,pty,re,select,subprocess,tempfile,threading,time,unittest,uuid
from pathlib import Path
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'tools/recording_transport/__init__.py').is_file())
spec=importlib.util.spec_from_file_location('shared_transport',ROOT/'tools/recording_transport/__init__.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class SerialTransport(unittest.TestCase):
 def trial(self,payload,fault=None,delay=0,budget=900,model=False):
  master,slave=pty.openpty();p=subprocess.Popen(['/bin/sh','-i'],stdin=slave,stdout=slave,stderr=slave,env={**os.environ,'PS1':'','PS2':''},start_new_session=True);os.close(slave)
  dest='/tmp/rt-'+uuid.uuid4().hex[:16];logs=[];tick=[0.0];count=[0];maxwire=[0]
  def exchange(wire,marker,timeout):
   count[0]+=1;maxwire[0]=max(maxwire[0],len(wire));self.assertLessEqual(len(wire),512)
   if fault=='truncate' and count[0]==2:wire=b'false\n'
   if fault=='missinghash' and b'sha256sum' in wire:wire=wire.replace(b'sha256sum',b'no_such_hash_applet')
   deadline=time.monotonic()+min(timeout,0.15 if fault in ('truncate','missinghash') else 3)
   # Actual partial writes through a real PTY. No retry of uncertain commands.
   m.write_all(lambda b:os.write(master,b[:7]),wire)
   if delay:time.sleep(delay)
   raw=b''
   while time.monotonic()<deadline:
    if select.select([master],[],[],.002)[0]:raw+=os.read(master,65536)
    if marker in m.match_lines(raw):
     if fault=='corrupt' and count[0]==2:Path(dest).write_bytes(b'CORRUPT')
     if fault=='echo':return wire
     if fault=='duplicate':return raw+marker+b'\n'
     if fault=='wrong':return raw.replace(marker,marker+b'0')
     if fault=='stale':return raw.replace(marker,b'RT_'+b'0'*32+b'_0_0')
     if fault=='wronghash':raw=re.sub(rb'(RH_[a-f0-9]{32} )[a-f0-9]{64}',lambda x:x[1]+b'0'*64,raw)
     if fault=='wrongsize':raw=re.sub(rb'(RN_[a-f0-9]{32} )\d+',rb'\g<1>999999',raw)
     if fault=='csi':raw=raw.replace(marker,b'\x1b[?7h'+marker)
     if model:tick[0]+=1.0
     return raw
   raise TimeoutError('HOST PTY ack timeout')
  try:
   kwargs={'toolbox':'HOST_TEST','budget':budget,'timeout':.4}
   if model:kwargs['clock']=lambda:tick[0]
   result=m.transfer(payload,dest,exchange,logs.append,**kwargs)
   self.assertEqual(Path(dest).read_bytes(),payload)
   self.assertEqual(result['sha256'],hashlib.sha256(payload).hexdigest());self.assertEqual(logs[-1]['status'],'VERIFIED')
   self.assertLessEqual(result['max_command_bytes'],512)
   return result,tick[0],maxwire[0]
  except BaseException:
   self.assertEqual(logs[-1]['status'],'FAILED');raise
  finally:
   p.kill();p.wait(3);os.close(master);Path(dest).unlink(missing_ok=True)
 def test_full51528_real_pty_delay_backpressure_budget(self):
  data=(bytes(range(256))*202)[:51528]
  result,modeled,wire=self.trial(data,delay=.002,model=True)
  self.assertEqual(result['acks'],808);self.assertEqual(modeled,808);self.assertLess(modeled,900)
  print('HOST_FULL_PAYLOAD',json.dumps({'bytes':51528,'acks':808,'max_command_bytes':wire,'modeled_seconds_at_1s_per_ack':modeled,'budget_seconds':900,'actual_ack_delay_seconds':.002}))
 def test_binary_controls_quotes(self):self.trial(bytes(range(256))+b"'\\\n\r$()\x00")
 def test_csi_real_ack(self):self.trial(b'bytes',fault='csi')
 def test_echo_rejected(self):
  with self.assertRaises(RuntimeError):self.trial(b'x',fault='echo')
 def test_duplicate_rejected(self):
  with self.assertRaises(RuntimeError):self.trial(b'x',fault='duplicate')
 def test_wrong_sequence_rejected(self):
  with self.assertRaises(RuntimeError):self.trial(b'x',fault='wrong')
 def test_stale_nonce_rejected(self):
  with self.assertRaises(RuntimeError):self.trial(b'x',fault='stale')
 def test_truncated_command_rejected(self):
  with self.assertRaises(TimeoutError):self.trial(b'x',fault='truncate')
 def test_corruption_rejected(self):
  with self.assertRaises(RuntimeError):self.trial(b'x',fault='corrupt')
 def test_wrong_size_rejected(self):
  with self.assertRaises(RuntimeError):self.trial(b'x',fault='wrongsize')
 def test_wrong_hash_rejected(self):
  with self.assertRaises(RuntimeError):self.trial(b'x',fault='wronghash')
 def test_missing_hash_rejected(self):
  with self.assertRaises(TimeoutError):self.trial(b'x',fault='missinghash')
 def test_global_budget_exhaustion(self):
  with self.assertRaises(TimeoutError):self.trial(b'x'*512,budget=2,model=True)
 def test_partial_write_and_closed_write(self):
  output=bytearray()
  def writer(b):output.extend(b[:3]);return min(3,len(b))
  m.write_all(writer,b'0123456789');self.assertEqual(output,b'0123456789')
  with self.assertRaises(RuntimeError):m.write_all(lambda b:0,b'x')
 def test_replayed_retained_csi_and_echo_negatives(self):
  for raw in (b'\x1b[?7hCOPY_6912\r\n',b'\x1b[?7hCOPY_7040\r\n'):
   self.assertTrue(any(x.startswith(b'COPY_') for x in m.match_lines(raw)))
  self.assertNotIn(b'COPY_6912',m.match_lines(b'# echo COPY_6912\nCOPY_69120\n'))
 def test_bounds(self):
  for kwargs in ({'destination':'/tmp/x;bad'},{'destination':'/tmp/'+'x'*25},{'chunk_bytes':65},{'budget':901},{'nonce':'bad'}):
   args={'destination':'/tmp/rt-test',**kwargs}
   with self.assertRaises(ValueError):m.transfer(b'x',exchange=None,log=None,**args)
 def test_public_redaction_preserves_private_raw(self):
  raw="printf '\\177\\105' >> /tmp/hs && printf 'ack'"
  public=m.redact_payload_commands(raw)
  self.assertNotIn("177",public);self.assertIn('OWN ELF COPY REDACTED',public)
  self.assertIn('177',raw)
 def test_caller_deadline_clipped(self):
  tick=[0];seen=[];logs=[]
  def exchange(wire,marker,timeout):
   seen.append(timeout);tick[0]+=2;return marker+b'\n'
  with self.assertRaises(TimeoutError):m.transfer(b'x','/tmp/rt-test',exchange,logs.append,budget=1,clock=lambda:tick[0])
  self.assertEqual(seen,[1]);self.assertEqual(logs[-1]['status'],'FAILED')
 def test_real_nonblocking_pipe_backpressure(self):
  readfd,writefd=os.pipe();fcntl.fcntl(writefd,fcntl.F_SETPIPE_SZ,4096);os.set_blocking(writefd,False)
  payload=bytes(range(256))*202;received=bytearray();blocked=[0];deadline=time.monotonic()+3
  def consume():
   time.sleep(.03)
   while len(received)<len(payload):
    received.extend(os.read(readfd,257));time.sleep(.0001)
  reader=threading.Thread(target=consume);reader.start()
  def writer(data):
   while time.monotonic()<deadline:
    try:return os.write(writefd,data)
    except BlockingIOError:blocked[0]+=1;select.select([],[writefd],[],.01)
   raise TimeoutError('HOST pipe deadline')
  try:
   m.write_all(writer,payload);reader.join(3)
   self.assertFalse(reader.is_alive());self.assertGreater(blocked[0],0);self.assertEqual(received,payload)
  finally:os.close(writefd);os.close(readfd)
if __name__=='__main__':unittest.main()
