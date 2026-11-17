#!/usr/bin/env python3
"""Build self-contained ChatGPT plugin and Claude skill from one source tree."""
from __future__ import annotations

import importlib.metadata
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills' / 'luxembourgish-writing'


def allowed(path):
    return not any(part in {'__pycache__', '.DS_Store'} or part.endswith('.egg-info') for part in path.parts) and path.suffix not in {'.pyc', '.pyo'}


def copy_tree(source, destination):
    for path in source.rglob('*'):
        if path.is_file() and allowed(path.relative_to(source)):
            if path.is_symlink():
                raise ValueError(f'Unexpected symlink: {path}')
            target = destination / path.relative_to(source)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)


def archive(source, target):
    with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as out:
        for path in sorted(source.rglob('*')):
            if path.is_file():
                name = path.relative_to(source).as_posix()
                info = zipfile.ZipInfo(name, date_time=(2026, 11, 17, 0, 0, 0))
                info.external_attr = 0o644 << 16
                out.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    print(f'{target.relative_to(ROOT)} ({target.stat().st_size:,} bytes)')


def main():
    import pypdf
    # Keep the tested reader version explicit; upgrades are a maintainer action.
    if importlib.metadata.version('pypdf') != '7.1.0':
        raise SystemExit('Build with the tested pypdf==7.1.0 dependency.')
    stage = ROOT / 'build' / 'packages'
    if stage.exists():
        shutil.rmtree(stage)
    plugin = stage / 'chatgpt'
    skill = plugin / 'skills' / SKILL.name
    copy_tree(SKILL, skill)
    vendor = skill / 'scripts' / 'vendor'
    copy_tree(Path(pypdf.__file__).parent, vendor / 'pypdf')
    dist = importlib.metadata.distribution('pypdf')
    license_files = [f for f in dist.files if 'license' in str(f).lower() and f.name.lower() in {'license', 'license.txt', 'license.md'}]
    if not license_files:
        raise SystemExit('Missing pypdf license; do not distribute without it.')
    for index, path in enumerate(license_files):
        shutil.copyfile(dist.locate_file(path), vendor / ('PYPDF-LICENSE' + (f'-{index}' if index else '') + '.txt'))
    (vendor / 'README.txt').write_text('pypdf 7.1.0, https://pypi.org/project/pypdf/7.1.0/\nBundled for local extraction of the public orthography PDF.\nSee PYPDF-LICENSE.txt; no orthography book text is bundled.\n', encoding='utf-8')
    manifest = json.loads((ROOT / 'plugin.json').read_text())
    (plugin / 'plugin.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    copy_tree(ROOT / '.codex-plugin', plugin / '.codex-plugin')
    claude = stage / 'claude'
    copy_tree(skill, claude / SKILL.name)
    (ROOT / 'dist').mkdir(exist_ok=True)
    archive(plugin, ROOT / 'dist' / 'letz-tools-chatgpt.zip')
    archive(claude, ROOT / 'dist' / 'letz-tools-claude.zip')


if __name__ == '__main__':
    main()
