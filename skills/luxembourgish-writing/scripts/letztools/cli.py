"""JSON interface shared by ChatGPT, Claude and local agent runtimes."""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

from .lod import LODClient
from .orthography import OrthographyGuide
from .spellchecker import Spellchecker


def compact_lookup(result):
    result = copy.deepcopy(result)
    for entry in result.get('entries', []):
        for key, limit in [('meanings', 4), ('translations', 4), ('examples', 6),
                           ('register', 8), ('related_entries', 6)]:
            items = entry.get(key, [])
            entry[key + '_total'] = len(items)
            entry[key] = items[:limit]
        entry.pop('tables', None)
        entry.pop('search_match', None)
        entry.pop('infoboxes', None)
    result['view'] = 'compact; use --full for every sense, example and table'
    return result


def parser():
    root = argparse.ArgumentParser(description='LëtzTools: official Luxembourgish language references; JSON output.')
    commands = root.add_subparsers(dest='command', required=True)
    check = commands.add_parser('check', help='Check a whole plain-text paragraph or document')
    source = check.add_mutually_exclusive_group(required=True)
    source.add_argument('--text', help='Plain text (prefer --file for longer drafts)')
    source.add_argument('--file', type=Path, help='UTF-8 text file; use - for stdin')
    check.add_argument('--tokens', action='store_true', help='Include every token and source metadata')
    lookup = commands.add_parser('lookup', help='LOD meanings, usage, register and variants')
    lookup.add_argument('query')
    lookup.add_argument('--language', choices=['lb', 'de', 'fr', 'en', 'pt'], default='lb')
    lookup.add_argument('--limit', type=int, default=3)
    lookup.add_argument('--full', action='store_true')
    forms = commands.add_parser('forms', help='LOD inflection and conjugation tables')
    forms.add_argument('query')
    rules = commands.add_parser('rules', help='Search the official orthography guide')
    rules.add_argument('query')
    rules.add_argument('--limit', type=int, default=4)
    rule = commands.add_parser('rule', help='Read a numbered official orthography section')
    rule.add_argument('section')
    return root


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == 'check':
            text = args.text if args.text is not None else (sys.stdin.read() if str(args.file) == '-' else args.file.read_text(encoding='utf-8'))
            result = Spellchecker().check(text, include_tokens=args.tokens)
        elif args.command == 'lookup':
            result = LODClient().lookup(args.query, limit=args.limit, language=args.language)
            if not args.full:
                result = compact_lookup(result)
        elif args.command == 'forms':
            result = LODClient().forms(args.query)
            for entry in result.get('entries', []):
                for key in ['meanings', 'translations', 'examples', 'register', 'related_entries', 'search_match', 'conjugation', 'declension', 'infoboxes', 'synonyms']:
                    entry.pop(key, None)
        elif args.command == 'rules':
            result = OrthographyGuide().search(args.query, args.limit)
        else:
            result = OrthographyGuide().rule(args.section)
    except (OSError, ValueError) as exc:
        result = {'status': 'invalid_request', 'error': str(exc)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result.get('status') in {'unavailable', 'partial', 'invalid_request'} else 0
