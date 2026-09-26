"""
statistical_analysis.py -- Rail-Guard: does bolt count actually separate the readings?

This answers the question directly, with numbers, not just "the chart looks
separated": does the number of tightened bolts produce a real, statistically
meaningful difference in the vibration ratio, or could the pattern we're
seeing just be noise?

What it does:
  1. Loads every "Accurate Readings" capture for 0, 1, 2, 3, and 4 bolts
     tight (3 repeats each -- 15 readings total).
  2. Computes the same low/high energy ratio fft_analysis.py and
     classify_tightness.py use (30-60 Hz energy / 60-100 Hz energy).
  3. Reports the mean, spread, and range of that ratio for each bolt count.
  4. Runs two group-difference tests across all 5 bolt counts at once:
       - One-way ANOVA (assumes roughly normal data)
       - Kruskal-Wallis (doesn't assume normality -- better fit for n=3)
  5. Runs a pairwise test between each *adjacent* bolt count (0 vs 1, 1 vs 2,
     2 vs 3, 3 vs 4) to see which specific boundaries are backed by the data.
  6. Saves a plot showing every individual reading's ratio, grouped by bolt
     count, so the separation (or lack of it) is visible at a glance.

Be upfront about what n=3 per group means:
  With only 3 repeats per bolt count, a pairwise test (Mann-Whitney U) can
  mathematically never produce a p-value below 0.1 -- there just aren't
  enough possible orderings of 3-vs-3 data for anything stronger. So "not
  statistically significant at p<0.05" for a pairwise comparison here isn't
  a failure of the project, it's a hard limit of only having 3 readings per
  state. The more honest evidence is the overall pattern: whether the 5
  group means are monotonically ordered (0 > 1 > 2 > 3 > 4) with little or
  no overlap between the ranges -- that's what this script highlights.

USAGE (from inside the folder with your capture CSVs, with fft_analysis.py
in the same folder as this script):

    python statistical_analysis.py
"""

import glob
import re

import numpy as np
import pandas as pd
from scipy import stats

from fft_analysis import load_and_trim, run_fft, low_high_ratio

FILE_PATTERN = "capture_{n}vibrating*.csv"


def collect_ratios():
    """Return a dict of {bolts_tight: [ratio, ratio, ratio]} for 0-4 bolts."""
    data = {}
    for n in range(5):
        files = sorted(glob.glob(FILE_PATTERN.format(n=n)))
        ratios = []
        for path in files:
            mag, *_ = load_and_trim(path)
            freqs, amp, _ = run_fft(mag)
            ratios.append(low_high_ratio(freqs, amp))
        data[n] = ratios
        print(f"{n} bolts tight: {len(files)} files -> ratios = {[round(r, 3) for r in ratios]}")
    return data


def describe_groups(data):
    print("\n=== Group statistics (ratio, per bolt count) ===")
    rows = []
    for n, ratios in data.items():
        arr = np.array(ratios)
        rows.append({
            "bolts_tight": n,
            "n": len(arr),
            "mean": round(arr.mean(), 4),
            "std": round(arr.std(ddof=1), 4) if len(arr) > 1 else float("nan"),
            "min": round(arr.min(), 4),
            "max": round(arr.max(), 4),
        })
    df = pd.DataFrame(rows)
    print(df.to_string(index=False))
    return df


def overall_group_test(data):
    print("\n=== Overall test: do all 5 bolt counts differ as a group? ===")
    groups = [data[n] for n in range(5)]

    f_stat, p_anova = stats.f_oneway(*groups)
    print(f"One-way ANOVA:      F = {f_stat:.3f}   p = {p_anova:.5f}")

    h_stat, p_kw = stats.kruskal(*groups)
    print(f"Kruskal-Wallis:      H = {h_stat:.3f}   p = {p_kw:.5f}")

    # Effect size (eta-squared) for the ANOVA: how much of the total
    # variation in ratio is explained by which bolt count group it's in.
    all_vals = np.concatenate(groups)
    grand_mean = all_vals.mean()
    ss_between = sum(len(g) * (np.mean(g) - grand_mean) ** 2 for g in groups)
    ss_total = sum((v - grand_mean) ** 2 for v in all_vals)
    eta_sq = ss_between / ss_total
    print(f"Eta-squared (effect size): {eta_sq:.4f}  "
          f"({eta_sq * 100:.1f}% of the variation in ratio is explained by bolt count)")

    return {"anova_p": p_anova, "kruskal_p": p_kw, "eta_squared": eta_sq}


def pairwise_adjacent_tests(data):
    print("\n=== Pairwise tests: adjacent bolt counts ===")
    print("(Mann-Whitney U with n=3 vs n=3 can't go below p=0.1 -- that's a")
    print(" sample-size limit, not evidence the groups are the same.)\n")
    for a, b in [(0, 1), (1, 2), (2, 3), (3, 4)]:
        ga, gb = np.array(data[a]), np.array(data[b])
        u_stat, p_mw = stats.mannwhitneyu(ga, gb, alternative="two-sided")
        gap = ga.min() - gb.max()  # positive means ranges don't overlap
        overlap = "no overlap" if gap > 0 else "RANGES OVERLAP"
        print(
            f"{a} vs {b} bolts tight:  "
            f"mean {ga.mean():.3f} vs {gb.mean():.3f}   "
            f"Mann-Whitney p = {p_mw:.3f}   "
            f"range gap = {gap:.3f} ({overlap})"
        )


def plot_ratio_by_bolt_count(data, save_path="bolt_count_ratio_plot.png"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 5))
    rng = np.random.default_rng(0)
    for n, ratios in data.items():
        xs = n + rng.uniform(-0.08, 0.08, size=len(ratios))
        ax.scatter(xs, ratios, s=60, color="tab:blue", zorder=3)
        ax.hlines(np.mean(ratios), n - 0.2, n + 0.2, color="tab:red", linewidth=2, zorder=4)

    ax.set_yscale("log")
    ax.set_xticks(range(5))
    ax.set_xlabel("Bolts tight (out of 4)")
    ax.set_ylabel("Low/high energy ratio (log scale)")
    ax.set_title("Rail-Guard: vibration ratio by bolt count\n(each dot = one reading, red line = group mean)")
    ax.axhline(0.35, color="gray", linestyle="--", linewidth=1, label="TIGHT/LOOSE threshold (0.35)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    print(f"\nSaved plot to {save_path}")


def main():
    data = collect_ratios()
    describe_groups(data)
    overall_group_test(data)
    pairwise_adjacent_tests(data)
    plot_ratio_by_bolt_count(data)


if __name__ == "__main__":
    main()
