# Verification

Development date: 17 November 2026. Offline suite: 33 passed (plus six subtests); one optional local-PDF test skipped in the routine run.

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

The installed Codex plugin's own packaged entrypoint was also exercised in this
session: live spelling and n-rule suggestions, LOD entry lookup, rule search and
numbered rule retrieval all returned successful structured responses.

Claude account upload and a real ChatGPT web/Claude conversation automatically
invoking the installed skill still need host-level confirmation;
file validation and private plugin creation alone do not prove that every host
allows outbound networking. No hosted backend is required or provisioned.

## Native Claude plugin (0.1.4)

- `claude plugin validate .` (Claude Code 2.1.325) passes for the plugin and the
  marketplace. `--profile directory` fails only on the missing licence.
- The PDF reader (pypdf 7.1.0, unmodified, BSD-3-Clause) is now tracked in
  `scripts/vendor/`, so a marketplace install contains everything the helpers need.
  Builds verify the vendored version; they no longer copy it from a developer
  environment.
- Installed through a marketplace whose plugin source is a git URL, in an isolated
  Claude Code configuration. This triggers the same copy into the plugin cache that
  a GitHub install uses. From that installed copy, with Python in isolated mode,
  site packages disabled and an empty guide cache, all six command forms returned
  `ok`: `check` (flags `den`→`de` and `Buhc`→`Buch`), `lookup`, `lookup --language fr`,
  `forms`, `rules` and `rule 6.1.1`. Tested on python.org Python 3.11 and Homebrew
  Python 3.14.
- A python.org macOS Python whose certificates were never installed previously
  failed TLS verification, which looked like an unreachable service. The client now
  falls back to the operating system's CA bundle only when Python has none, with
  verification still on. It reports certificate failures separately.
- macOS's built-in Python 3.9 runs `check`, `lookup` and `forms`. `rules`/`rule`
  return `unavailable` with a plain message, because pypdf needs 3.10+.
- A headless Claude Code session loaded the installed copy and listed
  `letz-tools:luxembourgish-writing`. The model turn could not run because the local
  CLI login had expired. Automatic activation in a real conversation still needs
  confirming in the Claude apps.

Not verifiable from the developer machine: adding the private GitHub marketplace in
Claude chat/Cowork, automatic skill use there, and whether their code sandbox may
reach `lod.lu` and `zls.gouvernement.lu` under each plan's network settings.
