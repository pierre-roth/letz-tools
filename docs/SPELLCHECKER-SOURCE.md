# spellchecker.lu adapter

Inspected the public site's current JavaScript on 17 November 2026:

- https://spellchecker.lu/assets/js/app.BRpjswpl.js
- https://spellchecker.lu/assets/js/Page.C1nhxE9V.js
- https://spellchecker.lu/assets/js/homepage.CDD12gc3.js

The adapter uses the same public backing service:
`POST https://lod.lu/api/lb/spellchecker/check-words` with `{"words":[...]}`,
in batches of at most 200 distinct tokens. It requests ranked suggestions through
`GET https://lod.lu/api/lb/spellchecker/suggestions/{word}` only for spelling flags.
It neither submits corrections nor calls editor replacement logging endpoints.

For each occurrence, a false `correct` field produces a spelling flag. Otherwise,
the browser flags an n-rule case when the current form is applicable and the
following word requests dropping n, or the current form is reversible and the
following word does not request dropping n. It uses `n_rule_variant` as the
suggestion. Context follows the browser's separator-only whitespace test;
punctuation and paragraph boundaries prevent adjacent-word evaluation. The
plain-text adapter handles single line breaks as the editor's br behavior,
and double line breaks as paragraph boundaries. It does not recreate rich-text
editor state, ignored-word lists, replacement history or all possible HTML paste
structures. It preserves original Python code-point offsets, including CRLF input.

A live synthetic paragraph was entered into the in-app browser and checked with
the helper. Both identified `den` before `Ball` (suggestion `de`) and `Buhc`
(suggestion `Buch`), with no other flags in that paragraph. This is a focused
integration check, not a claim of exhaustive editor equivalence.

LOD dictionary access uses the documented public API:
https://lod.lu/api/doc and
https://data.public.lu/en/datasets/letzebuerger-online-dictionnaire-lod-public-api/.
Lookup retains distinct entry identities, sense-scoped information and the
actual entry's tables rather than inventing variants or generated inflections.
