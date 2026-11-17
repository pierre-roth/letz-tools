# LëtzInitiative logo family

Six project identities, in site order: **LëtzBench → LëtzIndex → LëtzTools → LëtzEnv → LëtzCorpus → LëtzLM**. The umbrella LëtzInitiative is included as a seventh identity.

All use the existing original 5×7 vector glyphs and the tall L. The compact icon is intentionally the same family symbol for every project; use the wordmark or visible name to distinguish projects. No new platform logos, mascots, rounded shapes or background plates are introduced.

## Colours

| Element | Light mode | Dark mode |
|---|---|---|
| Logo red | #EF3340 | #EF3340 |
| Logo blue | #00A3E0 | #00A3E0 |
| Lettering | #1A232C | #EFF3F7 |

The selected screen approximations correspond to the supplied Luxembourg flag references, Pantone Red 032 C and Pantone 299 C. These HEX values are design choices for digital use, not legally defined flag HEX values. Print work should use the Pantone references and a print proof. The logo accent colours remain fixed when the website theme changes. UI colours remain independent: muted red/blue and contrast adjustments are appropriate for text and controls.

Colour references from the approved starting kit:
- Luxembourg Government: https://luxembourg.public.lu/content/dam/luxembourg/publications/a-propos-des-symboles-de-l-etat-et-de-la-nation/a-propos-des-symboles-de-l-etat-et-de-la-nation-fr.pdf
- Red 032 C digital pairing: https://www.bpfomento.pt/fotos/documentos/manual_normas_e_identidade_bpf_127431276566632e23ce620.pdf
- 299 C digital pairing: https://brandguide.asu.edu/elements-guidelines/design/color

## Files

`svg/letz{project}-{wordmark|icon|lockup}-{on-light|on-dark|black|white}.svg`

Each name has SVG masters, matching transparent PNGs and a default alias using the light-background variant. The icon PNG master is 512×512; small icons are exported at 24, 32 and 48 pixels in all four variants. Black and white variants are true monochrome, including the dots. The underscore-free project IDs are bench, index, tools, env, corpus, lm and initiative.

SVGs contain paths and groups only, without installed fonts, scripts, remote resources or embedded raster images. PNG files contain alpha transparency; the preview board deliberately uses backgrounds for comparison. Use the SVG wherever possible. Preserve proportions and the icon's clear space. Don't stretch, round, invert, tint or add shadows to the assets. Do not automatically invert the coloured logos in dark mode; select the on-dark variant instead.

## Typography and sizing

Wordmarks are original drawn lettering, not a named font. Body text uses Arial/Helvetica/sans-serif; labels use SFMono-Regular/Consolas/Liberation Mono/monospace. The icon is suitable from 24px; 32–48px is preferred. For long wordmarks, use at least roughly four screen pixels per vector unit. Keep a visible project name beside the shared icon in lists and pickers.

## Reproduction

From the parent proposal directory:

```
node branding/source/build.mjs
python3 branding/source/render.py
npm test
```

The website build refreshes the kit’s glyph source snapshot from the shared site source, avoiding a separate branding implementation. Existing ImageMagick and Pillow render PNGs; the website itself requires neither. Source files are included in the archive, including the shared glyph source snapshot. `validation.json` records dimensions, transparency, portable SVGs and the fixed red/blue pixel samples. `manifest.json` records SHA-256 hashes.

Local proposal only. Nothing uploaded or deployed.
