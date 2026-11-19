"""HOST-only configuration, independent oracle and binding guards."""
import hashlib,json,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from handoff_preflight import config,export_directory,binding
from handoff_oracle import verify
class Handoff(unittest.TestCase):
 def test_strict_c(self):
  with tempfile.TemporaryDirectory() as tmp:
   binary=Path(tmp)/'config'
   subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-pedantic','-I'+str(ROOT/'core'),str(ROOT/'tests/test_handoff_config.c'),'-o',str(binary)],check=True)
   subprocess.run([str(binary)],check=True)
   for tag,path in [('f0test','/mnt/host'),('dev-inputs','/mnt/dev-inputs'),('a'*31,'/mnt/'+'b'*63)]:
    config(tag,path);self.assertEqual(subprocess.run([str(binary),'--tag',tag,'--mountpoint',path,'--mount']).returncode,0)
   for tag,path in [('', '/mnt/host'),('a'*32,'/mnt/host'),('a,b','/mnt/host'),('..','/mnt/host'),('dev','/mnt/a/../b'),('dev','/mnt/a//b'),('dev','/mnt/a/'),('dev','/etc/a'),('dev','/mnt/'+'a'*64),('dev','/mnt/a b')]:
    with self.assertRaises(ValueError):config(tag,path)
    self.assertEqual(subprocess.run([str(binary),'--tag',tag,'--mountpoint',path,'--mount']).returncode,2)
   for args in [[],['--unknown'],['--tag'],['--mountpoint','/mnt/a'],['--mount','--mount'],['--tag','a','--tag','b'],['--pci-line','--msix']]:
    if not args:continue
    self.assertEqual(subprocess.run([str(binary),*args]).returncode,2)
   subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-pedantic','-c',str(ROOT/'native/conformance.c'),'-o',str(Path(tmp)/'client.o')],check=True)
 def test_export(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp);(p/'input').write_bytes(b'x');self.assertEqual(export_directory(p),p)
   (p/'escape').symlink_to('/etc/passwd')
   with self.assertRaises(ValueError):export_directory(p)
   with self.assertRaises(ValueError):export_directory(p/'missing')
   with self.assertRaises(ValueError):export_directory(p/'..'/p.name)
   (p/'escape').unlink();(p/'name,unsafe').mkdir()
   with self.assertRaises(ValueError):export_directory(p/'name,unsafe')
 def test_binding(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp);(p/'core').mkdir();(p/'native').mkdir();(p/'core/a.h').write_text('a');elf=p/'elf';elf.write_bytes(b'new elf')
   h=lambda q:hashlib.sha256(q.read_bytes()).hexdigest()
   data={'files':{'core/a.h':h(p/'core/a.h')},'elf_sha256':h(elf)};manifest=p/'manifest';manifest.write_text(json.dumps(data));binding(p,elf,manifest)
   elf.write_bytes(b'old elf')
   with self.assertRaises(ValueError):binding(p,elf,manifest)
   elf.write_bytes(b'new elf');data['files']={};manifest.write_text(json.dumps(data))
   with self.assertRaises(ValueError):binding(p,elf,manifest)
 def test_independent_oracle_negative_controls(self):
  with tempfile.TemporaryDirectory() as tmp:
   corpus=Path(tmp);rows=[]
   for name,data in {'empty':b'','one':b'x','4KiB':bytes(range(256))*16,'1MiB':bytes(range(256))*4096}.items():(corpus/name).write_bytes(data)
   for c in range(2):
    for name in ('empty','one','4KiB','1MiB'):
     for o in (0,1,3999,4000,4095,4096,1048575,1048576,1048581):
      for k in (0,1,17,257):
       data=(corpus/name).read_bytes()[o:o+k];rows.append('HS_CASE %d %s %d %d %d %s-'%(c,name,o,k,len(data),data.hex()))
    for rewind in range(2):
     rows.extend('HS_DIR %d %d %s'%(c,rewind,p.name) for p in corpus.iterdir());rows.append('HS_DIR_END %d %d'%(c,rewind))
   rows.extend('HS_DENY %s -1 30'%n for n in ('open0','open1','open2','open3','create'));rows.append('HS_CONFORMANCE_COMPLETE')
   text='\n'.join(rows);self.assertEqual(verify(text,corpus)['byte_cases'],288)
   for bad in [text.replace(' 78-',' 79-',1),text.replace(rows[0],'',1),text+'\n'+rows[0],text.replace('HS_DENY create -1 30','HS_DENY create 4 0'),text.replace('HS_CONFORMANCE_COMPLETE','')]:
    with self.assertRaises(ValueError):verify(bad,corpus)

 def test_actual_host_client_rejects_writable_directory(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp);main=p/'main.c';main.write_text('int mount_conformance(const char *);int main(int argc,char **argv){return argc==2?mount_conformance(argv[1]):2;}')
   binary=p/'client';subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-pedantic',str(ROOT/'native/conformance.c'),str(main),'-o',str(binary)],check=True)
   corpus=p/'corpus';corpus.mkdir()
   for n,b in {'empty':b'','one':b'x','4KiB':bytes(range(256))*16,'1MiB':bytes(range(256))*4096}.items():(corpus/n).write_bytes(b)
   run=subprocess.run([str(binary),str(corpus)],capture_output=True,text=True)
   self.assertEqual(run.returncode,7)
   with self.assertRaises(ValueError):verify(run.stdout,corpus)
