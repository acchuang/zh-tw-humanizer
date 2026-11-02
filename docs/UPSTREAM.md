# Upstream watch

Projects this skill tracks for ideas. Review monthly by hand, record each decision here, and bump `metadata.upstream-reviewed` in `SKILL.md`. Last review: 2026-11-02.

## Watched

| Project | Looked at | Notes |
|---|---|---|
| `humanizer-zh-next` 2.1.0 | Full `SKILL.md` | Source of most items below |
| Other zh humanizer skills on GitHub | Landing pages only | Re-read in full before copying anything |

## Adopted (1.9.0)

| Idea | Where it landed |
|---|---|
| Per-pattern "不用改" line (when not to fire) | Seven false-positive-prone patterns |
| Structure diff before/after (code fences, links, headings, tables, lists) | `scripts/check.py` |
| Review date for upstream | `metadata.upstream-reviewed` and this file |
| Reply re-explaining background the reader already confirmed | Pattern 61 |
| Casual 不是X而是Y and first-person send-offs | Watch lists in patterns 6, 15, 51 |

## Rejected

| Idea | Why |
|---|---|
| `references/` split | `SKILL.md` stays one file |
| Grant and commercial branches, watermark skill | Out of scope |
| Simplified-Chinese idioms | Breaks the Taiwanese-Mandarin-only contract |

## Open

- Academic over-hedging (repeated disclaimers, stacked qualifiers) is not a pattern yet; only a one-line note at the end of `SKILL.md`.
- Final-text-only default output versus our 草稿 → 審查 → 最終稿 flow. Needs a decision.
- Edit-depth modes (輕潤色 / 去 AI 味 / 深入重寫) chosen by the request, not only by genre.
