#!/usr/bin/env python3
"""Build ChatGPT plugin, Claude plugin and Claude skill archives from one source tree."""
from __future__ import annotations

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


def check_vendor():
    vendor = SKILL / 'scripts' / 'vendor'
    version = (vendor / 'pypdf' / '_version.py').read_text(encoding='utf-8')
    if "'7.1.0'" not in version and '"7.1.0"' not in version:
        raise SystemExit('Vendored pypdf is not the tested 7.1.0; run tools/vendor_pypdf.py.')
    if not (vendor / 'PYPDF-LICENSE.txt').is_file():
        raise SystemExit('Missing pypdf license; do not distribute without it.')


def main():
    # The skill, including its vendored PDF reader, is tracked in git and used
    # unchanged by every package: the Claude marketplace installs it straight
    # from the repository, so builds must not add files the repository lacks.
    check_vendor()
    stage = ROOT / 'build' / 'packages'
    if stage.exists():
        shutil.rmtree(stage)

    plugin = stage / 'chatgpt'
    copy_tree(SKILL, plugin / 'skills' / SKILL.name)
    manifest = json.loads((ROOT / 'plugin.json').read_text())
    (plugin / 'plugin.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    copy_tree(ROOT / '.codex-plugin', plugin / '.codex-plugin')
    copy_tree(ROOT / 'assets', plugin / 'assets')

    # Claude plugin for Customize > Plugins > upload (same layout as the marketplace install).
    claude_plugin = stage / 'claude-plugin'
    copy_tree(SKILL, claude_plugin / 'skills' / SKILL.name)
    shutil.copytree(ROOT / '.claude-plugin', claude_plugin / '.claude-plugin', ignore=shutil.ignore_patterns('marketplace.json', '.DS_Store'))
    copy_tree(ROOT / 'assets', claude_plugin / 'assets')
    shutil.copyfile(ROOT / 'README.md', claude_plugin / 'README.md')

    # Single skill for Customize > Skills upload.
    claude = stage / 'claude'
    copy_tree(SKILL, claude / SKILL.name)

    (ROOT / 'dist').mkdir(exist_ok=True)
    archive(plugin, ROOT / 'dist' / 'letz-tools-chatgpt.zip')
    archive(claude_plugin, ROOT / 'dist' / 'letz-tools-claude-plugin.zip')
    archive(claude, ROOT / 'dist' / 'letz-tools-claude.zip')


if __name__ == '__main__':
    main()
