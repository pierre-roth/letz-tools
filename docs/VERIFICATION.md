# Verification

Development date: 17 November 2026. Offline suite: 27 passed (plus six subtests); one optional local-PDF test skipped in the routine run.

- Offline checks cover spelling/n-rule assembly, repeated occurrences, ranked
  suggestions, punctuation and paragraph context, Unicode/CRLF offsets, 200-token
  batching, failed/partial sources, LOD homographs, senses and actual form tables.
- Guide checks cover source failures, cached public reference data, section
  retrieval, parent sections, search, page citations and edition changes. The
  optional extraction check uses a separately downloaded actual publisher PDF;
  no book text is distributed as fixtures.
- Live LOD searches/entries were checked for `Buch` and `goen`, including noun
  plural and verb conjugation. Guide extraction produced 183 numbered sections;
  6.1.1 and 6.2.1 were checked against the source PDF.
- A whole synthetic paragraph was compared with spellchecker.lu in the in-app
  browser: both flags and their suggestions matched. This does not establish
  exhaustive equivalence for arbitrary rich-text editor documents.
- Release archives were extracted and their entrypoints executed with Python isolated mode and site packages disabled. A fresh-cache guide lookup also succeeded using only the bundled PDF reader. Archives include the dependency license.
- The private ChatGPT plugin was saved through Plugin Creator and its skill, helpers and bundled dependency read back from the registered release. Consumer checks exercised all five commands from the built Claude skill.

The helpers are tested locally. Claude account upload and a real ChatGPT/Claude
conversation invoking the installed skill still need host-level confirmation;
file validation and private plugin creation alone do not prove that every host
allows outbound networking. No hosted backend is required or provisioned.
