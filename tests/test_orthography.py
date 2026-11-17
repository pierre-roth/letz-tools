"""Offline fixtures below are invented, not quotations from the official book."""
import json
import os
from pathlib import Path
import time

import pytest

from letztools.common import SourceError
from letztools.orthography import (
    OrthographyGuide, _extract_pdf, CACHE_SCHEMA, PDF_SHA256, PDF_URL,
)


def sample(section='6.1.1', text='Invented example: Alpha; exception: Beta.', heading='Synthetic heading'):
    return {'section': section, 'heading': heading, 'text': text,
            'pdf_page': 49, 'printed_page': 47, 'pdf_page_end': 50,
            'printed_page_end': 48, 'source_url': PDF_URL + '#page=49',
            'cross_references': ['2.3.3']}


def guide(tmp_path):
    result = OrthographyGuide(cache_dir=tmp_path)
    result._sections = [sample('6', '', 'Synthetic chapter'),
                        sample('6.1', '', 'Synthetic parent'), sample(),
                        sample('6.2.1', 'Invented text: Gamma is optional.', 'Synthetic optional form')]
    return result


def test_parent_preserves_children_examples_exceptions_and_crossrefs(tmp_path):
    result = guide(tmp_path).rule('6.1')
    assert result['status'] == 'ok'
    assert result['subsections'] == ['6.1.1']
    assert 'exception: Beta.' in result['text']
    assert 'Gamma' not in result['text']
    assert result['cross_references'] == ['2.3.3']
    assert result['printed_page_end'] == 48
    assert result['source_url'].endswith('#page=49')


def test_search_returns_excerpts_and_source_not_whole_index(tmp_path):
    result = guide(tmp_path).search('exception', limit=4)
    assert result['status'] == 'ok'
    assert result['hits'][0]['section'] == '6.1.1'
    assert 'exception: Beta.' in result['hits'][0]['excerpt']
    assert 'text' not in result['hits'][0]
    assert result['source']['sha256'] == PDF_SHA256


def test_accents_and_case_are_searchable(tmp_path):
    subject = guide(tmp_path)
    subject._sections = [sample(text='Invented Lëtzebuergesch example.')]
    assert subject.search('LETZEBUERGESCH')['status'] == 'ok'
    assert subject.search('unrelated')['status'] == 'no_matches'


def test_invalid_or_absent_sections_are_distinct(tmp_path):
    subject = guide(tmp_path)
    assert subject.rule('8e')['status'] == 'invalid_request'
    assert subject.rule('6.9')['status'] == 'not_found'
    assert subject.rule('§ 6.1.1.')['status'] == 'ok'
    assert subject.search('')['status'] == 'invalid_request'


def test_network_failure_cannot_be_a_clean_lookup(tmp_path):
    class Unreachable:
        def get_bytes(self, url):
            raise SourceError('Offline', source=url)
    result = OrthographyGuide(http=Unreachable(), cache_dir=tmp_path).search('example')
    assert result['status'] == 'unavailable'
    assert result['hits'] == []
    assert result['source_url'] == PDF_URL


def test_changed_pdf_rejected_before_any_parser_guess():
    with pytest.raises(SourceError, match='has changed'):
        _extract_pdf(b'%PDF different edition')


def test_public_cache_reused_and_stale_warning_explicit(tmp_path):
    class Unreachable:
        calls = 0
        def get_bytes(self, url):
            self.calls += 1
            raise SourceError('Offline', source=url)
    sections = [sample(str(i)) for i in range(183)]
    sections[0] = sample()
    payload = {'schema': CACHE_SCHEMA, 'sha256': PDF_SHA256,
               'retrieved_at': time.time(), 'sections': sections}
    path = tmp_path / 'index.json'
    path.write_text(json.dumps(payload))
    http = Unreachable()
    assert OrthographyGuide(http=http, cache_dir=tmp_path).rule('6.1.1')['status'] == 'ok'
    assert http.calls == 0
    payload['retrieved_at'] = 0
    path.write_text(json.dumps(payload))
    result = OrthographyGuide(http=http, cache_dir=tmp_path).rule('6.1.1')
    assert result['status'] == 'ok'
    assert 'could not be refreshed' in result['warnings'][0]
    assert http.calls == 1


@pytest.mark.skipif(not os.environ.get('LETZTOOLS_ORTHOGRAPHY_PDF'), reason='Optional publisher-PDF integration check')
def test_actual_publisher_pdf(tmp_path):
    sections = _extract_pdf(Path(os.environ['LETZTOOLS_ORTHOGRAPHY_PDF']).read_bytes())
    assert len(sections) == 183
    subject = OrthographyGuide(cache_dir=tmp_path)
    subject._sections = sections
    primary = subject.rule('6.1.1')
    optional = subject.rule('6.2.1')
    assert (primary['pdf_page'], primary['printed_page'], primary['pdf_page_end']) == (49, 47, 50)
    assert (optional['pdf_page'], optional['printed_page']) == (52, 50)
    assert 'fakultativ' in optional['text']
    assert 'hunn si' in optional['text']
    assert subject.rule('8')['heading'] == 'D’Grouss- a Klengschreiwung'
    assert subject.rule('9.5')['heading'].endswith('a Pronomen')
    assert subject.rule('10.5.2')['status'] == 'ok'
    assert subject.rule('7.2.4.4')['cross_references'] == ['2.2.5']
    for query in ['n-Reegel', 'Fakultativen n', 'Apostroph', 'Komma']:
        result = subject.search(query)
        assert result['status'] == 'ok'
        assert 3 <= len(result['hits']) <= 5
