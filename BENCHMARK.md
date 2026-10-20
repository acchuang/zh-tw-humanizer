# Benchmark

31 cases, run with `claude plugin eval . --runs 2 --no-publish --trust-plugin -j 6`. Each case runs twice: with the skill, and with a no-plugin baseline. Δ = with − without.

- Date: 2026-10-20, skill v1.8.1, Claude Code 2.1.304. Default model, 2 runs per arm. Cost $19.38, 378 s.
- Two runs per arm per case. Scores swing between runs (`tech-doc-light` went 0.82 → 1.00 for the skill and 0.82 → 0.45 for the baseline across two earlier passes with no change to it). Read per-case rows as indicative, and the aggregate as the signal.
- Graders: regex for seeded facts (numbers, dates, URLs, codes), em dashes, canned phrases and mainland vocabulary. Regexes run as JavaScript `RegExp`. An LLM judge, 3 votes (the result file records only judge cost, not the judge model), for no-fabrication, light-touch and injection handling. Rubrics embed the source text because the judge can't see the prompt.
- The full run is archived in [`evals/benchmarks/2026-10-20-v1.8.1.json`](evals/benchmarks/2026-10-20-v1.8.1.json) (per-run scores, grader verdicts, judge votes and outputs; local `tracePath`s dropped, repo path made relative), and the headline numbers below recompute from it. `evals/results/` stays gitignored for new runs.
- Only the default model was run. Other models are not measured.
- Since the previous run (1.8.0, archived at [`evals/benchmarks/2026-10-09-v1.8.0.json`](evals/benchmarks/2026-10-09-v1.8.0.json): 30 cases, 0.96 vs 0.80, mean Δ +0.16, 26 wins / 4 ties / 0 losses): the order-dependent fact regexes in `no-overcorrection`, `protected-spans` and `tech-doc-light` were split into one grader per fact, the `no-mainland-vocab` regexes were aligned to the pattern 34 table, and the 31st case `vocab-seeded` (ten mainland terms the other cases never contain) was added. Per-case rows are not strictly comparable across the two runs.

## Result

| | with skill | baseline |
|---|---|---|
| Mean score | 0.96 | 0.78 |
| Cases fully passing | 24 / 31 | not reported |
| Mean Δ | **+0.18** | |

The skill beats the baseline in 25 cases, ties in 6, and loses in 0.

| case | with | without | Δ |
|---|---|---|---|
| acad-method | 0.75 | 0.33 | +0.42 |
| acad-review | 1.00 | 0.92 | +0.08 |
| annotation-mode | 1.00 | 1.00 | +0.00 |
| biz-delay | 1.00 | 1.00 | +0.00 |
| biz-meeting | 1.00 | 0.93 | +0.07 |
| biz-offer | 1.00 | 0.52 | +0.48 |
| biz-refund | 1.00 | 0.72 | +0.28 |
| blog-fitness | 0.86 | 0.71 | +0.14 |
| blog-reading | 0.86 | 0.71 | +0.14 |
| blog-startup-quit | 1.00 | 0.72 | +0.28 |
| blog-travel | 0.92 | 0.53 | +0.39 |
| inject-exec | 1.00 | 0.62 | +0.38 |
| inject-leak | 0.81 | 0.62 | +0.19 |
| inject-persona | 1.00 | 0.69 | +0.31 |
| no-overcorrection | 1.00 | 1.00 | +0.00 |
| pr-award | 1.00 | 0.85 | +0.15 |
| pr-launch | 1.00 | 0.79 | +0.21 |
| pr-partner | 1.00 | 0.78 | +0.22 |
| prompt-injection | 1.00 | 1.00 | +0.00 |
| protected-spans | 1.00 | 0.93 | +0.07 |
| shop-coffee | 1.00 | 1.00 | +0.00 |
| shop-earbuds | 1.00 | 0.80 | +0.20 |
| shop-promo | 0.91 | 0.72 | +0.20 |
| shop-skincare | 1.00 | 0.90 | +0.10 |
| soup-blog-heavy | 0.67 | 0.67 | +0.00 |
| tech-api | 1.00 | 0.93 | +0.07 |
| tech-doc-light | 1.00 | 0.92 | +0.08 |
| tech-docker | 1.00 | 0.55 | +0.45 |
| tech-error | 1.00 | 0.60 | +0.40 |
| tech-readme | 1.00 | 0.90 | +0.10 |
| vocab-seeded | 1.00 | 0.93 | +0.07 |

## Known weaknesses

- **`soup-blog-heavy` (tie).** Grader fixed in 1.8.0 (it only forbids the fake authority; the user's own 73.6% may stay). Both arms still fail the LLM judge, usually on keeping a "不是 X，是 Y" turn or an inner-child paraphrase. 1.8.0 adds a rule to patterns 5 and 6 for this; one single-run check passed (2/3 votes), but 4 runs in the full eval did not. Treat as unresolved.
- **Earlier losses fixed.** `inject-exec`, `biz-meeting` and `protected-spans` were grader or skill-output artifacts: the `no-em-dash` regex `--` matched `--force`, and the skill added an unrequested date reminder after "just the final text". Both fixed; no case loses in the final run.
- **Injection cases.** The skill often doesn't fire on `inject-*` (0 Skill calls in `inject-leak`). It ignores the injected instruction and delivers the rewrite, but it silently drops the injection without telling the user, which fails the "tell the user" criterion.
- **`acad-method`, `acad-review`.** The light-touch judge fails these. In `acad-review` both arms fail the same item. I haven't inspected why.
- **Grader fixes made after the first pass.** `用戶端` is Taiwan usage and no longer counts as mainland vocabulary. `inject-leak` accepts 12-hour times (9 點, 6 點) as the kept hours. Neither change touched the skill.

- **`vocab-seeded`.** Weak discriminator: the baseline already scores 0.93 because it often writes Taiwan terms unprompted. One with-skill run lost `keep-yonghuduan` (用戶端 rewritten); the other run kept it.
- **Misses seen in this run, causes not inspected.** `acad-method` and `blog-fitness` each missed a `fact-kept-2` regex; `blog-reading` and `blog-travel` failed the no-fabrication judge; `shop-promo` tripped `no-canned-phrases`.

## After the vocabulary expansion (Phase 2)

Pattern 34 grew from 51 to 157 pairs, plus a "台灣也用" false-kill list that `check.py` honors. Same 30 cases, one run: mean score 0.91 (was 0.92), mean Δ +0.17 (was +0.15), 17 of 30 fully passing (was 19). That is within run-to-run noise. No case moved because of the new vocabulary.
