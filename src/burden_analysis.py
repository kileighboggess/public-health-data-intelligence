"""
County Health Burden Analysis

Analyzes the validated County Health Burden Index to identify:
1. Indicators most associated with overall burden
2. States with the highest burden
3. Differences between high- and low-burden counties
4. Potential priority counties

Input:
    data/processed/county_health_burden.csv

Outputs:
    data/processed/indicator_burden_relationship.csv
    data/processed/state_burden_summary.csv
    data/processed/high_vs_low_burden.csv
    data/processed/priority_counties.csv
"""

from pathlib import Path

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

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 60)
print("COUNTY HEALTH BURDEN ANALYSIS")
print("=" * 60)

print(f"\nLoading dataset:")
print(DATA_PATH)

df = pd.read_csv(DATA_PATH, low_memory=False)

print(f"Dataset loaded: {len(df):,} records")


# ============================================================
# FILTER TO VALID BURDEN SCORES
# ============================================================

analysis_df = df[
    df["health_burden_score"].notna()
].copy()

print(
    f"Records with valid burden scores: "
    f"{len(analysis_df):,}"
)


# ============================================================
# INDICATORS
# ============================================================

indicator_columns = [
    "ACCESS2",
    "BPHIGH",
    "COPD",
    "CSMOKING",
    "DEPRESSION",
    "DIABETES",
    "FOODINSECU",
    "GHLTH",
    "HOUSINSECU",
    "LACKTRPT",
    "LPA",
    "MHLTH",
    "OBESITY",
    "STROKE",
]

z_columns = [
    f"{indicator}_z"
    for indicator in indicator_columns
    if f"{indicator}_z" in analysis_df.columns
]

print(f"Indicators available: {len(z_columns)}")


# ============================================================
# 1. INDICATOR RELATIONSHIP WITH BURDEN
# ============================================================

print("\n" + "=" * 60)
print("INDICATOR RELATIONSHIP WITH HEALTH BURDEN")
print("=" * 60)

relationship_results = []

for z_column in z_columns:

    indicator = z_column.replace("_z", "")

    valid = analysis_df[
        [z_column, "health_burden_score"]
    ].dropna()

    correlation = valid[
        z_column
    ].corr(
        valid["health_burden_score"]
    )

    relationship_results.append(
        {
            "indicator": indicator,
            "correlation_with_burden": correlation,
            "observations": len(valid),
        }
    )


relationship_df = pd.DataFrame(
    relationship_results
).sort_values(
    "correlation_with_burden",
    ascending=False
)


print("\nIndicators most positively associated with burden:")

print(
    relationship_df.head(10).to_string(
        index=False
    )
)


# ============================================================
# SAVE INDICATOR RELATIONSHIPS
# ============================================================

relationship_path = (
    OUTPUT_DIR
    / "indicator_burden_relationship.csv"
)

relationship_df.to_csv(
    relationship_path,
    index=False
)

print(
    f"\nSaved indicator analysis:"
    f"\n{relationship_path}"
)


# ============================================================
# 2. STATE-LEVEL BURDEN ANALYSIS
# ============================================================

print("\n" + "=" * 60)
print("STATE-LEVEL BURDEN ANALYSIS")
print("=" * 60)


state_summary = (
    analysis_df
    .groupby(
        ["stateabbr", "statedesc"],
        as_index=False
    )
    .agg(
        mean_burden=(
            "health_burden_score",
            "mean"
        ),
        median_burden=(
            "health_burden_score",
            "median"
        ),
        max_burden=(
            "health_burden_score",
            "max"
        ),
        counties_analyzed=(
            "locationid",
            "nunique"
        ),
    )
    .sort_values(
        "mean_burden",
        ascending=False
    )
)


print("\nStates ranked by mean county burden:")

print(
    state_summary.head(15).to_string(
        index=False
    )
)


# ============================================================
# SAVE STATE SUMMARY
# ============================================================

state_path = (
    OUTPUT_DIR
    / "state_burden_summary.csv"
)

state_summary.to_csv(
    state_path,
    index=False
)

print(
    f"\nSaved state-level analysis:"
    f"\n{state_path}"
)


# ============================================================
# 3. HIGH VS LOW BURDEN COUNTIES
# ============================================================

print("\n" + "=" * 60)
print("HIGH VS LOW BURDEN COUNTY ANALYSIS")
print("=" * 60)


high_threshold = (
    analysis_df[
        "burden_percentile"
    ].quantile(0.90)
)

low_threshold = (
    analysis_df[
        "burden_percentile"
    ].quantile(0.10)
)


high_burden = analysis_df[
    analysis_df["burden_percentile"]
    >= high_threshold
].copy()

low_burden = analysis_df[
    analysis_df["burden_percentile"]
    <= low_threshold
].copy()


print(
    f"\nHigh-burden counties: "
    f"{len(high_burden):,}"
)

print(
    f"Low-burden counties: "
    f"{len(low_burden):,}"
)


comparison_results = []

for indicator in indicator_columns:

    if indicator not in analysis_df.columns:
        continue

    high_mean = high_burden[
        indicator
    ].mean()

    low_mean = low_burden[
        indicator
    ].mean()

    difference = (
        high_mean - low_mean
    )

    comparison_results.append(
        {
            "indicator": indicator,
            "high_burden_mean": high_mean,
            "low_burden_mean": low_mean,
            "difference": difference,
        }
    )


comparison_df = pd.DataFrame(
    comparison_results
).sort_values(
    "difference",
    ascending=False
)


print(
    "\nLargest differences between "
    "high- and low-burden counties:"
)

print(
    comparison_df.head(15).to_string(
        index=False
    )
)


# ============================================================
# SAVE HIGH VS LOW ANALYSIS
# ============================================================

comparison_path = (
    OUTPUT_DIR
    / "high_vs_low_burden.csv"
)

comparison_df.to_csv(
    comparison_path,
    index=False
)

print(
    f"\nSaved high vs low analysis:"
    f"\n{comparison_path}"
)


# ============================================================
# 4. PRIORITY COUNTIES
# ============================================================

print("\n" + "=" * 60)
print("PRIORITY COUNTY ANALYSIS")
print("=" * 60)


priority_counties = (
    analysis_df[
        analysis_df["burden_percentile"]
        >= 95
    ]
    .copy()
    .sort_values(
        "health_burden_score",
        ascending=False
    )
)


priority_columns = [
    "stateabbr",
    "statedesc",
    "locationname",
    "locationid",
    "totalpopulation",
    "indicator_count",
    "indicator_completeness",
    "health_burden_score",
    "burden_percentile",
]


priority_counties = priority_counties[
    priority_columns
]


print(
    f"\nPriority counties identified: "
    f"{len(priority_counties):,}"
)

print(
    "\nTop 20 priority counties:"
)

print(
    priority_counties.head(20).to_string(
        index=False
    )
)


# ============================================================
# SAVE PRIORITY COUNTIES
# ============================================================

priority_path = (
    OUTPUT_DIR
    / "priority_counties.csv"
)

priority_counties.to_csv(
    priority_path,
    index=False
)

print(
    f"\nSaved priority county analysis:"
    f"\n{priority_path}"
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("BURDEN ANALYSIS COMPLETE")
print("=" * 60)

print(
    f"\nValid counties analyzed: "
    f"{len(analysis_df):,}"
)

print(
    f"Indicators analyzed: "
    f"{len(indicator_columns)}"
)

print(
    f"High-burden counties: "
    f"{len(high_burden):,}"
)

print(
    f"Low-burden counties: "
    f"{len(low_burden):,}"
)

print(
    f"Priority counties: "
    f"{len(priority_counties):,}"
)

print("\nOutput files created:")

print(
    "- indicator_burden_relationship.csv"
)

print(
    "- state_burden_summary.csv"
)

print(
    "- high_vs_low_burden.csv"
)

print(
    "- priority_counties.csv"
)

print("\nAnalysis finished successfully.")