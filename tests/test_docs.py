"""Host-only documentation regression; no SDK, QEMU or native execution."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PAGES = ('README.md', 'docs/JUDGES.md', 'docs/RUN_NATIVE.md',
         'docs/CURRENT_CONTRACT.md', 'docs/DEMO_DRAFT.md')


class DocumentationContract(unittest.TestCase):
    def test_current_local_links_exist(self):
        for name in PAGES:
            page = ROOT / name
            for target in re.findall(r'\]\(([^)]+)\)', page.read_text()):
                if '://' not in target and not target.startswith('#'):
                    with self.subTest(page=name, target=target):
                        self.assertTrue((page.parent / target.split('#')[0]).exists())

    def test_quickstart_commands_omit_obsolete_midread_gate(self):
        # Native recipes moved out of the HOST-only README; keep both recipe gates.
        for name in ('docs/HISTORY.md', 'docs/RUN_NATIVE.md'):
            source = (ROOT / name).read_text()
            commands = [line for line in source.splitlines()
                        if line.startswith('sh tools/run-native-suite.sh ')]
            self.assertEqual(len(commands), 2)
            for command in commands:
                self.assertNotIn('--midread', command)
                result = subprocess.run([sys.executable,
                    str(ROOT / 'tools/run-native-suite.py'),
                    *command.split()[2:], '--help'], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('Historical diagnostic only', source)
            self.assertIn('ESRCH3', source)
            self.assertIn('export HS_BUILD_MANIFEST=/absolute/path/to/fresh-build-source-hashes.json', source)
            self.assertNotIn('export HS_BUILD_MANIFEST="$PWD/docs/acceptance/', source)

    def test_living_contract_media_not_written_only(self):
        source = (ROOT / 'docs/CURRENT_CONTRACT.md').read_text()
        self.assertNotIn('recorded=false', source)
        self.assertNotIn('EDU owns the current lease', source)
        self.assertIn('https://youtu.be/O0SA7W6gFyE', source)
        self.assertIn('private draft is not a public release', source)
        self.assertIn('before RPC/DMA', source)

    def test_fresh_manifest_recipe_and_existing_runner_binding(self):
        source = (ROOT / 'docs/RUN_NATIVE.md').read_text()
        recipe = source.split("<<'PYMANIFEST'\n", 1)[1].split('\nPYMANIFEST', 1)[0]
        runner = (ROOT / 'tools/run-native-suite.py').read_text()
        # Execute only the existing hash checks, never launcher/guest code.
        checks = runner.split("elf=Path(os.environ['HS_ELF'])", 1)[1]
        checks = "elf=Path(os.environ['HS_ELF'])" + checks.split('assert not subprocess.check_output', 1)[0]
        (ROOT / '.local').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / '.local') as temporary:
            base = Path(temporary)
            elf, output = base / 'synthetic-not-an-elf', base / 'manifest.json'
            elf.write_bytes(b'host-only fixture A')
            def generate():
                return subprocess.run([sys.executable, '-c', recipe, str(elf), str(output)],
                                      cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(generate().returncode, 0)
            original = output.read_bytes()
            manifest = json.loads(original)
            expected = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                        for folder in ('core', 'native') for p in (ROOT / folder).glob('*.[ch]')}
            self.assertEqual(manifest['files'], expected)
            self.assertEqual(manifest['elf_sha256'], hashlib.sha256(elf.read_bytes()).hexdigest())
            self.assertNotEqual(generate().returncode, 0)  # never overwrite
            self.assertEqual(output.read_bytes(), original)
            environment = dict(os.environ, HS_ELF=str(elf), HS_BUILD_MANIFEST=str(output),
                               HS_IFS=str(base / "unused-ifs"), HS_DISK=str(base / "unused-disk"))
            def verify(root=ROOT):
                exec(checks, {'Path': Path, 'os': type('Env', (), {'environ': environment}),
                             'json': json, 'h': lambda p: hashlib.sha256(p.read_bytes()).hexdigest(),
                             'root': root})
            verify()
            elf.write_bytes(b'host-only fixture B')
            with self.assertRaises(AssertionError):
                verify()  # mismatched ELF rejected by unchanged runner
            output.unlink()
            self.assertEqual(generate().returncode, 0)
            self.assertNotEqual(json.loads(output.read_text())['elf_sha256'], manifest['elf_sha256'])
            # Alter one source binding, not any actual project source.
            altered = json.loads(output.read_text())
            altered['files'][next(iter(expected))] = '0' * 64
            output.write_text(json.dumps(altered))
            with self.assertRaises(AssertionError):
                verify()  # mismatched source rejected by unchanged runner
            output.unlink()
            elf.unlink()
            self.assertNotEqual(generate().returncode, 0)
            self.assertFalse(output.exists())
