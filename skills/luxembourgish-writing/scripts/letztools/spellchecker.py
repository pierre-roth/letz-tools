"""Plain-text spelling reports from spellchecker.lu's official backing API.

The published editor supplies word metadata, then applies contextual n-rule flags.
This adapter assembles occurrences and suggestions; it implements no dictionary.
"""
from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import quote

from .common import HttpClient, SourceError

API = 'https://lod.lu/api/lb/spellchecker'
FRONTEND = 'https://spellchecker.lu/assets/js/homepage.CDD12gc3.js'
SEPARATORS = frozenset(" \n\r\t\u00a0\u200b.,;:!?’/'\"@<>{}[]=*&$€#+-„“”«»()%§°²³£µ×÷…–—‘‚‹›•©®™№¶‰‱´″‴‵‶‷")
JS_WHITESPACE = '\t\n\v\f\r \u00a0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u2028\u2029\u202f\u205f\u3000\ufeff'


def tokenize(text: str) -> list[dict]:
    """Keep code-point offsets; p/br boundaries mirror plain clipboard text."""
    normalized, mapping = [], []
    index = 0
    while index < len(text):
        mapping.append(index)
        if text[index:index+2] == '\r\n':
            normalized.append('\n'); index += 2
        else:
            normalized.append(text[index]); index += 1
    mapping.append(len(text))
    source = ''.join(normalized)
    spans = []; index = block = 0
    while index < len(source):
        if source[index:index+2] == '\n\n':
            block += 1; index += 2
            continue
        if source[index] == '\n':
            index += 1
            continue
        start = index; separator = source[index] in SEPARATORS
        index += 1
        while index < len(source) and source[index] != '\n' and (source[index] in SEPARATORS) == separator:
            index += 1
        a, b = mapping[start], mapping[index]
        spans.append({'text': text[a:b], 'start': a, 'end': b,
                      'separator': separator, 'block': block})
    return spans


def assemble(text: str, metadata: dict, suggestions: dict) -> tuple[list, list]:
    spans = tokenize(text); words = []; findings = []
    for index, span in enumerate(spans):
        if span['separator']:
            continue
        following = ''
        if index+2 < len(spans):
            separator, next_word = spans[index+1:index+3]
            if (separator['separator'] and not next_word['separator']
                    and separator['block'] == span['block'] == next_word['block']
                    and not separator['text'].strip(JS_WHITESPACE)):
                following = next_word['text']
        data = metadata.get(span['text'])
        valid = (isinstance(data, dict) and type(data.get('correct')) is bool
                 and (not data['correct'] or all(type(data.get(key)) is bool for key in
                      ('n_rule_applicable', 'n_rule_reversible', 'n_rule_applicable_for_previous_word'))))
        status = 'unavailable' if not valid else 'correct'
        if valid and not data['correct']:
            status = 'spelling'
        elif valid and following and (data['n_rule_applicable'] or data['n_rule_reversible']):
            next_data = metadata.get(following)
            next_flag = next_data.get('n_rule_applicable_for_previous_word') if isinstance(next_data, dict) else None
            if type(next_flag) is not bool:
                status = 'unavailable'
            elif (data['n_rule_applicable'] and next_flag or data['n_rule_reversible'] and not next_flag):
                status = 'n_rule'
        row = {**span, 'following_word': following, 'status': status}
        words.append(row)
        if status in ('spelling', 'n_rule'):
            proposed = suggestions.get(span['text'], []) if status == 'spelling' else [data.get('n_rule_variant')]
            findings.append({'start': span['start'], 'end': span['end'], 'text': span['text'],
                             'type': status, 'suggestions': [x for x in proposed if isinstance(x, str) and x],
                             'following_word': following,
                             'context': text[max(0, span['start']-65):min(len(text), span['end']+65)]})
    return words, findings


class Spellchecker:
    def __init__(self, http=None):
        self.http = http or HttpClient()

    def check(self, text: str, *, max_suggestions: int = 8, include_tokens: bool = False) -> dict:
        if not isinstance(text, str):
            raise ValueError('The text must be a string.')
        if type(max_suggestions) is not int or max_suggestions < 1:
            raise ValueError('max_suggestions must be a positive integer.')
        distinct = list(dict.fromkeys(s['text'] for s in tokenize(text) if not s['separator']))
        metadata = {}; errors = []; suggestion_map = {}
        for offset in range(0, len(distinct), 200):
            batch = distinct[offset:offset+200]
            try:
                reply = self.http.post_json(API+'/check-words', {'words': batch})
                results = reply.get('results') if isinstance(reply, dict) else None
                if not isinstance(results, dict):
                    raise SourceError('The spelling service returned an unexpected metadata format.', source=API)
                metadata.update({word: value for word, value in results.items() if word in batch})
            except SourceError as error:
                errors.append(str(error))
        words, initial = assemble(text, metadata, {})
        for word in dict.fromkeys(f['text'] for f in initial if f['type'] == 'spelling'):
            try:
                reply = self.http.get_json(API+'/suggestions/'+quote(word, safe=''))
                if not isinstance(reply, list) or any(not isinstance(s, str) for s in reply):
                    raise SourceError('The spelling service returned an unexpected suggestions format.', source=API)
                suggestion_map[word] = reply[:max_suggestions]
            except SourceError as error:
                errors.append(str(error))
        words, findings = assemble(text, metadata, suggestion_map)
        unavailable = [w for w in words if w['status'] == 'unavailable']
        if unavailable:
            errors.append(f'Metadata unavailable for {len(unavailable)} word occurrences; those words have not been certified correct.')
        status = 'ok' if not errors else 'unavailable' if words and len(unavailable) == len(words) else 'partial'
        result = {'source': 'spellchecker.lu', 'source_url': 'https://spellchecker.lu/',
                  'checked_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
                  'status': status, 'text': text, 'word_occurrences': len(words),
                  'findings': findings, 'unavailable_words': list(dict.fromkeys(w['text'] for w in unavailable)),
                  'warnings': list(dict.fromkeys(errors)),
                  'scope': 'Spelling and contextual n-rule flags for plain text; grammar and meaning still require interpretation.',
                  'client_reference': FRONTEND, 'offsets': 'Unicode code points; end is exclusive'}
        if include_tokens:
            result['tokens'] = words
            result['metadata'] = metadata
        return result
