# Mobile Game Progression-Gate A/B Test (Cookie Cats)

**Product question:** Does moving the first forced-wait gate from level 30 to level 40 change player retention, and should it ship?

**Answer:** No. Moving the gate to level 40 **lowered 7-day retention by 0.82 percentage points** (19.02% → 18.20%, 95% CI [-1.33, -0.31] pp, p = 0.0016). Recommendation: keep the gate at level 30.

## Data
[Mobile Games A/B Testing – Cookie Cats](https://www.kaggle.com/datasets/mursideyarkin/mobile-games-ab-testing-cookie-cats) (Kaggle): 90,189 players randomly assigned at install to `gate_30` (control) or `gate_40` (treatment).
Columns: `userid`, `version`, `sum_gamerounds` (rounds played in first 14 days), `retention_1`, `retention_7`.
The CSV is not committed; download it and save as `data/cookie_cats.csv`.

## Metrics
| Role | Metric |
|---|---|
| Primary | 7-day retention |
| Secondary | 1-day retention |
| Guardrail | Game rounds in first 14 days |

## Method
1. **SQL (DuckDB)** – group sizes, duplicate/null checks, retention by arm, outlier inspection, retention by engagement bucket (`sql/01_load_and_check.sql`).
2. **Experiment health** – sample-ratio-mismatch (SRM) chi-square test against a 50/50 split.
3. **Inference** – two-proportion z-tests with 95% CIs, cross-checked with a 10,000-resample bootstrap; Bonferroni threshold (p < 0.025) for the two retention metrics.
4. **Heavy-tailed engagement** – Mann-Whitney U, Welch t-test on log(1 + rounds), and a trimmed comparison.
5. **Power** – minimum detectable effect and required sample sizes.

## Results
| Group | Users | 1-day retention | 7-day retention |
|---|---|---|---|
| gate_30 (control) | 44,700 | 44.82% | 19.02% |
| gate_40 (treatment) | 45,489 | 44.23% | 18.20% |

| Metric | Difference (gate_40 − gate_30) | 95% CI | p-value |
|---|---|---|---|
| 7-day retention (primary) | **−0.82 pp** | [−1.33, −0.31] | 0.0016 |
| 7-day retention, bootstrap | −0.82 pp | [−1.32, −0.33] | – |
| 1-day retention (secondary) | −0.59 pp | [−1.24, +0.06] | 0.074 (not significant) |

**Guardrail (game rounds).** Medians are 17 (gate_30) and 16 (gate_40). Mann-Whitney p = 0.050 and log-scale Welch t-test p = 0.070 are borderline. One gate_30 player logged 49,854 rounds (next highest: 2,961); the raw-rounds t-test after removing that single user gives p = 0.95, so the apparent difference in mean rounds is driven by that outlier and raw means should not be trusted.

**Power.** With ~44,700 users per arm, 80% power and α = 0.05, the minimum detectable effect on 7-day retention is ≈ 0.74 pp. Detecting a 0.5 pp difference would need ≈ 97,700 users per arm; 1.0 pp needs ≈ 24,700.

## Limitations
- **Mild sample-ratio imbalance:** 44,700 vs 45,489 users (chi-square p = 0.0086). This does not cross the strict 0.001 alarm threshold but is below 0.05; it is reported rather than ignored. Cause unknown from the data provided.
- **No revenue or ad data:** the result only says retention is worse under gate_40. Monetization effects of the gate placement cannot be assessed.
- **Zero-round players** (~4.3–4.5%) are kept in all analyses because assignment happened at install; excluding them would break the randomization.
- Only one outcome window per metric; no segment (new vs. returning player) analysis.

## Reproduce
```bash
pip install pandas numpy scipy duckdb
# save the Kaggle CSV as data/cookie_cats.csv
python src/step1_sql_checks.py     # SQL metrics, data checks, SRM test
python src/step2_inference.py      # z-tests, bootstrap, rounds tests, power
```

## Repository layout
```
sql/01_load_and_check.sql      all metric and validation queries
src/step1_sql_checks.py        loads data into DuckDB, runs the SQL, SRM test
src/step2_inference.py         statistical inference and power analysis
```
