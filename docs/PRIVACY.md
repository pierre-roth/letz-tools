# LëtzTools privacy policy

LëtzTools is an independent Luxembourgish writing tool maintained by Pierre Roth. It has no account system, backend, analytics or advertising. The maintainer does not receive your draft, tool queries or conversation when you use the skill.

## What the skill sends

- **Live spelling:** With your permission, the helper sends the eligible words from the Luxembourgish text you want checked to `lod.lu`, operated by the Zenter fir d’Lëtzebuerger Sprooch (ZLS). It sends distinct word tokens in batches. If a word is flagged, it requests suggestions using that word. The helper reconstructs the findings in context in the assistant’s execution environment.
- **Live dictionary:** With your permission, the helper sends words, short search terms or dictionary entry IDs to `lod.lu` to retrieve meanings, usage examples or word forms.
- **Orthography:** The helper downloads the public guide from `zls.gouvernement.lu` and searches it in the execution environment. It does not send your draft or rule search terms to the publisher. Network requests expose ordinary connection details, such as the calling environment’s IP address, to the recipient.

Do not use the skill on content containing payment-card data, protected health information, government IDs, login credentials or other sensitive personal data. Remove confidential or identifying details before asking for a live check. You can decline live lookups or ask the assistant to review your writing without sending it to LOD.

## Retention and controls

- **LëtzTools:** The helpers do not keep a history of draft text or lookups. If a temporary draft file is needed, the skill directs the assistant to remove it after the check. The only cache the helpers maintain contains public orthography material. It is refreshed after seven days when the guide is used and can be removed by deleting the execution environment’s `letztools-orthography-v2` temporary directory.
- **Language services:** The [spellchecker.lu privacy notice](https://spellchecker.lu/info/#dateschutz) says full texts are not stored, checked words are kept anonymously for statistics, and IP addresses kept for security are deleted after three months. It does not give a retention period for those word statistics. LëtzTools does not control the separate retention practices of LOD dictionary endpoints or the [government website](https://zls.gouvernement.lu/lb/support/aspects-legaux.html) that supplies the guide.
- **Assistant platform:** Your host may store your conversation, files and tool activity according to its own settings and policies. For retention and deletion controls, see the [OpenAI privacy policy](https://openai.com/policies/privacy-policy/) or [Anthropic privacy policy](https://www.anthropic.com/legal/privacy), as applicable.
- **Support:** [GitHub Issues](https://github.com/pierre-roth/letz-tools/issues) are public. The maintainer uses what you post there to investigate the issue and respond. Posts are retained on GitHub as part of the issue record and are subject to [GitHub’s privacy statement](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement). You can edit your posts to remove details; use a synthetic example and never post personal data or private documents.

You can stop using the skill or uninstall it at any time. For questions about these practices, use [LëtzTools support](https://github.com/pierre-roth/letz-tools/issues) without including personal information in the public issue.
