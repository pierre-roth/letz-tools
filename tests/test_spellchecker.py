from letztools.spellchecker import API, Spellchecker, assemble, tokenize
from letztools.common import SourceError


def data(correct=True, **extra):
    return {'correct': correct, 'n_rule_applicable': False, 'n_rule_reversible': False,
            'n_rule_applicable_for_previous_word': False, **extra}


def test_repeated_words_keep_all_original_occurrences_and_rank_order():
    class HTTP:
        def __init__(self): self.suggestions = 0
        def post_json(self, url, payload): return {'results': {w: data(False) for w in payload['words']}}
        def get_json(self, url):
            self.suggestions += 1
            return ['Buch', 'Bich']
    http = HTTP(); result = Spellchecker(http).check('Buhc a Buhc')
    assert [(f['start'], f['end']) for f in result['findings']] == [(0, 4), (5, 6), (7, 11)]
    assert result['findings'][0]['suggestions'] == ['Buch', 'Bich']
    assert http.suggestions == 2


def test_n_rule_uses_following_word_and_punctuation_blocks_it():
    metadata = {'den': data(n_rule_applicable=True, n_rule_variant='de'),
                'Buch': data(n_rule_applicable_for_previous_word=True)}
    assert assemble('den Buch', metadata, {})[1][0]['suggestions'] == ['de']
    assert not assemble('den, Buch', metadata, {})[1]
    assert not assemble('den\n\nBuch', metadata, {})[1]
    assert not assemble('den\nBuch', metadata, {})[1]


def test_n_restoration_and_spelling_precedence():
    metadata = {'de': data(n_rule_reversible=True, n_rule_variant='den'), 'Apel': data()}
    assert assemble('de Apel', metadata, {})[1][0]['suggestions'] == ['den']
    metadata['de']['correct'] = False
    assert assemble('de Apel', metadata, {'de': ['den']})[1][0]['type'] == 'spelling'


def test_metadata_failure_never_becomes_clean_text():
    class Offline:
        def post_json(self, *args): raise SourceError('Offline')
    result = Spellchecker(Offline()).check('E Buch.')
    assert result['status'] == 'unavailable'
    assert result['unavailable_words'] == ['E', 'Buch']


def test_missing_metadata_and_suggestions_have_explicit_partial_status():
    class HTTP:
        def post_json(self, *args): return {'results': {'Buhc': data(False)}}
        def get_json(self, *args): raise SourceError('No suggestions')
    result = Spellchecker(HTTP()).check('Buhc Text')
    assert result['status'] == 'partial' and result['findings'][0]['suggestions'] == []


def test_unicode_and_crlf_offsets_point_to_original_text():
    text = '🦊\r\nBuhc.'
    spans = [s for s in tokenize(text) if not s['separator']]
    assert spans[-1]['start'] == 3 and text[spans[-1]['start']:spans[-1]['end']] == 'Buhc'


def test_metadata_requests_use_published_batch_limit():
    class HTTP:
        def __init__(self): self.batches=[]
        def post_json(self, url, payload):
            self.batches.append(payload['words'])
            return {'results': {w:data() for w in payload['words']}}
    http=HTTP(); result=Spellchecker(http).check(' '.join('word'+str(i) for i in range(401)))
    assert result['status']=='ok' and list(map(len,http.batches)) == [200,200,1]


def test_incomplete_following_metadata_cannot_imply_n_restoration():
    metadata = {'de': data(n_rule_reversible=True, n_rule_variant='den'), 'Apel': {'correct': True}}
    words, findings = assemble('de Apel', metadata, {})
    assert not findings and words[0]['status'] == 'unavailable'
    assert words[1]['status'] == 'unavailable'
