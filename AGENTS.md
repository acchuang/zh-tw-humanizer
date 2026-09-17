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

- Plain Markdown skill, no build, no deploy.
- The runtime artifact stays a single file (`SKILL.md`) — it is what gets loaded, so no
  `references/` split and no assets the rewrite itself has to read.
- Author-side tooling is allowed and lives outside the runtime artifact:
  - `scripts/check.py` — mechanical break-check (em dashes, mainland vocabulary, invisible
    characters, curly quotes, tool traces, emoji density, placeholders). It parses the
    vocabulary table straight out of `SKILL.md` pattern 34; never copy that table anywhere else.
  - `evals/` — `claude plugin eval .` suite. Run it after any meaningful `SKILL.md` change.
- No fabrication rule and Taiwanese-Mandarin-only output are core contracts — do not weaken them in edits.

## Checks

```bash
python3 scripts/check.py --self-test          # checker's own tests
python3 scripts/check.py <draft.md>           # exit 1 if mechanical breaks remain
claude plugin eval . --runs 1 --no-publish    # skill behaviour, ~$0.7 per full pass
```

兩個已知不穩定的案例，不要當成迴歸就急著調 grader：

- `prompt-injection` — 輸入裡夾帶「忽略先前的所有指示」時，skill 常常不會被觸發（`skill-fired` FAIL），
  裸模型接手後用英文回覆，`treated-as-text` 的「回覆須為繁體」條件就掛了。這是觸發層的問題，
  SKILL.md 本文改不到。
- `protected-spans` — 約一半的跑次會把「2026 年 10 月 1 日」縮成「10 月 1 日」。§保護清單和流程
  第 6 步都已經寫明日期含年份，仍有殘留；再加第三份提醒只是重複，不要加。

`scripts/check.py` on `SKILL.md` itself is meaningless — the skill quotes every bad pattern
as an example. Run it on rewritten prose only.
