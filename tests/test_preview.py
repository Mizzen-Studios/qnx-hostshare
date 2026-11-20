import os,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Preview(unittest.TestCase):
    def test_preview_without_external_inputs(self):
        env={k:v for k,v in os.environ.items() if not k.startswith(('HS_','QNX_'))}
        p=subprocess.run([sys.executable,str(ROOT/'tools/preview-handoff.py')],env=env,capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr)
        for marker in ['PREVIEW ONLY','NOT VALIDATED','No guest started','readonly=on','$HS_EXPORT']:
            self.assertIn(marker,p.stdout)
        source=(ROOT/'tools/preview-handoff.py').read_text()
        self.assertNotIn('subprocess',source);self.assertNotIn('.read_',source)
    def test_invalid_preview_config_still_rejected(self):
        for args in [['--tag','../bad'],['--mountpoint','/tmp/unapproved']]:
            p=subprocess.run([sys.executable,str(ROOT/'tools/preview-handoff.py'),*args],capture_output=True,text=True)
            self.assertEqual(p.returncode,2);self.assertIn('BLOCKED:',p.stderr)
