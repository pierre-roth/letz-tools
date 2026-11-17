#!/usr/bin/env python3
"""Run directly; the downloadable skill includes its PDF dependency."""
from pathlib import Path
import sys

scripts = Path(__file__).resolve().parent
sys.path.insert(0, str(scripts))
sys.path.insert(0, str(scripts / 'vendor'))
from letztools.cli import main

if __name__ == '__main__':
    raise SystemExit(main())
