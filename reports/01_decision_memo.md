# Decision Memo: Moving the First Progression Gate (Level 30 → 40)

**To:** Product Manager, Cookie Cats  **From:** Shiyi Tang  **Date:** October 2026
**Decision requested:** Ship the level-40 gate to all players?

## Recommendation
**Do not ship.** Keep the gate at level 30. The level-40 gate reduced 7-day retention, and the experiment shows no offsetting benefit.

## Evidence
90,189 players were randomly assigned at install to a gate at level 30 (control, 44,700 players) or level 40 (treatment, 45,489 players).

| Metric | Level 30 | Level 40 | Difference | 95% CI | Significant? |
|---|---|---|---|---|---|
| **7-day retention (primary)** | 19.02% | 18.20% | **−0.82 pp** | [−1.33, −0.31] | Yes (p = 0.0016) |
| 1-day retention | 44.82% | 44.23% | −0.59 pp | [−1.24, +0.06] | No (p = 0.074) |
| Game rounds (guardrail) | median 17 | median 16 | – | – | Borderline (p ≈ 0.05) |

- The entire confidence interval for 7-day retention is below zero, so a harmful effect is the best-supported conclusion. A bootstrap interval ([−1.32, −0.33]) agrees.
- In practical terms: roughly **820 fewer players returning at day 7 per 100,000 installs** (plausible range 310–1,330), about a 4% relative drop.
- 1-day retention points the same way but is not conclusive.
- Mean game rounds look similar between groups once a single player with 49,854 rounds is removed, so engagement does not offset the retention loss. Raw means should not be used for this metric.

## Risks and limitations
- **No revenue or ad data.** Later gates could raise monetization; this experiment cannot measure that. The recommendation rests on retention alone.
- **Mild sample imbalance** (44,700 vs 45,489; chi-square p = 0.0086). Not severe by the usual strict threshold, but the cause is unknown and should be checked with the engineering team.
- **Mechanism untested.** Why a later gate hurts retention is not established by this data; any explanation (for example, players hitting friction later but with more invested) is a hypothesis.
- **Sensitivity.** The test could reliably detect effects of about 0.74 pp or larger. Smaller true effects, including benefits from the later gate, would not have been detectable.

## Next steps
1. Add revenue and ad-impression metrics to the experiment readout before any future gate test.
2. If the team still wants to explore later gating, test an intermediate position (or a softer gate) against level 30. Detecting a 0.5 pp retention difference needs about 97,700 players per arm.
3. Check why the groups are not exactly equal in size.
4. Segment results by new versus returning players if that data becomes available.
