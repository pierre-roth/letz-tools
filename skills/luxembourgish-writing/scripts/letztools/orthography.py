"""Search the publisher's orthography PDF, downloaded once to a public-source cache.

No third-party rule text is distributed with the skill. Extraction preserves the
PDF's wording and line breaks; citations distinguish printed and physical pages.
"""
from __future__ import annotations

import hashlib
import io
import json
import math
import re
import tempfile
import time
import unicodedata
from pathlib import Path

from .common import HttpClient, SourceError

LANDING_URL = 'https://zls.gouvernement.lu/lb/orthographe.html'
PUBLICATION_URL = 'https://zls.gouvernement.lu/lb/actualites/publications/letzebuerger-orthografie.html'
PDF_URL = 'https://zls.gouvernement.lu/dam-assets/pdfen/web-letzortho-oplo6-v01.pdf'
LEGAL_URL = 'https://zls.gouvernement.lu/fr/support/aspects-legaux.html'
PDF_SHA256 = 'be3f14e8bdffa971b34873b51b7e7184fffe9f0e01c7e81aac4e448e5404a550'
SOURCE_VERSION = '6. Oplo; PDF imprint: Lëtzebuerg 2024; publication page: 2026'
VERIFIED_ON = '2026-11-17'
CACHE_SCHEMA = 2
CACHE_MAX_AGE = 7 * 24 * 3600
HEADING = re.compile(r'^(?P<id>(?:10|[1-9])(?:\.\s*\d+){1,4}|(?:10|[1-9])\.)(?:\s+)(?P<title>\S.*)$')
EXTRACTION_WARNING = ('PDF text extraction preserves wording and line breaks, but typography, '
                      'tables and emphasis may require checking the linked PDF page.')


def _fold(text):
    text = unicodedata.normalize('NFKD', text.casefold().replace('’', "'"))
    return ''.join(c for c in text if not unicodedata.combining(c))


def _tokens(text):
    # Join layout hyphenation for searching only; returned source text is unchanged.
    words = re.findall(r'[\w]+', _fold(re.sub(r'(\w)-\s*\n(\w)', r'\1\2', text)))
    return ['fakultativ' if word in {'fakultativen', 'fakultative', 'optional'} else word for word in words]


def _space(text):
    return re.sub(r'\s+', ' ', text).strip()


def _extract_pdf(data):
    try:
        from pypdf import PdfReader
    except ImportError:
        raise SourceError('The packaged PDF reader is missing. Reinstall the complete LëtzTools skill archive.', source=PDF_URL) from None
    if hashlib.sha256(data).hexdigest() != PDF_SHA256:
        raise SourceError('The publisher PDF has changed. This edition needs verification before rule citations can be returned. Open the official guide.', source=LANDING_URL)
    try:
        reader = PdfReader(io.BytesIO(data))
        if len(reader.pages) != 120:
            raise ValueError('unexpected page count')
        sections = []
        current = None
        # Verified sixth-edition profile: physical pages 12–96, printed 10–94.
        # Font membership identifies wrapped headings, rather than guessing from prose.
        for physical in range(12, 97):
            page = reader.pages[physical - 1]
            heading_lines = []
            last_y = None
            def visitor(text, cm, tm, font, size):
                nonlocal last_y
                if not text.strip():
                    return
                if any(face in str((font or {}).get('/BaseFont', '')) for face in ('GothamNarrow-Bold', 'TradeGothicLTPro-BdCn20')):
                    y = round(tm[5], 1)
                    if y == last_y and heading_lines:
                        heading_lines[-1] += text
                    else:
                        heading_lines.append(text)
                    last_y = y
                else:
                    last_y = None
            raw = page.extract_text(visitor_text=visitor) or ''
            bold = {_space(line) for line in heading_lines}
            lines = raw.replace('\xad', '').splitlines()
            # Running chapter number and page header occupy the first two lines.
            if len(lines) < 2 or not re.match(r'^\s*\d+', lines[1]):
                raise ValueError('unrecognized running header')
            lines = lines[2:]
            index = 0
            while index < len(lines):
                line = re.sub(r'^\s*V\s+', '› ', lines[index])
                match = HEADING.match(line.strip())
                if match and _space(line) in bold:
                    section_id = re.sub(r'\s+', '', match['id']).rstrip('.')
                    title = match['title'].strip()
                    while (index + 1 < len(lines) and _space(lines[index + 1]) in bold
                           and not HEADING.match(lines[index + 1].strip())):
                        index += 1
                        title += ' ' + lines[index].strip()
                    current = {'section': section_id, 'heading': title, 'text': '',
                               'pdf_page': physical, 'printed_page': physical - 2,
                               'pdf_page_end': physical, 'printed_page_end': physical - 2,
                               'source_url': f'{PDF_URL}#page={physical}'}
                    sections.append(current)
                elif current is not None:
                    current['text'] += line.rstrip() + '\n'
                    if line.strip():
                        current['pdf_page_end'] = physical
                        current['printed_page_end'] = physical - 2
                index += 1
        for section in sections:
            section['text'] = section['text'].strip()
            reference_groups = re.findall(r'\bcf\.\s*([\d.,;\s]+)', section['text'])
            section['cross_references'] = sorted({ref for group in reference_groups for ref in re.findall(r'\d+(?:\.\d+)+', group)})
        ids = [s['section'] for s in sections]
        if len(ids) < 170 or len(set(ids)) != len(ids) or not all(i in ids for i in ['1.1', '6.1.1', '6.2.1', '7.2', '10.5.2']):
            raise ValueError('section validation failed')
        if ids != sorted(ids, key=lambda value: tuple(map(int, value.split('.')))):
            raise ValueError('section order failed')
        return sections
    except SourceError:
        raise
    except Exception as error:
        raise SourceError('The official PDF could not be indexed reliably. Open the official guide; no rule has been inferred.', source=PDF_URL) from error


class OrthographyGuide:
    def __init__(self, http=None, cache_dir=None):
        self.http = http if http is not None else HttpClient()
        self.cache_dir = Path(cache_dir) if cache_dir is not None else Path(tempfile.gettempdir()) / 'letztools-orthography-v2'
        self._sections = None
        self._warnings = []
        self._retrieved_at = None

    def _source(self):
        return {'title': 'D’Lëtzebuerger Orthografie', 'publisher': 'SCRIPT / ZLS',
                'authors': 'CPLL / ZLS', 'version': SOURCE_VERSION, 'sha256': PDF_SHA256,
                'landing_url': LANDING_URL, 'publication_url': PUBLICATION_URL,
                'pdf_url': PDF_URL, 'verified_on': VERIFIED_ON,
                'retrieved_at': self._retrieved_at}

    def _read_cache(self):
        try:
            cached = json.loads((self.cache_dir / 'index.json').read_text(encoding='utf-8'))
            if (cached['schema'] == CACHE_SCHEMA and cached['sha256'] == PDF_SHA256
                and isinstance(cached['retrieved_at'], (int, float))
                and isinstance(cached['sections'], list) and len(cached['sections']) == 183
                and all(isinstance(s, dict) and all(k in s for k in ('section', 'heading', 'text', 'pdf_page', 'printed_page', 'pdf_page_end', 'printed_page_end', 'source_url', 'cross_references')) for s in cached['sections'])):
                return cached
        except (OSError, ValueError, KeyError, TypeError):
            pass
        return None

    def _load(self):
        if self._sections is not None:
            return
        cached = self._read_cache()
        if cached and time.time() - cached['retrieved_at'] < CACHE_MAX_AGE:
            self._sections = cached['sections']
            self._retrieved_at = cached['retrieved_at']
            return
        try:
            data = self.http.get_bytes(PDF_URL)
            sections = _extract_pdf(data)
        except (SourceError, OSError) as error:
            # A source update must not silently turn into a successful stale answer.
            if cached and 'has changed' not in str(error):
                self._sections = cached['sections']
                self._retrieved_at = cached['retrieved_at']
                self._warnings.append('The official source could not be refreshed. Using the previously downloaded verified edition.')
                return
            raise
        self._sections = sections
        self._retrieved_at = time.time()
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            payload = {'schema': CACHE_SCHEMA, 'sha256': PDF_SHA256,
                       'retrieved_at': self._retrieved_at, 'sections': sections}
            # No writing queries or office text; this contains public reference text only.
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=self.cache_dir,
                                             prefix='index-', suffix='.tmp', delete=False) as handle:
                json.dump(payload, handle, ensure_ascii=False)
                temporary = Path(handle.name)
            temporary.replace(self.cache_dir / 'index.json')
        except OSError:
            self._warnings.append('The public reference cache could not be saved; the next request may download the guide again.')

    def _unavailable(self, error):
        return {'status': 'unavailable', 'source': self._source(), 'hits': [],
                'warnings': [str(error)], 'source_url': getattr(error, 'source', None) or PDF_URL}

    def search(self, query, limit=4):
        query = str(query).strip()
        if not query or len(query) > 1000:
            return {'status': 'invalid_request', 'hits': [], 'warnings': ['Use a short orthography question or keywords.']}
        try:
            try:
                limit = max(1, min(int(limit), 5))
            except (TypeError, ValueError):
                return {'status': 'invalid_request', 'hits': [], 'warnings': ['The result limit must be a number.']}
            self._load()
        except (SourceError, OSError) as error:
            return self._unavailable(error)
        stopwords = {'the','a','an','and','of','in','de','den','der','dei','d','e','en','eng','vun','fir','mat','ass','ginn','gett'}
        search_query = re.sub(r'\beifeler\s+(?:regel|rule)\b', 'n-Reegel', _fold(query))
        search_query = re.sub(r'\bn[ -]+(?:rule|regel)\b', 'n-Reegel', search_query)
        terms = set(_tokens(search_query)) - stopwords
        if not terms:
            terms = set(_tokens(query))
        sections = self._sections or []
        headings = {s['section']: s['heading'] for s in sections}
        contexts = {}
        for s in sections:
            parts = s['section'].split('.')
            contexts[s['section']] = ' / '.join(headings.get('.'.join(parts[:i]), '') for i in range(1, len(parts) + 1))
        documents = [set(_tokens(contexts[s['section']] + '\n' + s['text'])) for s in sections]
        frequency = {term: sum(term in doc for doc in documents) for term in terms}
        ranked = []
        for section, words in zip(sections, documents):
            if not section['text'].strip():
                continue
            matches = terms & words
            if not matches:
                continue
            title_terms = set(_tokens(contexts[section['section']]))
            score = sum(math.log(1 + len(sections) / (1 + frequency[t])) * (3 if t in title_terms else 1) for t in matches)
            score *= len(matches) / max(1, len(terms))
            phrase = ' '.join(_tokens(search_query))
            if phrase and phrase in ' '.join(_tokens(contexts[section['section']])):
                score += 10
            ranked.append((score, section))
        ranked.sort(key=lambda pair: -pair[0])
        hits = []
        for score, section in ranked[:limit]:
            hit = dict(section)
            text = _space(section['text'])
            folded = _fold(text)
            positions = [folded.find(term) for term in terms if folded.find(term) >= 0]
            start = max(0, min(positions, default=0) - 160)
            hit['excerpt'] = ('…' if start else '') + text[start:start + 900] + ('…' if len(text) > start + 900 else '')
            hit.pop('text')
            hit['score'] = round(score, 3)
            hits.append(hit)
        return {'status': 'ok' if hits else 'no_matches', 'source': self._source(),
                'query': query, 'hits': hits, 'warnings': self._warnings + [EXTRACTION_WARNING]}

    def rule(self, section):
        section = str(section).strip().removeprefix('§').strip().rstrip('.')
        if not re.fullmatch(r'(?:10|[1-9])(?:\.\d+){0,4}', section):
            return {'status': 'invalid_request', 'warnings': ['Use a printed guide section, for example 6.1.1 or 6.2.1.']}
        try:
            self._load()
        except (SourceError, OSError) as error:
            return self._unavailable(error)
        selected = [s for s in self._sections or [] if s['section'] == section or s['section'].startswith(section + '.')]
        if not selected or selected[0]['section'] != section:
            return {'status': 'not_found', 'section': section, 'source': self._source(), 'warnings': ['This section is not present in the verified edition.']}
        result = dict(selected[0])
        result['text'] = '\n\n'.join((s['section'] + ' ' + s['heading'] + '\n' + s['text']).rstrip() for s in selected)
        result['pdf_page_end'] = max(s['pdf_page_end'] for s in selected)
        result['printed_page_end'] = max(s['printed_page_end'] for s in selected)
        result['subsections'] = [s['section'] for s in selected[1:]]
        result['cross_references'] = sorted({ref for s in selected for ref in s['cross_references']})
        return {'status': 'ok', **result, 'source': self._source(), 'warnings': self._warnings + [EXTRACTION_WARNING]}

    get_rule = rule
