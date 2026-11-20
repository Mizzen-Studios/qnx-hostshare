"""HOST-only judge documentation regression; no network or native execution."""
import re, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class JudgeDocs(unittest.TestCase):
    def test_portable_readme_and_local_links(self):
        text=(ROOT/'README.md').read_text()
        self.assertIn('HOST ONLY',text)
        self.assertIn('PUBLIC',text)
        self.assertNotIn('/home/ubuntu',text)
        for rel in ['README.md','docs/HISTORY.md','docs/PATHS.md']:
            source=ROOT/rel
            for target in re.findall(r'[]][(]([^)]*)[)]',source.read_text()):
                if re.match(r'[a-z]+:|#|/',target):continue
                self.assertTrue((source.parent/target.split('#')[0]).exists(),(rel,target))
