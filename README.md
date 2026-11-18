<picture>
  <source media="(prefers-color-scheme: dark)" srcset="skills/luxembourgish-writing/assets/letztools-wordmark-on-dark.svg">
  <img src="skills/luxembourgish-writing/assets/letztools-wordmark-on-light.svg" width="340" alt="LëtzTools">
</picture>

Write and proofread Luxembourgish in ChatGPT and Claude. Check spelling with
spellchecker.lu, look up words and forms in LOD, and consult the official
orthography guide.

## Install from GitHub

- **ChatGPT (workspaces):** a workspace admin opens **Admin Console › Plugins › Add › Import marketplace**
  and enters `https://github.com/pierre-roth/letz-tools` as the source. Leave **Path**
  and **Branch** blank. After import, workspace members install **LëtzTools** from
  **Plugins**. [OpenAI import guide](https://help.openai.com/en/articles/20001504-importing-and-syncing-plugin-marketplaces-from-github)
- **Claude (chat and Cowork):** open **Customize › Plugins**, choose **Add marketplace**,
  enter `pierre-roth/letz-tools`, then install **LëtzTools**. On Team and Enterprise
  plans, an owner can add it for everyone under **Organization settings › Plugins & skills**.
- **Claude Code:** `/plugin install letz-tools --marketplace pierre-roth/letz-tools`

Try: “Improve this Luxembourgish email without changing its meaning.”

No server or API key to set up. Live checks you authorize send words or lookups to
`lod.lu`; the guide downloads from `zls.gouvernement.lu`. If Claude says it could not
reach them, allow these sites under **Settings › Capabilities**, or ask your
administrator.

[Support](https://github.com/pierre-roth/letz-tools/issues) · [Privacy](https://github.com/pierre-roth/letz-tools/blob/main/docs/PRIVACY.md) · [Terms](https://github.com/pierre-roth/letz-tools/blob/main/docs/TERMS.md)
