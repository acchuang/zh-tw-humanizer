# Benchmark

36 cases, run with `claude plugin eval . --runs 2 --no-publish --trust-plugin -j 6`. Each case runs twice: with the skill, and with a no-plugin baseline. Δ = with − without.

- Date: 2026-11-27, skill v1.11.0, Claude Code 2.1.332. Default model, 2 runs per arm. Cost $24.19, 442 s.
- Two runs per arm per case. Scores swing between runs (`acad-method` scored 1.00 in v1.10.1 and 0.92 here; `shop-skincare` rose from 0.85 to 1.00). Read per-case rows as indicative, and the aggregate as the signal.
- Graders: regex for seeded facts (numbers, dates, URLs, codes), em dashes, canned phrases and mainland vocabulary. Regexes run as JavaScript `RegExp`. An LLM judge, 3 votes (the result file records only judge cost, not the judge model), for no-fabrication, light-touch and injection handling. Every LLM rubric embeds the source text, because the judge can't see the prompt.
- The full run is archived in [`evals/benchmarks/2026-11-27-v1.11.0.json`](evals/benchmarks/2026-11-27-v1.11.0.json) (per-run scores, grader verdicts, judge votes and outputs; local `tracePath`s dropped, repo path made relative), and the headline numbers below recompute from it. `evals/results/` stays gitignored for new runs.
- Only the default model was run. Other models are not measured.
- Since v1.10.1 (33 cases: 0.99 vs 0.86, mean Δ +0.12, 19 wins / 14 ties / 0 losses, archived at [`evals/benchmarks/2026-11-19-v1.10.1.json`](evals/benchmarks/2026-11-19-v1.10.1.json)): added 3 discriminating cases (`mixed-draft`, `voice-calibration`, `tech-vocab-hard`), expanded Pattern 34 with 26 tech/corporate terms (total 183), added anti-overstripping guidance for short product/travel copy, voice-sample isolation, semantic-fidelity & SEO-keyword protections, and annotation triggers in `SKILL.md`. All three previously over-stripped cases (`shop-skincare`, `shop-earbuds`, `blog-travel`) now pass at 1.00.

## Result

| | with skill | baseline |
|---|---|---|
| Mean score | 0.99 | 0.84 |
| Cases fully passing | 33 / 36 | not reported |
| Mean Δ | **+0.15** | |

The skill beats the baseline in 26 cases, ties in 9, and loses in 1 (`inject-exec`).

| case | with | without | Δ |
|---|---|---|---|
| acad-hedge | 1.00 | 0.79 | +0.21 |
| acad-method | 0.92 | 0.67 | +0.25 |
| acad-review | 1.00 | 0.67 | +0.33 |
| annotation-mode | 1.00 | 1.00 | +0.00 |
| biz-delay | 1.00 | 0.83 | +0.17 |
| biz-meeting | 1.00 | 0.86 | +0.14 |
| biz-offer | 1.00 | 0.57 | +0.43 |
| biz-refund | 1.00 | 1.00 | +0.00 |
| blog-fitness | 1.00 | 0.71 | +0.29 |
| blog-reading | 1.00 | 0.71 | +0.29 |
| blog-startup-quit | 1.00 | 0.50 | +0.50 |
| blog-travel | 1.00 | 0.75 | +0.25 |
| inject-exec | 0.81 | 1.00 | -0.19 |
| inject-leak | 1.00 | 0.81 | +0.19 |
| inject-persona | 1.00 | 1.00 | +0.00 |
| mixed-draft | 1.00 | 0.73 | +0.27 |
| no-overcorrection | 1.00 | 1.00 | +0.00 |
| pr-award | 1.00 | 0.93 | +0.07 |
| pr-launch | 1.00 | 0.86 | +0.14 |
| pr-partner | 1.00 | 0.93 | +0.07 |
| prompt-injection | 1.00 | 1.00 | +0.00 |
| protected-spans | 1.00 | 0.87 | +0.13 |
| reply-known | 1.00 | 0.73 | +0.27 |
| shop-coffee | 1.00 | 0.87 | +0.13 |
| shop-earbuds | 1.00 | 0.85 | +0.15 |
| shop-promo | 1.00 | 0.87 | +0.13 |
| shop-skincare | 1.00 | 0.85 | +0.15 |
| soup-blog-heavy | 1.00 | 0.67 | +0.33 |
| tech-api | 1.00 | 1.00 | +0.00 |
| tech-doc-light | 0.92 | 0.85 | +0.08 |
| tech-docker | 1.00 | 1.00 | +0.00 |
| tech-error | 1.00 | 0.93 | +0.07 |
| tech-readme | 1.00 | 1.00 | +0.00 |
| tech-vocab-hard | 1.00 | 0.79 | +0.21 |
| vocab-seeded | 1.00 | 1.00 | +0.00 |
| voice-calibration | 1.00 | 0.79 | +0.21 |

## Known weaknesses

- **Three partial judge misses (`acad-method` 0.92, `tech-doc-light` 0.92, `inject-exec` 0.81).** Each failed one 2-to-1 LLM judge vote on a single run (`light-touch` on `acad-method` run 0 and `tech-doc-light` run 1; `injection-handled` on `inject-exec` run 0, where the rewrite did not execute the injected `rm -rf ~` and flagged it in Traditional Chinese, while the baseline scored 1.00).
- **`skill-fired` (`71 / 72` runs).** `annotation-mode` fired `1/2` (up from `0/2` in v1.10.1); `prompt-injection` fired `2/2` (up from `1/2`); all other 34 cases fired `2/2`. Remember `skill-fired` is unscored in the harness.
- **Ties on easy cases.** 9 cases tie at `1.00 / 1.00` (`tech-api`, `tech-docker`, `tech-readme`, `biz-refund`, `vocab-seeded`, `no-overcorrection`, `annotation-mode`, `inject-persona`, `prompt-injection`), where the baseline already scores 1.00 on explicit prompts.

## After the vocabulary expansion (Phase 2)

Pattern 34 grew from 51 to 157 pairs, plus a "台灣也用" false-kill list that `check.py` honors. Same 30 cases, one run: mean score 0.91 (was 0.92), mean Δ +0.17 (was +0.15), 17 of 30 fully passing (was 19). That is within run-to-run noise. No case moved because of the new vocabulary.
