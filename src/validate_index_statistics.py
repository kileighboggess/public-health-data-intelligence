from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "county_health_burden.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 80)
print("HEALTH BURDEN INDEX — STATISTICAL VALIDATION")
print("=" * 80)

df = pd.read_csv(
    DATA_PATH,
    low_memory=False
)

print(f"\nDataset: {DATA_PATH}")
print(f"Counties: {len(df):,}")


# ============================================================
# INDICATORS
# ============================================================

INDICATORS = [
    "OBESITY",
    "DIABETES",
    "BPHIGH",
    "STROKE",
    "COPD",
    "DEPRESSION",
    "CSMOKING",
    "LPA",
    "GHLTH",
    "MHLTH",
    "ACCESS2",
]


Z_COLUMNS = [
    f"{indicator}_z"
    for indicator in INDICATORS
]


# ============================================================
# VALID SCORE CHECK
# ============================================================

print("\n" + "=" * 80)
print("1. BURDEN SCORE COMPLETENESS")
print("=" * 80)

valid_scores = df["health_burden_score"].notna().sum()
missing_scores = df["health_burden_score"].isna().sum()

print(f"Valid scores:   {valid_scores:,}")
print(f"Missing scores: {missing_scores:,}")


# ============================================================
# Z-SCORE STATISTICS
# ============================================================

print("\n" + "=" * 80)
print("2. Z-SCORE STATISTICS")
print("=" * 80)

results = []

for indicator, z_column in zip(INDICATORS, Z_COLUMNS):

    series = df[z_column].dropna()

    results.append(
        {
            "indicator": indicator,
            "observations": len(series),
            "mean": series.mean(),
            "std": series.std(),
            "min": series.min(),
            "max": series.max(),
        }
    )

z_summary = pd.DataFrame(results)

print(
    z_summary.to_string(
        index=False,
        float_format=lambda x: f"{x:.6f}"
    )
)


# ============================================================
# Z-SCORE VALIDATION
# ============================================================

print("\n" + "=" * 80)
print("3. Z-SCORE VALIDATION")
print("=" * 80)

mean_ok = np.allclose(
    z_summary["mean"],
    0,
    atol=1e-10
)

std_ok = np.allclose(
    z_summary["std"],
    1,
    atol=1e-10
)

print(f"All means approximately 0: {mean_ok}")
print(f"All standard deviations approximately 1: {std_ok}")


# ============================================================
# BURDEN SCORE RECONSTRUCTION
# ============================================================

print("\n" + "=" * 80)
print("4. BURDEN SCORE RECONSTRUCTION")
print("=" * 80)

reconstructed_score = df[Z_COLUMNS].mean(axis=1)

difference = (
    reconstructed_score
    - df["health_burden_score"]
).abs()

print(
    f"Maximum difference: {difference.max():.12f}"
)

print(
    f"Mean difference:    {difference.mean():.12f}"
)

scores_match = np.allclose(
    reconstructed_score,
    df["health_burden_score"],
    atol=1e-10
)

print(
    f"Scores reconstructed correctly: {scores_match}"
)


# ============================================================
# COMPLETENESS
# ============================================================

print("\n" + "=" * 80)
print("5. INDICATOR COMPLETENESS")
print("=" * 80)

indicator_count = (
    df[Z_COLUMNS]
    .notna()
    .sum(axis=1)
)

print(
    indicator_count
    .value_counts()
    .sort_index()
    .to_string()
)

print(
    f"\nMinimum indicators: {indicator_count.min()}"
)

print(
    f"Maximum indicators: {indicator_count.max()}"
)


# ============================================================
# PERCENTILE VALIDATION
# ============================================================

print("\n" + "=" * 80)
print("6. PERCENTILE VALIDATION")
print("=" * 80)

percentiles = df["burden_percentile"]

print(
    f"Minimum percentile: {percentiles.min():.4f}"
)

print(
    f"Maximum percentile: {percentiles.max():.4f}"
)

print(
    f"Percentiles within 0–100: "
    f"{percentiles.between(0, 100).all()}"
)


# ============================================================
# PRIORITY COUNTY VALIDATION
# ============================================================

print("\n" + "=" * 80)
print("7. PRIORITY COUNTY VALIDATION")
print("=" * 80)

priority = df[
    df["burden_percentile"] >= 95
]

print(
    f"Priority counties: {len(priority):,}"
)

print(
    f"Expected minimum percentile: "
    f"{priority['burden_percentile'].min():.4f}"
)

print(
    f"Highest burden score: "
    f"{priority['health_burden_score'].max():.4f}"
)


# ============================================================
# FINAL RESULT
# ============================================================

print("\n" + "=" * 80)
print("VALIDATION SUMMARY")
print("=" * 80)

checks = {
    "No missing burden scores": missing_scores == 0,
    "Z-score means approximately 0": mean_ok,
    "Z-score std approximately 1": std_ok,
    "Burden score reconstruction": scores_match,
    "All counties have 11 indicators": (
        indicator_count.min() == 11
        and indicator_count.max() == 11
    ),
    "Percentiles valid": percentiles.between(0, 100).all(),
    "Priority threshold valid": (
        priority["burden_percentile"].min() >= 95
    ),
}

for check, passed in checks.items():

    symbol = "✓" if passed else "✗"

    print(
        f"{symbol} {check}: {passed}"
    )

all_passed = all(checks.values())

print("\n" + "=" * 80)

if all_passed:
    print("ALL STATISTICAL VALIDATION CHECKS PASSED")
else:
    print("ONE OR MORE VALIDATION CHECKS FAILED")

print("=" * 80)