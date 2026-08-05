# zh-tw-humanizer

## Purpose

Published repo for the `zh-tw-humanizer` agent skill: removes AI writing tells from
Traditional Chinese text and localizes it to Taiwanese Mandarin. The runtime
artifact is `SKILL.md` at the repo root, kept byte-identical to the installed copy
at `~/.agents/skills/zh-tw-humanizer/SKILL.md`.

## Ownership

- This repo is the published source of truth for the skill.
- Editing workflow: change `SKILL.md` here, then sync to `~/.agents/skills/zh-tw-humanizer/SKILL.md` (installed location) and bump `metadata.version` in the frontmatter on meaningful changes.
- README and LICENSE are distribution files; keep them in sync with SKILL.md content.

## Local Contracts

- Plain Markdown skill, no build, no test, no deploy.
- Keep the skill a single file (`SKILL.md`); no bundled assets unless the skill genuinely needs them.
- No fabrication rule and Taiwanese-Mandarin-only output are core contracts — do not weaken them in edits.
