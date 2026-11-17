<picture>
  <source media="(prefers-color-scheme: dark)" srcset="skills/luxembourgish-writing/assets/letztools-lockup-on-dark.svg">
  <img src="skills/luxembourgish-writing/assets/letztools-lockup-on-light.svg" width="380" alt="LëtzTools">
</picture>

# LëtzTools

Write, translate and improve Luxembourgish in ChatGPT or Claude, with help from
spellchecker.lu, the official LOD dictionary and the official orthography guide.
Ask normally; receive a finished text ready to copy.

> “Verbesser dësen Text, ouni de Sënn ze änneren.”
>
> “Schreif mir eng professionell E-Mail op Lëtzebuergesch.”
>
> “Ass dës Form richteg? Erklär mir firwat.”

## Install once

**ChatGPT:** open [the private LëtzTools plugin](https://chatgpt.com/plugins/plugins_6afc7e87fdb88191add1d3649a542486) and
add it to your account/workspace. Enable it where you write. The skill is configured
for automatic selection when Luxembourgish writing help is relevant. Availability
and installation controls depend on your ChatGPT account and surface.

**Claude:** download `letz-tools-claude.zip`, open **Customize → Skills**, choose
**+ → Create skill → Upload skill**, upload the ZIP and enable the skill. Code
execution / file creation must be enabled. Allow access to the official sources
if your Claude environment requests it. Then ask for help in an ordinary chat.

You do not need to set up a server, Python, an API key or a separate LëtzTools
account. The downloadable skill contains its Python helper and PDF reader; the
agent runs them in its own execution environment. That environment needs Python
3.10+ and internet access to `lod.lu` and `zls.gouvernement.lu`. A host without
network-enabled execution can browse the sources if it has browsing, but cannot
promise the same automatic API workflow. Installing the skill alone cannot override
host network restrictions or guarantee invocation on every turn.

For automatic use, leave the skill enabled. You can also say “Use LëtzTools”
explicitly. It returns the corrected text first, with short explanations when
useful, while preserving meaning, names and tone.

Installation guidance: [ChatGPT skills](https://help.openai.com/en/articles/20001066-skills-in-chatgpt),
[Claude skills](https://support.claude.com/en/articles/12512180-use-skills-in-claude).

## What it does

- Checks whole passages through spellchecker.lu's live backing API, assembling
  spelling and contextual n-rule findings with suggestions and original offsets.
- Looks up LOD meanings, usage, register, distinct homographs and actual inflection
  tables. Can search Luxembourgish, German, French, English and Portuguese.
- Searches the official orthography book and retrieves numbered rules with page
  links, examples, exceptions and cross-references.
- Gives the agent a short workflow to interpret these sources, preserve valid
  alternatives and recheck edits. It adds no independent language model.

The spelling service is a reference, not a complete grammar checker. The host
model still judges grammar, wording and meaning. Failed requests are reported as
unavailable, never as evidence of correctness. This project is independent of
LëtzCheck and is not an official ZLS product.

## Sources and privacy

Word batches and dictionary queries go directly to the official LOD/ZLS services.
There is no LëtzTools server or text logging. The official guide is downloaded
on demand and cached locally; the cache contains public reference text only.
The chat provider still handles the conversation under its own settings.
Respect workplace restrictions on external processing.

LOD and spelling results are live. The guide currently supports the sixth printing
linked by ZLS on 17 November 2026; a changed PDF is reported rather than silently
misquoted. Updates to third-party API schemas or a new book edition may need a
small package update. See [orthography source details](docs/ORTHOGRAPHY-SOURCE.md)
and [API assembly details](docs/SPELLCHECKER-SOURCE.md).

## Developers and other agents

One portable [Agent Skill](skills/luxembourgish-writing/SKILL.md) powers both
packages. Claude Code and other Agent Skills-compatible runtimes can use the
`skills/luxembourgish-writing` directory directly; source checkouts need `pypdf`
for guide extraction, while the built archives already include it. No MCP service
is required. The helper emits JSON for any agent that can execute Python.

```sh
uv venv .venv
uv pip install --python .venv/bin/python -e '.[dev]'
.venv/bin/python -m pytest -q
.venv/bin/python tools/build_packages.py
.venv/bin/python skills/luxembourgish-writing/scripts/letztools.py check --text 'Ech liesen e Buhc.'
```

Build artifacts are `dist/letz-tools-chatgpt.zip` and
`dist/letz-tools-claude.zip`. Builds vendor the tested pypdf 7.1.0 with its BSD
license. Neither archive contains the orthography book, source captures, test
fixtures, credentials or development environments. [Verification](docs/VERIFICATION.md)
distinguishes tested helpers from host installation testing.

## Branding

Uses the supplied LëtzInitiative family artwork, unchanged, with separate light
and dark icons and lockups. The shared icon is distinguished by the visible
LëtzTools name. UI accent colours follow the supplied design tokens; logo red and
blue remain fixed. Wordmarks are vector lettering and require no installed font.

Source artwork and guidance are under
[`skills/luxembourgish-writing/assets`](skills/luxembourgish-writing/assets).
Only the LëtzTools assets and common guidance were copied from the supplied
`letz-brand-kit.zip`; the other project identities are not packaged here.
