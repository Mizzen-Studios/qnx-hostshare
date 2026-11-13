"""Host-only launcher/fixture checks; never native proof."""
import ast,hashlib,json,subprocess,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class NativeSuiteContract(unittest.TestCase):
 def test_exact_public_corpus(self):
  tree=ast.parse((ROOT/'tools/run-native-suite.py').read_text())
  assignment=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='contents' for t in n.targets))
  data=eval(compile(ast.Expression(assignment.value),'fixtures','eval'),{'bytes':bytes,'range':range})
  expected=json.loads((ROOT/'docs/acceptance/mount-20261113/corpus.json').read_text())
  self.assertEqual(len(data),7)
  for name,b in data.items():
   checksum=int(subprocess.run(['cksum'],input=b,capture_output=True,check=True).stdout.split()[0])
   self.assertEqual(expected[name],{'sha256':hashlib.sha256(b).hexdigest(),'size':len(b),'posix_cksum':checksum})
 def test_launcher_help_without_credentials_or_guest(self):
  result=subprocess.run(['python3',str(ROOT/'tools/run-native-suite.py'),'--help'],capture_output=True,text=True)
  self.assertEqual(result.returncode,0);self.assertIn('--image-kind',result.stdout);self.assertIn('--midread',result.stdout)
 def test_native_read_errno_is_not_translated(self):
  source=(ROOT/'native/mount_checksum.c').read_text()
  self.assertIn('ssize_t n=read(fd,b,sizeof b);int saved=errno;',source)
  self.assertIn('return n==-1&&saved==EIO?0:3;',source)
  self.assertNotIn('saved=EIO',source)
