"""Offline checks that every host gets the same self-contained skill."""
import json
from pathlib import Path
import struct
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills' / 'luxembourgish-writing'
ENTRY = SKILL / 'scripts' / 'letztools.py'


def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def test_versions_and_names_agree():
    version = tomllib.loads((ROOT / 'pyproject.toml').read_text())['project']['version']
    claude = load('.claude-plugin/plugin.json')
    marketplace = load('.claude-plugin/marketplace.json')
    entry, = marketplace['plugins']
    assert entry['source'] == './'
    assert entry['name'] == claude['name'] == load('plugin.json')['name'] == load('.codex-plugin/plugin.json')['name']
    assert {claude['version'], entry['version'], load('plugin.json')['version'],
            load('.codex-plugin/plugin.json')['version']} == {version}
    assert f"__version__ = '{version}'" in (SKILL / 'scripts' / 'letztools' / '__init__.py').read_text()


def test_claude_icon_is_square_l_icon():
    icon = ROOT / load('.claude-plugin/plugin.json')['icon']
    assert icon.read_bytes() == (SKILL / 'assets' / 'letztools-icon-on-light.png').read_bytes()
    width, height = struct.unpack('>II', icon.read_bytes()[16:24])
    assert width == height == 512


def test_skill_frontmatter_matches_directory():
    head = (SKILL / 'SKILL.md').read_text(encoding='utf-8').split('---')[1]
    assert f'name: {SKILL.name}' in head


def test_no_symlinks_in_installed_files():
    for base in [SKILL, ROOT / '.claude-plugin', ROOT / 'assets']:
        assert not [p for p in base.rglob('*') if p.is_symlink()]


def test_entrypoint_runs_without_site_packages():
    """The installed plugin must not rely on a developer virtualenv."""
    probe = ('import runpy, sys; sys.argv = [sys.argv[0], "--help"]\n'
             'sys.path[:0] = [%r, %r]\n'
             'import pypdf; assert pypdf.__version__ == "7.1.0", pypdf.__version__\n'
             'assert pypdf.__file__.startswith(%r), pypdf.__file__\n'
             % (str(SKILL / 'scripts'), str(SKILL / 'scripts' / 'vendor'), str(SKILL / 'scripts' / 'vendor')))
    subprocess.run([sys.executable, '-I', '-S', '-c', probe], check=True)
    help_text = subprocess.run([sys.executable, '-I', '-S', str(ENTRY), '--help'],
                               check=True, capture_output=True, text=True).stdout
    for command in ['check', 'lookup', 'forms', 'rules', 'rule']:
        assert command in help_text


def test_tls_falls_back_to_os_bundle_only_when_python_has_no_cas(monkeypatch, tmp_path):
    from letztools import common

    class Context:
        def __init__(self): self.loaded = []
        def cert_store_stats(self): return {'x509_ca': 0}
        def load_verify_locations(self, cafile): self.loaded.append(cafile)

    bundle = tmp_path / 'cert.pem'
    bundle.write_text('placeholder')
    monkeypatch.setattr(common.ssl, 'create_default_context', Context)
    monkeypatch.setattr(common, 'SYSTEM_CA_BUNDLES', (str(tmp_path / 'missing.pem'), str(bundle)))
    paths = common.ssl.DefaultVerifyPaths
    monkeypatch.setattr(common.ssl, 'get_default_verify_paths',
                        lambda: paths(str(tmp_path / 'none.pem'), None, '', '', '', ''))
    assert common.tls_context().loaded == [str(bundle)]
    present = tmp_path / 'python-cas.pem'
    present.write_text('placeholder')
    monkeypatch.setattr(common.ssl, 'get_default_verify_paths',
                        lambda: paths(str(present), None, '', '', '', ''))
    assert common.tls_context().loaded == []
