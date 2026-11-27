# Upstream watch

Projects this skill tracks for ideas. Review monthly by hand, record each decision here, and bump `metadata.upstream-reviewed` in `SKILL.md`. Last review: 2026-11-27.

## Watched

| Project | Looked at | Notes |
|---|---|---|
| `humanizer-zh-next` 2.1.0 | Full `SKILL.md` | Source of most items below (no new release since 2026-10-15) |
| `blader/humanizer` 4.0.0 | README only | Dropped its no-invention rule |
| `Aboudjem/humanizer-skill` | README only | Local score, voice presets, sentence-rhythm signals |
| `conorbronsdon/avoid-ai-writing` 3.39 | README & release notes | Tiered tables, 74 patterns, pre-commit gates, Liang 2023 citation |
| `slivenred/humanizer-zh-TW-Pro` | README & summary | Semantic fidelity, voice-sample isolation, SEO keywords, tech exemptions |
| `Raymondhou0917/speak-human-tw` | README & summary | 38 patterns, half-width punctuation, literary personification |
| `kevintsai1202/Humanizer-zh-TW`, `yelban/humanizer.TW`, `ZeddYu/humanizer_zh` | READMEs | Tracked zh-TW / zh peers |

## Adopted (1.9.0)

| Idea | Where it landed |
|---|---|
| Per-pattern "不用改" line (when not to fire) | Seven false-positive-prone patterns |
| Structure diff before/after (code fences, links, headings, tables, lists) | `scripts/check.py` |
| Review date for upstream | `metadata.upstream-reviewed` and this file |
| Reply re-explaining background the reader already confirmed | Pattern 61 |
| Casual 不是X而是Y and first-person send-offs | Watch lists in patterns 6, 15, 51 |

## Adopted (1.10.0)

| Idea | Where it landed |
|---|---|
| Academic over-hedging (repeated disclaimers, stacked qualifiers) | Pattern 62 |
| Edit depth chosen by the request (輕潤色 / 深入重寫) | One level down or up from the 場景力度 table; no separate mode |
| Final-text-only output | Kept 草稿 → 審查 → 最終稿 as the default; final text only when the user asks (already in 貼文模式) |

## Adopted (1.11.0)

| Idea | Where it landed |
|---|---|
| Voice-matching isolation (never copy sample facts/opinions into rewrite) | §語音校準 |
| Semantic fidelity (negation, conditions, attribution, causal/temporal order) | §你的任務 #3 |
| User-specified SEO keywords / terms locked | §保護清單 |
| Anti-overstripping guard for short product copy & travel posts | §場景力度 |
| Technical false-positive exemptions (閉環控制, 鏈路聚合, 核心 dump) & 26 tech/dev/corporate vocab rows | Pattern 34 |
| Pre-emptive defensive hedging watchwords & over-literary personification note | Patterns 62, 3 |
| Half-width punctuation check & expanded `--patterns` advisory patterns | Pattern 40, §流程第 6 步, `scripts/check.py` |
| Annotation/review trigger words in frontmatter | `SKILL.md` frontmatter `description` |

## Rejected

| Idea | Why |
|---|---|
| `references/` split (also in `avoid-ai-writing`, `humanizer-zh-TW-Pro`) | `SKILL.md` stays one file |
| Grant and commercial branches, watermark skill | Out of scope |
| Simplified-Chinese idioms | Breaks the Taiwanese-Mandarin-only contract |
| blader/humanizer 4.0.0: allow adding facts | Breaks our no-invention rule (保護清單 > 不捏造) |
| Single 0–100 "AI-tell" score (Aboudjem/humanizer-skill) | Invites gaming the number instead of reading the hits; `check.py` stays per-hit and advisory |
| Voice presets (Aboudjem/humanizer-skill) | Overlaps 語音校準 |
| Interactive list-before-edit as default (`speak-human-tw`) | Keep one-shot rewrite default; annotation mode covers list-only review |

## Open

None.
