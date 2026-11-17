"""Synthetic protocol fixtures; these are not live LOD captures."""
import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/luxembourgish-writing/scripts"))
from letztools.lod import API, LODClient


class FixtureHTTP:
    def __init__(self, responses):
        self.responses = responses
        self.urls = []

    def get_json(self, url):
        self.urls.append(url)
        value = self.responses[url]
        if isinstance(value, Exception):
            raise value
        return copy.deepcopy(value)


def entry(identity="GOEN1", lemma="goen", **extra):
    return {"entry": {"lod_id": identity, "lemma": lemma, "partOfSpeechLabel": "VRB",
                      "microStructures": [], **extra}}


def search_url(query="goen", language="lb"):
    from urllib.parse import urlencode
    return f"{API}/search?{urlencode({'lang': language, 'query': query})}"


class LODTests(unittest.TestCase):
    def test_real_table_shape_and_n_rule_form_are_preserved(self):
        tables = {"verbConjugation": {"pastParticiple": "gaangen / gaang",
                                    "indicative": {"present": {"p1": "ginn", "p2": "gees"}}}}
        http = FixtureHTTP({f"{API}/entry/GOEN1": entry(tables=tables, nRuleForm="goe")})
        client = LODClient(http)
        result = client.forms("GOEN1")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["entries"][0]["conjugation"], tables["verbConjugation"])
        self.assertEqual(result["entries"][0]["n_rule_forms"], ["goe"])
        self.assertEqual(result["person_labels"]["p2"], "du")
        client.forms("GOEN1")
        self.assertEqual(len(http.urls), 1, "immutable entry cache avoids repeated requests")
        json.dumps(result, ensure_ascii=False)

    def test_homographs_and_related_variant_identities_stay_distinct(self):
        matches = [{"id": "BUCH1", "article_id": "BUCH1", "word_lb": "Buch"},
                   {"id": "BUCH2", "article_id": "BUCH2", "word_lb": "Buch"}]
        http = FixtureHTTP({search_url("Buch"): {"results": matches},
                            f"{API}/entry/BUCH1": entry("BUCH1", "Buch", acceptedVariants=[{"lod_id": "VARIANT1", "lemma": "Testvariant"}],
                              infoboxes={"seeAlso": [{"relation": "synonym", "idRef": "OTHER1"}]}),
                            f"{API}/entry/BUCH2": entry("BUCH2", "Buch")})
        result = LODClient(http).lookup("Buch")
        self.assertEqual(result["status"], "ok")
        self.assertEqual([e["id"] for e in result["entries"]], ["BUCH1", "BUCH2"])
        first = result["entries"][0]
        self.assertEqual(first["accepted_variants"][0]["value"][0]["lod_id"], "VARIANT1")
        self.assertEqual(first["related_entries"][0]["value"][0]["idRef"], "OTHER1")
        self.assertNotIn("OTHER1", str(first["accepted_variants"]))

    def test_sense_context_register_translation_clarifier_and_punctuation(self):
        meaning = {"meaningID": "BUCH1UNI1", "attributes": ["STYLE_FIXTURE"],
                   "targetLanguages": {"fr": {"parts": [
                       {"type": "translation", "content": "livre"},
                       {"type": "semanticClarifier", "content": "publication"}]}},
                   "examples": [{"parts": [{"type": "text", "parts": [
                       {"type": "word", "content": "d'"},
                       {"type": "inflectedHeadword", "content": "Bicher", "joinWithPreviousWord": True},
                       {"type": "word", "content": "!", "joinWithPreviousWord": True}]}]}]}
        micro = {"inflection": {"forms": [{"content": "Bicher"}]}, "grammaticalUnits": [
                 {"grammaticalInformation": ["fixture grammar"], "meanings": [meaning]}]}
        http = FixtureHTTP({f"{API}/entry/BUCH1": entry("BUCH1", "Buch", microStructures=[micro])})
        normalized = LODClient(http).forms("BUCH1")["entries"][0]
        self.assertEqual(normalized["meanings"][0]["targetLanguages"], meaning["targetLanguages"])
        self.assertEqual(normalized["meanings"][0]["context"]["grammar"]["grammaticalInformation"], ["fixture grammar"])
        self.assertEqual(normalized["examples"][0]["text"], "d'Bicher!")
        self.assertEqual(normalized["inflections"][0]["data"], micro["inflection"])
        self.assertIn("meanings[0].attributes", normalized["register"][0]["path"])

    def test_adjective_declension_uses_entry_table_and_never_generates_forms(self):
        table = {"basicForms": {"positive": "fixture"}, "declension": {"positive": {"nominative": "fixture form"}}}
        http = FixtureHTTP({f"{API}/entry/ADJ1": entry("ADJ1", "fixture", tables={"adjDeclension": table})})
        result = LODClient(http).forms("ADJ1")
        self.assertEqual(result["entries"][0]["declension"], table)
        self.assertIsNone(result["entries"][0]["conjugation"])

    def test_foreign_search_uses_official_lang_parameter(self):
        http = FixtureHTTP({search_url("livre", "fr"): {"results": []}})
        result = LODClient(http).lookup("livre", language="fr")
        self.assertEqual(result["status"], "not_found")
        self.assertIn("not proof", result["note"])
        self.assertEqual(http.urls, [search_url("livre", "fr")])

    def test_transport_or_schema_error_is_not_not_found(self):
        for response in [OSError("offline"), {"error": "unavailable"}, {"results": None}, {"results": [{}]}]:
            with self.subTest(response=response):
                result = LODClient(FixtureHTTP({search_url(): response})).lookup("goen")
                self.assertEqual(result["status"], "unavailable")
                self.assertIn("error", result)

    def test_partial_entry_failure_is_explicit(self):
        http = FixtureHTTP({search_url(): {"results": [{"id": "GOEN1"}, {"id": "OTHER1"}]},
                            f"{API}/entry/GOEN1": entry(),
                            f"{API}/entry/OTHER1": OSError("offline")})
        result = LODClient(http).lookup("goen")
        self.assertEqual(result["status"], "unavailable")
        self.assertTrue(result["partial"])
        self.assertEqual(result["entries"][0]["id"], "GOEN1")

    def test_word_forms_follow_search_and_respect_limit(self):
        http = FixtureHTTP({search_url(): {"results": [{"id": "GOEN1"}, {"id": "OTHER1"}]},
                            f"{API}/entry/GOEN1": entry()})
        result = LODClient(http).lookup("goen", limit=1)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["total_matches"], 2)
        self.assertEqual(len(result["entries"]), 1)
        self.assertEqual(len(http.urls), 2)

    def test_explicit_seealso_variants_retain_targets_and_example_scope(self):
        def box(intro, identity, example=False):
            return {"intro": intro, "concernsExample": example, "content": [
                {"tag": "infoboxList", "items": [{"tag": "infoboxListItem", "items": [
                    {"tag": "internalLink", "content": "fixture variant", "idRef": identity}]}]}]}
        for label in ["variant", "variants"]:
            with self.subTest(label=label):
                variant = box(label, "SITZUNG1", True)
                unrelated = box("synonym", "OTHER1")
                http = FixtureHTTP({f"{API}/entry/SETZUNG1": entry("SETZUNG1", "Sëtzung",
                                   infoboxes={"seeAlso": [variant, unrelated]})})
                normalized = LODClient(http).forms("SETZUNG1")["entries"][0]
                variants = normalized["accepted_variants"]
                self.assertEqual(len(variants), 1)
                self.assertEqual(variants[0]["targets"][0]["id"], "SITZUNG1")
                self.assertEqual(variants[0]["targets"][0]["lemma"], "fixture variant")
                self.assertEqual(variants[0]["value"], variant)
                self.assertEqual(variants[0]["path"], "infoboxes.seeAlso[0]")
                self.assertEqual(variants[0]["source_entry_id"], "SETZUNG1")
                self.assertTrue(variants[0]["concerns_example"])
                self.assertNotIn("OTHER1", str(variants))
                self.assertIn("OTHER1", str(normalized["related_entries"]))

    def test_forms_select_exact_lemmas_before_fetching_and_keep_all_homographs(self):
        matches = [{"id": "BROAD1", "word_lb": "fixture broad"}]
        matches += [{"id": f"EXACT{i}", "word_lb": "Buch"} for i in range(1, 7)]
        responses = {search_url("Buch"): {"results": matches}}
        responses.update({f"{API}/entry/EXACT{i}": entry(f"EXACT{i}", "Buch") for i in range(1, 7)})
        http = FixtureHTTP(responses)
        result = LODClient(http).forms("Buch")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["match_selection"], "exact_lemma")
        self.assertEqual(len(result["entries"]), 6)
        self.assertEqual([e["id"] for e in result["entries"]], [f"EXACT{i}" for i in range(1, 7)])
        self.assertNotIn(f"{API}/entry/BROAD1", http.urls)

    def test_forms_falls_back_to_related_search_matches_if_no_exact_lemma(self):
        http = FixtureHTTP({search_url("goe"): {"results": [{"id": "GOEN1", "word_lb": "goen"}]},
                            f"{API}/entry/GOEN1": entry()})
        result = LODClient(http).forms("goe")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["match_selection"], "related_search_results")
        self.assertEqual(result["entries"][0]["id"], "GOEN1")

    def test_validation_does_not_contact_server(self):
        http = FixtureHTTP({})
        client = LODClient(http)
        for kwargs in [{"query": ""}, {"query": "x", "language": "all"},
                       {"query": "x", "limit": 0}, {"query": "x", "limit": True}]:
            with self.assertRaises(ValueError):
                client.lookup(**kwargs)
        self.assertFalse(http.urls)


if __name__ == "__main__":
    unittest.main()
