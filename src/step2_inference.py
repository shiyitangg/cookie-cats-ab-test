"""Step 2: statistical inference for the Cookie Cats A/B test (scipy/numpy only).
Usage: python src/step2_inference.py [path_to_csv]
Control = gate_30, Treatment = gate_40.
"""
import sys
import numpy as np, pandas as pd
from scipy import stats

CSV = sys.argv[1] if len(sys.argv) > 1 else "data/cookie_cats.csv"
rng = np.random.default_rng(42)
ALPHA = 0.05

df = pd.read_csv(CSV)
for c in ["retention_1", "retention_7"]:
    df[c] = df[c].astype(str).str.lower().map({"true": 1, "false": 0, "1": 1, "0": 0})
ctrl, trt = df[df.version == "gate_30"], df[df.version == "gate_40"]

def two_prop(x1, n1, x2, n2, label):
    p1, p2 = x1 / n1, x2 / n2
    diff = p2 - p1                                   # treatment - control
    pool = (x1 + x2) / (n1 + n2)
    z = diff / np.sqrt(pool * (1 - pool) * (1 / n1 + 1 / n2))
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    se = np.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    lo, hi = diff - 1.96 * se, diff + 1.96 * se
    print(f"{label}: gate_30={p1:.4%}  gate_40={p2:.4%}  diff={diff*100:+.3f} pp  "
          f"95% CI [{lo*100:+.3f}, {hi*100:+.3f}] pp  z={z:.3f}  p={p:.4f}")
    return diff, p

print("=== Two-proportion z-tests (treatment - control) ===")
for m in ["retention_7", "retention_1"]:
    two_prop(ctrl[m].sum(), len(ctrl), trt[m].sum(), len(trt), m)
print(f"Bonferroni threshold for 2 metrics: p < {ALPHA/2:.3f}\n")

print("=== Bootstrap CI for 7-day retention difference (10,000 resamples) ===")
a, b = ctrl.retention_7.values, trt.retention_7.values
boot = np.array([rng.choice(b, len(b)).mean() - rng.choice(a, len(a)).mean() for _ in range(10000)])
print(f"diff={(b.mean()-a.mean())*100:+.3f} pp  bootstrap 95% CI "
      f"[{np.percentile(boot,2.5)*100:+.3f}, {np.percentile(boot,97.5)*100:+.3f}] pp\n")

print("=== Guardrail: game rounds (heavy-tailed -> non-parametric) ===")
u, p = stats.mannwhitneyu(ctrl.sum_gamerounds, trt.sum_gamerounds, alternative="two-sided")
print(f"Mann-Whitney U p={p:.4f} | medians: gate_30={ctrl.sum_gamerounds.median()}, gate_40={trt.sum_gamerounds.median()}")
t_all = stats.ttest_ind(np.log1p(ctrl.sum_gamerounds), np.log1p(trt.sum_gamerounds), equal_var=False)
print(f"Welch t-test on log(1+rounds) p={t_all.pvalue:.4f}")
cap = df.sum_gamerounds.max()
trim = df[df.sum_gamerounds < cap]
t_trim = stats.ttest_ind(trim[trim.version=='gate_30'].sum_gamerounds,
                         trim[trim.version=='gate_40'].sum_gamerounds, equal_var=False)
print(f"Welch t-test on raw rounds after dropping the single max value ({cap}): p={t_trim.pvalue:.4f}\n")

print("=== Power / MDE (7-day retention, alpha=0.05, power=0.80) ===")
n = min(len(ctrl), len(trt)); p0 = a.mean()
z_a, z_b = stats.norm.ppf(1 - ALPHA / 2), stats.norm.ppf(0.80)
mde = (z_a + z_b) * np.sqrt(2 * p0 * (1 - p0) / n)
print(f"Baseline 7-day retention={p0:.4%}, n per arm={n:,} -> MDE ≈ {mde*100:.3f} pp")
for target in [0.005, 0.01]:
    p1 = p0 + target
    n_req = ((z_a + z_b) ** 2 * (p0*(1-p0) + p1*(1-p1))) / target ** 2
    print(f"To detect {target*100:.1f} pp: need ≈ {int(np.ceil(n_req)):,} users per arm")
