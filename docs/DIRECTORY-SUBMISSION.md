# Claude directory submission (prepared, not submitted)

Status: **not submitted**. Prepared 17 November 2026 against Anthropic's
[submission guide](https://claude.com/docs/plugins/submit) and
[pre-submission checklist](https://claude.com/docs/plugins/pre-submission-checklist.md).

## Blockers needing the owner's decision

1. **Licence.** The directory refuses plugins without a `LICENSE` file or a
   `license` SPDX id in `.claude-plugin/plugin.json`. No licence has been chosen.
   The vendored pypdf keeps its own BSD-3-Clause licence.
2. **Public repository.** Validation and submission can run on a private repository
   (the Claude GitHub App must be installed on it), but publishing needs a public
   one. Keep the repository private until you decide to publish.
3. **Large vendored file.** `scripts/vendor/pypdf/_codecs/adobe_glyphs.py` is 564 KiB.
   The checklist asks for non-image files under 256 KiB; expect it to be held for a
   reviewer or refused. Options: ask the reviewer, or trim pypdf (a maintainer change
   that must be retested).
4. **Plan.** Submitting needs a Pro, Max, Ultra, Team or Enterprise account.

## Form values

- Portal: https://claude.ai/directory/manage → **Submit new** → **Plugin bundle**
- Repository: `pierre-roth/letz-tools`; Plugin path: *(empty, repository root)*;
  Branch: `main`
- Listing details come from `.claude-plugin/plugin.json` and `README.md`.
  Icon: `assets/icon.png`, the square L icon (512×512 PNG).
- Optional URL fields (`documentationUrl`, `supportUrl`, `privacyPolicyUrl`,
  `termsOfServiceUrl`) are unset. Add them to `plugin.json` once public pages exist.

## Data handling (draft answers)

- Personal data: the user's draft text is split into words. Those words go to the
  public LOD spellchecker API (`lod.lu`). Lookup queries also go to `lod.lu`.
- Other services: `lod.lu` (Luxembourg Online Dictionary and spellchecker backend)
  and `zls.gouvernement.lu` (the official orthography PDF). There is no LëtzTools
  server and no analytics.
- Retention: the helpers store no user text. A public-reference index of the
  orthography guide is cached in the system temporary directory.
- Under-18 use: not targeted.

## Compliance

The contact email and the four acknowledgements must be entered by the owner in
the portal.
