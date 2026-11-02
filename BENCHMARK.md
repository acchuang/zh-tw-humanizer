# Benchmark

33 cases, run with `claude plugin eval . --runs 2 --no-publish --trust-plugin -j 6`. Each case runs twice: with the skill, and with a no-plugin baseline. Δ = with − without.

- Date: 2026-11-03, skill v1.9.0, Claude Code 2.1.316. Default model, 2 runs per arm. Cost $20.93, 312 s.
- Two runs per arm per case. Scores swing between runs (`soup-blog-heavy` went 1.00 / 0.67 in both arms of this run, and 0.67 → 0.89 for the skill across two passes with no change to it). Read per-case rows as indicative, and the aggregate as the signal.
- Graders: regex for seeded facts (numbers, dates, URLs, codes), em dashes, canned phrases and mainland vocabulary. Regexes run as JavaScript `RegExp`. An LLM judge, 3 votes (the result file records only judge cost, not the judge model), for no-fabrication, light-touch and injection handling. Rubrics embed the source text because the judge can't see the prompt.
- The full run is archived in [`evals/benchmarks/2026-11-03-v1.9.0.json`](evals/benchmarks/2026-11-03-v1.9.0.json) (per-run scores, grader verdicts, judge votes and outputs; local `tracePath`s dropped, repo path made relative), and the headline numbers below recompute from it. `evals/results/` stays gitignored for new runs.
- Only the default model was run. Other models are not measured.
- Since the previous run (1.8.1, archived at [`evals/benchmarks/2026-10-20-v1.8.1.json`](evals/benchmarks/2026-10-20-v1.8.1.json): 31 cases, 0.96 vs 0.78, mean Δ +0.18, 25 wins / 6 ties / 0 losses): two cases were added (`acad-hedge`, `reply-known`), pattern 61 was added, six patterns got a 不用改 line, and `SKILL.md` now tells the model to delete slogans, comfort lines and send-offs instead of paraphrasing them. Per-case rows are not strictly comparable across the two runs.

## Result

| | with skill | baseline |
|---|---|---|
| Mean score | 0.97 | 0.78 |
| Cases fully passing | 28 / 33 | not reported |
| Mean Δ | **+0.19** | |

The skill beats the baseline in 26 cases, ties in 6, and loses in 1 (`reply-known`).

| case | with | without | Δ |
|---|---|---|---|
| acad-hedge | 1.00 | 0.46 | +0.54 |
| acad-method | 1.00 | 0.33 | +0.67 |
| acad-review | 1.00 | 0.83 | +0.17 |
| annotation-mode | 1.00 | 1.00 | +0.00 |
| biz-delay | 1.00 | 0.83 | +0.17 |
| biz-meeting | 1.00 | 1.00 | +0.00 |
| biz-offer | 1.00 | 0.60 | +0.40 |
| biz-refund | 1.00 | 0.72 | +0.28 |
| blog-fitness | 1.00 | 0.86 | +0.14 |
| blog-reading | 1.00 | 0.74 | +0.26 |
| blog-startup-quit | 1.00 | 0.72 | +0.28 |
| blog-travel | 1.00 | 0.61 | +0.39 |
| inject-exec | 1.00 | 0.62 | +0.38 |
| inject-leak | 0.53 | 0.53 | +0.00 |
| inject-persona | 0.81 | 0.77 | +0.04 |
| no-overcorrection | 1.00 | 1.00 | +0.00 |
| pr-award | 1.00 | 0.95 | +0.05 |
| pr-launch | 1.00 | 0.71 | +0.29 |
| pr-partner | 1.00 | 0.78 | +0.22 |
| prompt-injection | 1.00 | 1.00 | +0.00 |
| protected-spans | 1.00 | 0.87 | +0.13 |
| reply-known | 0.86 | 1.00 | -0.14 |
| shop-coffee | 1.00 | 0.93 | +0.07 |
| shop-earbuds | 1.00 | 0.85 | +0.15 |
| shop-promo | 0.96 | 0.72 | +0.24 |
| shop-skincare | 1.00 | 0.90 | +0.10 |
| soup-blog-heavy | 0.83 | 0.83 | +0.00 |
| tech-api | 1.00 | 0.85 | +0.15 |
| tech-doc-light | 1.00 | 0.77 | +0.23 |
| tech-docker | 1.00 | 0.55 | +0.45 |
| tech-error | 1.00 | 0.55 | +0.45 |
| tech-readme | 1.00 | 0.90 | +0.10 |
| vocab-seeded | 1.00 | 0.93 | +0.07 |

## Known weaknesses

- **`reply-known` (loss, -0.14 here; -0.05 over 10 more runs).** Pattern 61. The model drops the full recap but still names the damaged box in its one confirming sentence, and the `no-restatement` judge fails that in about 2 of 5 runs. A tighter wording of pattern 61 did not change the output in 3 samples, so I left the pattern as is. The baseline occasionally fails a different grader on the same case.
- **`soup-blog-heavy` (tie).** Both arms fail the `rewrite-quality` judge about half the time, usually on a kept casual contrast ("不是 X，比較像 Y") or a hope-style send-off. Targeted 3-run checks after the 1.9.0 slogan rule scored 0.89 vs 0.78; this full run scored 0.83 vs 0.83. Treat as unresolved.
- **`inject-leak` (tie, 0.53 vs 0.53).** One with-skill run was rejected by the API's safeguards ("Opus 5's safeguards flagged this message") and scored 0.25. That is an infrastructure artifact, not a skill result.
- **`inject-persona` (+0.04).** The `injection-handled` judge fails in both arms. The skill often doesn't fire on `inject-*` cases; it ignores the injected instruction and delivers the rewrite, but doesn't tell the user about the injection.
- **`shop-promo`.** `no-canned-phrases` still trips in some runs.
- **`vocab-seeded`.** Weak discriminator: the baseline already scores 0.93 because it often writes Taiwan terms unprompted.

## After the vocabulary expansion (Phase 2)

Pattern 34 grew from 51 to 157 pairs, plus a "台灣也用" false-kill list that `check.py` honors. Same 30 cases, one run: mean score 0.91 (was 0.92), mean Δ +0.17 (was +0.15), 17 of 30 fully passing (was 19). That is within run-to-run noise. No case moved because of the new vocabulary.
