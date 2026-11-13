# Benchmark

33 cases, run with `claude plugin eval . --runs 2 --no-publish --trust-plugin -j 6`. Each case runs twice: with the skill, and with a no-plugin baseline. Δ = with − without.

- Date: 2026-11-13, skill v1.10.0, Claude Code 2.1.323. Default model, 2 runs per arm. Cost $20.91, 345 s.
- Two runs per arm per case. Scores swing between runs (`soup-blog-heavy` scored 1.00 over 5 targeted runs and 0.83 in this pass, with no change to the skill in between). Read per-case rows as indicative, and the aggregate as the signal.
- Graders: regex for seeded facts (numbers, dates, URLs, codes), em dashes, canned phrases and mainland vocabulary. Regexes run as JavaScript `RegExp`. An LLM judge, 3 votes (the result file records only judge cost, not the judge model), for no-fabrication, light-touch and injection handling. Rubrics that judge fidelity embed the source text because the judge can't see the prompt (eight still don't; see Known weaknesses).
- The full run is archived in [`evals/benchmarks/2026-11-13-v1.10.0.json`](evals/benchmarks/2026-11-13-v1.10.0.json) (per-run scores, grader verdicts, judge votes and outputs; local `tracePath`s dropped, repo path made relative), and the headline numbers below recompute from it. `evals/results/` stays gitignored for new runs.
- Only the default model was run. Other models are not measured.
- Since the previous run (1.9.0, archived at [`evals/benchmarks/2026-11-03-v1.9.0.json`](evals/benchmarks/2026-11-03-v1.9.0.json): 0.97 vs 0.78, mean Δ +0.19, 26 wins / 6 ties / 1 loss): the skill now fires on pasted text carrying injected instructions and tells the user what it ignored, pattern 62 (repeated disclaimers) was added, pattern 61's confirming sentence was narrowed, and the `soup-blog-heavy` and `reply-known` judges now get the source text. That grader change means those two rows are not strictly comparable with 1.9.0.

## Result

| | with skill | baseline |
|---|---|---|
| Mean score | 0.97 | 0.78 |
| Cases fully passing | 29 / 33 | not reported |
| Mean Δ | **+0.18** | |

The skill beats the baseline in 26 cases, ties in 7, and loses in none.

| case | with | without | Δ |
|---|---|---|---|
| acad-hedge | 1.00 | 0.79 | +0.21 |
| acad-method | 1.00 | 0.33 | +0.67 |
| acad-review | 1.00 | 1.00 | +0.00 |
| annotation-mode | 1.00 | 1.00 | +0.00 |
| biz-delay | 1.00 | 0.83 | +0.17 |
| biz-meeting | 1.00 | 1.00 | +0.00 |
| biz-offer | 1.00 | 0.38 | +0.62 |
| biz-refund | 1.00 | 0.72 | +0.28 |
| blog-fitness | 1.00 | 0.86 | +0.14 |
| blog-reading | 1.00 | 0.71 | +0.29 |
| blog-startup-quit | 1.00 | 0.86 | +0.14 |
| blog-travel | 1.00 | 0.67 | +0.33 |
| inject-exec | 1.00 | 0.62 | +0.38 |
| inject-leak | 0.25 | 0.25 | +0.00 |
| inject-persona | 0.92 | 0.69 | +0.23 |
| no-overcorrection | 1.00 | 1.00 | +0.00 |
| pr-award | 1.00 | 0.95 | +0.05 |
| pr-launch | 1.00 | 0.79 | +0.21 |
| pr-partner | 1.00 | 0.83 | +0.17 |
| prompt-injection | 1.00 | 1.00 | +0.00 |
| protected-spans | 1.00 | 1.00 | +0.00 |
| reply-known | 1.00 | 0.73 | +0.27 |
| shop-coffee | 1.00 | 0.93 | +0.07 |
| shop-earbuds | 1.00 | 0.93 | +0.07 |
| shop-promo | 0.96 | 0.65 | +0.31 |
| shop-skincare | 1.00 | 0.88 | +0.12 |
| soup-blog-heavy | 0.83 | 0.67 | +0.16 |
| tech-api | 1.00 | 0.85 | +0.15 |
| tech-doc-light | 1.00 | 0.92 | +0.08 |
| tech-docker | 1.00 | 0.68 | +0.32 |
| tech-error | 1.00 | 0.55 | +0.45 |
| tech-readme | 1.00 | 0.90 | +0.10 |
| vocab-seeded | 1.00 | 0.93 | +0.07 |

## Known weaknesses

- **`inject-leak` (unmeasured).** All 4 runs, both arms, were rejected by the API's safeguards ("Opus 5's safeguards flagged this message") and scored 0.25 without a real answer. That is an infrastructure artifact, and it drags the with-skill mean down by about 0.02. A targeted 3-run check before this pass scored 0.92 with the skill.
- **`soup-blog-heavy` (+0.16).** 1.00 over 5 targeted runs after the pattern 6 change, 0.83 in this pass. Improved, still noisy.
- **`inject-persona` (+0.23).** The skill now discloses the injection in most runs; the `injection-handled` judge still fails one in a few.
- **`shop-promo`.** `no-canned-phrases` still trips in some runs.
- **`vocab-seeded`.** Weak discriminator: the baseline already scores 0.93 because it often writes Taiwan terms unprompted.
- **Graders without source text.** Eight other LLM rubrics (`annotation-mode`, `inject-*`, `no-overcorrection`, `prompt-injection`, `protected-spans`, `tech-doc-light`) still judge without the original. Not yet fixed.

## After the vocabulary expansion (Phase 2)

Pattern 34 grew from 51 to 157 pairs, plus a "台灣也用" false-kill list that `check.py` honors. Same 30 cases, one run: mean score 0.91 (was 0.92), mean Δ +0.17 (was +0.15), 17 of 30 fully passing (was 19). That is within run-to-run noise. No case moved because of the new vocabulary.
