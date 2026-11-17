# Official orthography reference

Use the packaged helper's `guide.search(query, limit=4)` for relevant excerpts and
`guide.rule("6.1.1")` to read a complete numbered section. The CLI exposes these
operations as `rules QUERY` and `rule SECTION` (see the skill's main
instructions for the exact command).

The official source is [D’Lëtzebuerger Orthografie, sixth edition](https://zls.gouvernement.lu/lb/orthographe.html).
The first lookup downloads its public PDF and creates a local public-reference
cache. No server, account, model key or package installation is required in the
complete skill archive. Internet access to the official publisher is required for
first use. Search returns up to five excerpts; `rule` includes all child sections,
examples, remarks, exceptions, cross-references and source-page links.

Use the section identifier and printed page from the result when explaining a
correction, and link its PDF page. Preserve permitted variants and optional forms.
Read related exceptions before applying a short search excerpt. For text-layout
questions or exact visual quotations, open the linked PDF: extraction does not
preserve emphasis or table formatting.

Do not present an `unavailable`, `not_found`, or `no_matches` result as a confirmed
rule. Follow any cache freshness warning. Do not invent wording, a section number
or a rule to cover a failed lookup. Orthotrainer has different section numbering;
do not substitute its chapter numbers for this book's identifiers.

Copyright remains with the publisher. Full rule text is downloaded for the user's
consultation and is intentionally absent from this archive. The official
[legal notice](https://zls.gouvernement.lu/fr/support/aspects-legaux.html) grants
consultation/download/printing of text documents; it does not establish an open
redistribution licence for this book. Maintainer source and extraction details
are in `docs/ORTHOGRAPHY-SOURCE.md` in the project repository.
