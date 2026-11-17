#!/usr/bin/env python3
"""Refresh the tracked copy of pypdf inside the skill (maintainer action).

The skill runs directly from an installed Claude plugin, a ChatGPT plugin or a
skill ZIP. None of these hosts installs Python packages, so the tested PDF
reader is committed under scripts/vendor/. Run this only when deliberately
upgrading, from an environment with the pinned version installed:

    python -m pip install pypdf==7.1.0 && python tools/vendor_pypdf.py
"""
from __future__ import annotations

import importlib.metadata
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / 'skills' / 'luxembourgish-writing' / 'scripts' / 'vendor'
PYPDF_VERSION = '7.1.0'
README = (f'pypdf {PYPDF_VERSION}, https://pypi.org/project/pypdf/{PYPDF_VERSION}/\n'
          'Bundled unmodified for local extraction of the public orthography PDF,\n'
          'because Claude, ChatGPT and skill hosts do not install Python packages.\n'
          'See PYPDF-LICENSE.txt (BSD-3-Clause). No orthography book text is bundled.\n'
          'Refresh with tools/vendor_pypdf.py.\n')


def main():
    import pypdf
    if importlib.metadata.version('pypdf') != PYPDF_VERSION:
        raise SystemExit(f'Install the tested pypdf=={PYPDF_VERSION} first.')
    if VENDOR.exists():
        shutil.rmtree(VENDOR)
    source = Path(pypdf.__file__).parent
    for path in sorted(source.rglob('*.py')) + sorted(source.rglob('py.typed')):
        target = VENDOR / 'pypdf' / path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    dist = importlib.metadata.distribution('pypdf')
    licenses = [f for f in dist.files if f.name.lower() in {'license', 'license.txt', 'license.md'}]
    if len(licenses) != 1:
        raise SystemExit('Expected exactly one pypdf license file; do not distribute without it.')
    shutil.copyfile(dist.locate_file(licenses[0]), VENDOR / 'PYPDF-LICENSE.txt')
    (VENDOR / 'README.txt').write_text(README, encoding='utf-8')
    print(f'Vendored pypdf {PYPDF_VERSION} into {VENDOR.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
