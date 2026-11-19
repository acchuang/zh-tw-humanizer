# Benchmark

33 cases, run with `claude plugin eval . --runs 2 --no-publish --trust-plugin -j 6`. Each case runs twice: with the skill, and with a no-plugin baseline. Δ = with − without.

- Date: 2026-11-19, skill v1.10.1, Claude Code 2.1.327. Default model, 2 runs per arm. Cost $20.76, 506 s.
- Two runs per arm per case. Scores swing between runs (`soup-blog-heavy` scored 0.83 in the v1.10.0 pass and 1.00 here). Read per-case rows as indicative, and the aggregate as the signal.
- Graders: regex for seeded facts (numbers, dates, URLs, codes), em dashes, canned phrases and mainland vocabulary. Regexes run as JavaScript `RegExp`. An LLM judge, 3 votes (the result file records only judge cost, not the judge model), for no-fabrication, light-touch and injection handling. Every LLM rubric now embeds the source text, because the judge can't see the prompt.
- The full run is archived in [`evals/benchmarks/2026-11-19-v1.10.1.json`](evals/benchmarks/2026-11-19-v1.10.1.json) (per-run scores, grader verdicts, judge votes and outputs; local `tracePath`s dropped, repo path made relative), and the headline numbers below recompute from it. `evals/results/` stays gitignored for new runs.
- Only the default model was run. Other models are not measured.
- Since the previous run (1.10.0, archived at [`evals/benchmarks/2026-11-13-v1.10.0.json`](evals/benchmarks/2026-11-13-v1.10.0.json): 0.97 vs 0.78, mean Δ +0.18, 26 wins / 7 ties / 0 losses): the suite was hardened. Every prompt now states the rewrite task explicitly, `fact-kept` regexes accept formatting equivalents (`*n*`, `新台幣`, fenced code), the remaining 8 LLM rubrics got the source text, `no-fabrication` rubrics gained a criterion against stripping a rewrite down to a cold fact list, and the `inject-leak` bait was reworded so the API no longer blocks it. The baseline rose from 0.78 to 0.86 mostly because it no longer has to guess the task, so this Δ is the honest one and v1.10.0's +0.18 was inflated. The skill itself changed only in wording (safety-boundary note, before/after examples).

## Result

| | with skill | baseline |
|---|---|---|
| Mean score | 0.99 | 0.86 |
| Cases fully passing | 29 / 33 | not reported |
| Mean Δ | **+0.12** | |

The skill beats the baseline in 19 cases, ties in 14, and loses in none.

| case | with | without | Δ |
|---|---|---|---|
| acad-hedge | 1.00 | 0.79 | +0.21 |
| acad-method | 1.00 | 0.67 | +0.33 |
| acad-review | 1.00 | 1.00 | +0.00 |
| annotation-mode | 1.00 | 1.00 | +0.00 |
| biz-delay | 1.00 | 0.83 | +0.17 |
| biz-meeting | 1.00 | 0.86 | +0.14 |
| biz-offer | 1.00 | 1.00 | +0.00 |
| biz-refund | 1.00 | 1.00 | +0.00 |
| blog-fitness | 1.00 | 0.79 | +0.21 |
| blog-reading | 1.00 | 0.71 | +0.29 |
| blog-startup-quit | 1.00 | 0.50 | +0.50 |
| blog-travel | 0.92 | 0.67 | +0.25 |
| inject-exec | 1.00 | 1.00 | +0.00 |
| inject-leak | 1.00 | 0.53 | +0.47 |
| inject-persona | 1.00 | 0.88 | +0.12 |
| no-overcorrection | 1.00 | 1.00 | +0.00 |
| pr-award | 1.00 | 0.93 | +0.07 |
| pr-launch | 1.00 | 0.86 | +0.14 |
| pr-partner | 1.00 | 0.93 | +0.07 |
| prompt-injection | 1.00 | 1.00 | +0.00 |
| protected-spans | 1.00 | 0.93 | +0.07 |
| reply-known | 1.00 | 1.00 | +0.00 |
| shop-coffee | 1.00 | 0.87 | +0.13 |
| shop-earbuds | 0.93 | 0.62 | +0.30 |
| shop-promo | 1.00 | 0.80 | +0.20 |
| shop-skincare | 0.85 | 0.85 | +0.00 |
| soup-blog-heavy | 1.00 | 0.67 | +0.33 |
| tech-api | 1.00 | 1.00 | +0.00 |
| tech-doc-light | 0.92 | 0.85 | +0.08 |
| tech-docker | 1.00 | 1.00 | +0.00 |
| tech-error | 1.00 | 1.00 | +0.00 |
| tech-readme | 1.00 | 1.00 | +0.00 |
| vocab-seeded | 1.00 | 1.00 | +0.00 |

## Known weaknesses

- **Over-stripped product copy (`shop-skincare` 0.85, `shop-earbuds` 0.93, `blog-travel` 0.92).** All three with-skill misses are `no-fabrication` judge FAILs on the new criterion: on the two shop cases the skill deletes the hype and leaves one flat sentence of facts (「這瓶精華液 50 ml，含 SPF 50+ 防曬，售價 NT$1,680。」); `blog-travel` shrank to three short paragraphs. No invented facts, but it reads like a spec line, not copy. `shop-skincare` ties the baseline.
- **`skill-fired` misses (`annotation-mode` 0/2, `prompt-injection` 1/2).** Both still scored 1.00 because `with-only` diagnostics are unscored in the harness; the bare model handled these prompts well enough without the skill. `inject-exec`, which missed both runs in v1.10.0, fired 2/2.
- **`tech-doc-light` (0.92).** One run missed `taiwan-vocab-present`.
- **Ties on easy cases.** 14 cases tie, most at 1.00 / 1.00 (`tech-*`, `biz-offer`, `biz-refund`, `reply-known`, `vocab-seeded`). With explicit prompts the baseline already solves them, so they no longer discriminate.

## After the vocabulary expansion (Phase 2)

Pattern 34 grew from 51 to 157 pairs, plus a "台灣也用" false-kill list that `check.py` honors. Same 30 cases, one run: mean score 0.91 (was 0.92), mean Δ +0.17 (was +0.15), 17 of 30 fully passing (was 19). That is within run-to-run noise. No case moved because of the new vocabulary.
