# Official orthography source

Verified on 17 November 2026. The primary source is the official ZLS/SCRIPT book,
[D’Lëtzebuerger Orthografie](https://zls.gouvernement.lu/lb/orthographe.html).
The [publication record](https://zls.gouvernement.lu/lb/actualites/publications/letzebuerger-orthografie.html)
was updated on 2 July 2026 and describes the sixth edition, publication year 2026,
ISBN 978-99959-1-163-8. The linked [PDF](https://zls.gouvernement.lu/dam-assets/pdfen/web-letzortho-oplo6-v01.pdf)
has an imprint stating sixth printing, Luxembourg 2024, copyright MENJE 2019.
Both dates are reported rather than inventing a new edition date.

The PDF has 120 physical pages, including covers, versus 116 pages described by
the publication record. Physical PDF pages 12–96 contain the ten orthography
chapters, numbered printed pages 10–94. The helper indexes all 183 numbered
chapters, sections and subsections, including four-part identifiers. It excludes
the preface, phonetics appendix and historical essay. A PDF link's `#page=49`
means physical PDF page 49, which is printed page 47. Results provide both.

## Reuse decision

The [ZLS legal notice](https://zls.gouvernement.lu/fr/support/aspects-legaux.html),
section “Propriété intellectuelle”, permits users to consult, download and print
text documents without a prior request. It also states that no intellectual
property licence is granted unless otherwise indicated. The PDF imprint gives a
copyright notice and no open-content licence was found. The notice's reproduction
permission for *other* types of content does not establish permission to
redistribute this text book. Accordingly, the project does **not** bundle the
PDF, extracted rule bodies, or a complete third-party text index, and does not
label the book CC0. Redistribution would require separate permission or a
verified licence applicable to the book.

The installed helper downloads the official public PDF on demand and builds a
local search cache for that user's consultation. It sends no writing, search
queries or document contents to the publisher: the only HTTP request is the PDF
GET. The cache contains public reference text only; it is outside the skill and
must not be put in release archives. Users can delete the temporary
`letztools-orthography-v2` directory to clear it. The PDF reader dependency has its
own licence in the packaged vendor directory; that licence does not apply to the
book.

## Extraction, freshness and limitations

The verified PDF is 995,307 bytes, SHA-256
`be3f14e8bdffa971b34873b51b7e7184fffe9f0e01c7e81aac4e448e5404a550`.
The parser verifies that fingerprint before applying its edition-specific page
and font profile. It uses publisher typography to distinguish headings from
examples, joins headings split across lines, and retains the original wording,
examples, remarks, exceptions and in-text cross-references. PDF bullet-font
characters are represented as `›`; other emphasis and table layout are not
reconstructed. Source text line breaks and line-end hyphens remain, so consult
the page link for typography or an exact visual quotation.

The public index is refreshed after seven days. On a network failure a previously
verified cache can be used with an explicit warning. A changed PDF fails closed
and does not silently return a stale rule. There is no automatic inference of a
new edition or fallback to a differently numbered guide. The maintainer should
recheck the landing page, imprint, legal notice, page offsets and headings when
updating the supported PDF fingerprint. Network access is required for first use;
if the agent environment cannot access the publisher, the helper returns
`unavailable` and the official source link, never a fabricated rule.

[Orthotrainer](https://orthotrainer.lu/) is another ZLS-endorsed reference. Its
published frontend uses `/api/chapters` and `/api/chapters/{id}` to retrieve HTML
rule pages. Those chapter numbers differ from the book (trainer chapter 8 is the
book's chapter 6), and its current chapter list does not include the full book
punctuation chapter. It is therefore a useful browsing reference, but is not
silently substituted for the complete numbered book.

## Verification

The actual publisher PDF was downloaded and extracted locally during development;
no third-party book text is committed as a test fixture. Checks cover all 183
numbered headings, ordering, unique identifiers, wrapped headings, cross-references
and final subsection 10.5.2. Rules 6.1.1 and 6.2.1 were checked against the PDF,
including printed/physical page numbers, continuation of 6.1.1 onto the next page,
and the optional-n examples. The source page for 6.1.1 was rendered for visual
comparison. Automated offline tests use clearly invented short examples. An
optional test runs against a locally downloaded PDF when
`LETZTOOLS_ORTHOGRAPHY_PDF` names it.
