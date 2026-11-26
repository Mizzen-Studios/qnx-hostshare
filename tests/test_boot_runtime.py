"""HOST execution/negatives only; never QNX acceptance."""
import os,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import boot_runtime as b,boot_handoff
class BootRuntime(unittest.TestCase):
 def setUp(self):
  (ROOT/'.local').mkdir(exist_ok=True)
 def test_isolated_actual_client_with_unrelated_driver_logs(self):
  with tempfile.TemporaryDirectory(dir=ROOT/'.local') as tmp:
   p=Path(tmp);app=p/'app';inputfile=p/'input';output=p/'output';nonce='1'*32
   subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','examples/developer-loop.c','-o',str(app)],cwd=ROOT,check=True)
   inputfile.write_bytes(b'host proof\n'.replace(b'\\n',b'\n'))
   result=subprocess.run(['/bin/sh','-c','echo HOSTSHARE_IRQ_INTERLEAVED; '+b.client_command(str(app),str(inputfile),str(output),nonce)],capture_output=True,text=True,check=True)
   self.assertTrue(b.verify_client(result.stdout,nonce,output.read_bytes(),inputfile.read_bytes()))
   for bad in (output.read_bytes()+b'junk',b'',b'HOSTSHARE IRQ_PULSE\n'+output.read_bytes(),output.read_bytes()[:-1]):
    with self.assertRaises(ValueError):b.verify_client(result.stdout,nonce,bad,inputfile.read_bytes())
   for bad in ('',result.stdout.replace('=0','=1'),result.stdout+result.stdout):
    with self.assertRaises(ValueError):b.verify_client(bad,nonce,output.read_bytes(),inputfile.read_bytes())
 def test_pid_guard_real_shell_negatives_and_live_process(self):
  with tempfile.TemporaryDirectory(dir=ROOT/'.local') as tmp:
   pid=Path(tmp)/'pid';cmd=b.pid_command().replace('/dev/shmem/hs-boot.pid',str(pid))
   for value in (None,'','0','1','-1','123;echo injected','99999999'):
    if value is None:pid.unlink(missing_ok=True)
    else:pid.write_text(value)
    r=subprocess.run(['/bin/sh','-c',cmd],capture_output=True,text=True)
    self.assertEqual(b.status(r.stdout,'PID_GUARD_RC'),1)
   child=subprocess.Popen(['sleep','20'])
   try:
    pid.write_text(str(child.pid));r=subprocess.run(['/bin/sh','-c',cmd],capture_output=True,text=True)
    self.assertEqual(b.status(r.stdout,'PID_GUARD_RC'),0)
   finally:child.terminate();child.wait()
 def test_stop_actual_signal_reap_and_export_path_check(self):
  with tempfile.TemporaryDirectory(dir=ROOT/'.local') as tmp:
   mount=Path(tmp);(mount/'hello.txt').write_text('fixture')
   # Sibling process and independent reaper model the boot hook (not serial-shell child).
   child=subprocess.Popen(['/bin/sh','-c',"trap 'echo HOSTSHARE MOUNT TERM_DETACHED; rm " + str(mount/'hello.txt')+"; exit 0' TERM; echo ready; while :; do sleep .1; done"],stdout=subprocess.PIPE,text=True)
   self.assertEqual(child.stdout.readline().strip(),'ready')
   import threading
   reaper=threading.Thread(target=child.wait);reaper.start()
   try:
    result=subprocess.run(['/bin/sh','-c','HS_PID='+str(child.pid)+'; '+b.stop_command(str(mount))],capture_output=True,text=True,timeout=5)
    reaper.join(2);text=child.stdout.read()+result.stdout
    self.assertTrue(b.verify_stop(text));self.assertFalse((mount/'hello.txt').exists())
    for bad in (text.replace('STOP_SIGNAL_RC=0','STOP_SIGNAL_RC=1'),text.replace('STILL_ALIVE_RC=1','STILL_ALIVE_RC=0'),text.replace('STOP_PATH_ABSENT_RC=0','STOP_PATH_ABSENT_RC=1'),text.replace('HOSTSHARE MOUNT TERM_DETACHED','missing'),text+text):
     try:passed=b.verify_stop(bad)
     except ValueError:passed=False
     self.assertFalse(passed)
   finally:
    if child.poll() is None:child.kill();child.wait()
    reaper.join();child.stdout.close()
 def test_hook_no_external_printf_even_empty_path(self):
  self.assertNotIn(b'printf',boot_handoff.hook())
  with tempfile.TemporaryDirectory(dir=ROOT/'.local') as tmp:
   p=Path(tmp);driver=p/'driver';pid=p/'pid'
   driver.write_text('#!/bin/sh\necho HOST_FAKE\n'.replace('\\n','\n'));driver.chmod(0o700)
   script=boot_handoff.hook().decode().replace('/boot/hsd',str(driver)).replace('/dev/shmem/hs-boot.pid',str(pid))
   r=subprocess.run(['/bin/sh','-c',script],env={'PATH':'/nonexistent'},capture_output=True,text=True)
   self.assertEqual(r.returncode,0);self.assertTrue(pid.read_text().strip().isdigit());self.assertIn('HOSTSHARE_BOOT_LAUNCHED',r.stdout)
