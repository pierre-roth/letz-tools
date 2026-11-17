"""Small client for the official, public Lëtzebuerger Online Dictionnaire.

Routes: https://lod.lu/api/doc (OpenAPI); query parameters and table fields
are also used by LOD's own public frontend. No API key or dataset download.
Typed translation parts, sense-level attributes and related-entry references
are retained: a synonym or a related entry is not automatically a variant.
"""
from __future__ import annotations

import re
from urllib.parse import quote, urlencode

API = "https://lod.lu/api/lb"
DOCUMENTATION = "https://lod.lu/api/doc"
LANGUAGES = {"lb", "de", "fr", "en", "pt"}


class LODResponseError(ValueError):
    """The server replied, but not with the documented frontend data shape."""


def _source(url):
    return {"name": "Lëtzebuerger Online Dictionnaire (LOD)", "url": url,
            "documentation": DOCUMENTATION}


def _text(parts):
    """Render LOD word parts, including its explicit punctuation join flag."""
    rendered = ""
    for part in parts or []:
        if not isinstance(part, dict):
            continue
        content = part.get("content")
        if not isinstance(content, str):
            content = _text(part.get("parts", []))
        if not content or part.get("type") == "attribute":
            continue
        if rendered and not part.get("joinWithPreviousWord"):
            rendered += " "
        rendered += content
    return rendered


def _observations(value, keys, path=""):
    """Keep values and their scope without interpreting undocumented codes."""
    found = []
    if isinstance(value, dict):
        for key, child in value.items():
            location = f"{path}.{key}" if path else key
            if key in keys and child:
                found.append({"path": location, "value": child})
            found.extend(_observations(child, keys, location))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_observations(child, keys, f"{path}[{index}]"))
    return found


def _labeled_variants(entry, source):
    """Normalize only LOD's explicit variant/variants seeAlso labels.

    Keep the original box, location and example flag: a variant note attached
    to an example must not silently become an entry-wide equivalence.
    """
    variants = []
    for observation in _observations(entry, {"seeAlso"}):
        boxes = observation["value"]
        if not isinstance(boxes, list):
            continue
        for index, box in enumerate(boxes):
            if not isinstance(box, dict) or box.get("intro") not in {"variant", "variants"}:
                continue
            targets = []

            def links(node):
                if isinstance(node, dict):
                    if node.get("tag") == "internalLink" and isinstance(node.get("idRef"), str):
                        targets.append({"id": node["idRef"], "lemma": node.get("content"),
                                        "evidence": node})
                    for child in node.values():
                        links(child)
                elif isinstance(node, list):
                    for child in node:
                        links(child)

            links(box.get("content", []))
            variants.append({"path": f"{observation['path']}[{index}]", "value": box,
                             "relation": box["intro"], "targets": targets,
                             "concerns_example": box.get("concernsExample"),
                             "source_entry_id": entry["lod_id"], "source": source})
    return variants


class LODClient:
    def __init__(self, http=None):
        if http is None:
            from .common import HTTPClient
            http = HTTPClient()
        self.http = http
        self._entries = {}

    def _entry(self, lod_id):
        if lod_id not in self._entries:
            url = f"{API}/entry/{quote(lod_id, safe='')}"
            response = self.http.get_json(url)
            if not isinstance(response, dict) or not isinstance(response.get("entry"), dict):
                raise LODResponseError("LOD entry response has no entry object")
            entry = response["entry"]
            if not isinstance(entry.get("lemma"), str) or not entry.get("lod_id"):
                raise LODResponseError("LOD entry response lacks its lemma or identity")
            self._entries[lod_id] = entry
        return self._entries[lod_id]

    @staticmethod
    def _normalize(entry, match=None):
        lod_id = entry["lod_id"]
        source = _source(f"{API}/entry/{quote(lod_id, safe='')}")
        meanings, translations, examples, grammar = [], [], [], []
        structures = entry.get("microStructures", [])
        if not isinstance(structures, list):
            raise LODResponseError("LOD microStructures is not a list")
        for mi, micro in enumerate(structures):
            if not isinstance(micro, dict):
                raise LODResponseError("LOD microstructure is not an object")
            grammar.append({"microstructure_index": mi,
                            **{k: v for k, v in micro.items() if k != "grammaticalUnits"}})
            for gi, unit in enumerate(micro.get("grammaticalUnits", [])):
                context = {"microstructure_index": mi, "grammatical_unit_index": gi,
                           "grammar": {k: v for k, v in unit.items() if k != "meanings"}}
                for meaning in unit.get("meanings", []):
                    # Retain the original structured sense; register and variants can
                    # be attached to a sense, an example, or a translation part.
                    meanings.append({**meaning, "context": context})
                    identity = meaning.get("meaningID")
                    translations.append({"meaning_id": identity,
                                         "languages": meaning.get("targetLanguages", {})})
                    for example in meaning.get("examples", []):
                        examples.append({"meaning_id": identity,
                                         "text": _text(example.get("parts", []))})
        inflections = [{"microstructure_index": i, "data": micro["inflection"]}
                       for i, micro in enumerate(structures) if micro.get("inflection")]
        # Explicit API variant fields are kept separate from cross references.
        variants = _observations(entry, {"acceptedVariants", "variants", "alternativeForms"})
        variants.extend(_labeled_variants(entry, source))
        return {
            "id": lod_id, "lemma": entry["lemma"],
            "pos": entry.get("partOfSpeechLabel", entry.get("partOfSpeech")),
            "meanings": meanings, "translations": translations, "examples": examples,
            "register": _observations(entry, {"attributes", "style", "styles", "register"}),
            "accepted_variants": variants,
            "related_entries": _observations(entry, {"internalLink", "seeAlso"}),
            "synonyms": entry.get("allSynonyms", []),
            "n_rule_forms": [entry["nRuleForm"]] if entry.get("nRuleForm") else [],
            "grammar": grammar, "inflections": inflections,
            "tables": entry.get("tables", {}), "infoboxes": entry.get("infoboxes", []),
            "links": {"entry": f"https://lod.lu/artikel/{quote(lod_id, safe='')}",
                      "api": source["url"]},
            "source": source, "search_match": match or {},
        }

    def lookup(self, query, limit=5, language="lb"):
        """Search Luxembourgish or DE/FR/EN/PT translations, then fetch senses.

        `not_found` only describes this dictionary search. It does not prove
        a word is incorrect. Any failed or malformed request is `unavailable`.
        """
        return self._lookup(query, limit, language)

    def _lookup(self, query, limit, language, *, exact_lemma=False):
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Enter a word or expression to look up")
        if language not in LANGUAGES:
            raise ValueError("LOD search language must be lb, de, fr, en or pt")
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 20:
            raise ValueError("LOD result limit must be between 1 and 20")
        query = query.strip()
        url = f"{API}/search?{urlencode({'lang': language, 'query': query})}"
        result = {"status": "unavailable", "query": query, "language": language,
                  "entries": [], "source": _source(url)}
        try:
            data = self.http.get_json(url)
            if not isinstance(data, dict) or not isinstance(data.get("results"), list):
                raise LODResponseError("LOD search response has no results list")
            matches = data["results"]
            result["description"] = data.get("description", "")
            result["total_matches"] = len(matches)
            if exact_lemma:
                exact = [match for match in matches if isinstance(match, dict)
                         and isinstance(match.get("word_lb"), str)
                         and match["word_lb"].casefold() == query.casefold()]
                if exact:
                    matches = exact
                    # Keep every distinct exact homograph, even when broad
                    # search results place one beyond the normal result limit.
                    limit = max(limit, len(exact))
                    result["match_selection"] = "exact_lemma"
                else:
                    result["match_selection"] = "related_search_results"
            seen = set()
            for match in matches:
                if not isinstance(match, dict) or not isinstance(match.get("article_id", match.get("id")), str):
                    raise LODResponseError("LOD search result lacks an entry identity")
                # Article identity, not displayed spelling: homographs and real
                # variant entries must never be collapsed just by their lemma.
                lod_id = match.get("article_id") or match["id"]
                if lod_id in seen:
                    continue
                seen.add(lod_id)
                result["entries"].append(self._normalize(self._entry(lod_id), match))
                if len(result["entries"]) >= limit:
                    break
            result["status"] = "ok" if result["entries"] else "not_found"
            if not result["entries"]:
                result["note"] = "No LOD match; this is not proof of a spelling error."
        except Exception as exc:
            result["status"] = "unavailable"
            result["error"] = {"type": type(exc).__name__, "message": str(exc)}
            result["partial"] = bool(result["entries"])
        return result

    def forms(self, word_or_id):
        """Return actual entry tables and noun inflections, without generating forms.

        An uppercase LOD ID ending in a number fetches that entry directly.
        A word prefers exact lemmas from search, keeping every exact homograph.
        Related search matches are returned only when no exact lemma is found.
        Table person codes p1..p6 follow LOD: ech, du, hien/si/hatt, mir, dir, si.
        """
        if not isinstance(word_or_id, str) or not word_or_id.strip():
            raise ValueError("Enter a word or LOD entry ID")
        value = word_or_id.strip()
        if re.fullmatch(r"[A-Z][A-Z0-9_\-]*[0-9]", value):
            result = {"status": "unavailable", "query": value, "entries": [],
                      "source": _source(f"{API}/entry/{quote(value, safe='')}")}
            try:
                result["entries"] = [self._normalize(self._entry(value))]
                result["status"] = "ok"
            except Exception as exc:
                result["error"] = {"type": type(exc).__name__, "message": str(exc)}
        else:
            result = self._lookup(value, 5, "lb", exact_lemma=True)
        for entry in result["entries"]:
            entry["conjugation"] = entry["tables"].get("verbConjugation")
            entry["declension"] = entry["tables"].get("adjDeclension")
            entry["has_forms"] = bool(entry["tables"] or entry["inflections"])
        result["person_labels"] = {"p1": "ech", "p2": "du", "p3": "hien/si/hatt",
                                   "p4": "mir", "p5": "dir", "p6": "si"}
        return result
