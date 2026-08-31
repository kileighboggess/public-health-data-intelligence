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

print("=" * 80)
print("PUBLIC HEALTH BURDEN — INDICATOR RELATIONSHIP ANALYSIS")
print("=" * 80)

print(f"\nLoading dataset:")
print(DATA_PATH)

df = pd.read_csv(
    DATA_PATH,
    low_memory=False
)

print(f"Counties loaded: {len(df):,}")


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


# ============================================================
# VALID RECORDS
# ============================================================

analysis_df = df[
    df["health_burden_score"].notna()
].copy()

print(
    f"Valid burden records: "
    f"{len(analysis_df):,}"
)


# ============================================================
# 1. INDICATOR → BURDEN CORRELATION
# ============================================================

print("\n")
print("=" * 80)
print("1. INDICATOR–BURDEN RELATIONSHIPS")
print("=" * 80)

relationship_results = []

for indicator in INDICATORS:

    z_column = f"{indicator}_z"

    if z_column not in analysis_df.columns:
        print(
            f"WARNING: {z_column} not found."
        )
        continue

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


print(
    relationship_df.to_string(
        index=False
    )
)


# ============================================================
# SAVE RELATIONSHIP RESULTS
# ============================================================

relationship_output = (
    OUTPUT_DIR
    / "indicator_burden_relationships.csv"
)

relationship_df.to_csv(
    relationship_output,
    index=False
)

print(
    f"\nSaved:"
    f"\n{relationship_output}"
)


# ============================================================
# 2. INDICATOR CORRELATION MATRIX
# ============================================================

print("\n")
print("=" * 80)
print("2. INDICATOR CORRELATION MATRIX")
print("=" * 80)

z_columns = [
    f"{indicator}_z"
    for indicator in INDICATORS
    if f"{indicator}_z" in analysis_df.columns
]

indicator_corr = analysis_df[
    z_columns
].corr()

print(
    indicator_corr.round(3).to_string()
)


# ============================================================
# SAVE CORRELATION MATRIX
# ============================================================

corr_output = (
    OUTPUT_DIR
    / "indicator_correlation_matrix.csv"
)

indicator_corr.to_csv(
    corr_output
)

print(
    f"\nSaved:"
    f"\n{corr_output}"
)


# ============================================================
# 3. HIGHEST INDICATOR CORRELATIONS
# ============================================================

print("\n")
print("=" * 80)
print("3. STRONGEST INDICATOR-TO-INDICATOR RELATIONSHIPS")
print("=" * 80)

pairs = []

for i in range(len(z_columns)):

    for j in range(i + 1, len(z_columns)):

        indicator_1 = z_columns[i].replace(
            "_z",
            ""
        )

        indicator_2 = z_columns[j].replace(
            "_z",
            ""
        )

        correlation = indicator_corr.iloc[
            i,
            j
        ]

        pairs.append(
            {
                "indicator_1": indicator_1,
                "indicator_2": indicator_2,
                "correlation": correlation,
                "absolute_correlation": abs(
                    correlation
                ),
            }
        )


pairs_df = pd.DataFrame(
    pairs
).sort_values(
    "absolute_correlation",
    ascending=False
)


print(
    pairs_df.head(20).to_string(
        index=False
    )
)


# ============================================================
# SAVE STRONGEST RELATIONSHIPS
# ============================================================

pairs_output = (
    OUTPUT_DIR
    / "indicator_pair_correlations.csv"
)

pairs_df.to_csv(
    pairs_output,
    index=False
)

print(
    f"\nSaved:"
    f"\n{pairs_output}"
)


# ============================================================
# 4. TOP AND BOTTOM BURDEN COUNTIES
# ============================================================

print("\n")
print("=" * 80)
print("4. EXTREME BURDEN COUNTIES")
print("=" * 80)

county_columns = [
    "stateabbr",
    "statedesc",
    "locationname",
    "locationid",
    "health_burden_score",
    "burden_percentile",
]


print("\nTOP 10 HIGHEST-BURDEN COUNTIES")

print(
    analysis_df[
        county_columns
    ]
    .sort_values(
        "health_burden_score",
        ascending=False
    )
    .head(10)
    .to_string(index=False)
)


print("\nTOP 10 LOWEST-BURDEN COUNTIES")

print(
    analysis_df[
        county_columns
    ]
    .sort_values(
        "health_burden_score",
        ascending=True
    )
    .head(10)
    .to_string(index=False)
)


# ============================================================
# 5. INDICATOR VALUES IN PRIORITY COUNTIES
# ============================================================

print("\n")
print("=" * 80)
print("5. INDICATOR PROFILES OF PRIORITY COUNTIES")
print("=" * 80)

priority_df = analysis_df[
    analysis_df["burden_percentile"] >= 95
].copy()

print(
    f"Priority counties analyzed: "
    f"{len(priority_df):,}"
)


priority_means = (
    priority_df[
        INDICATORS
    ]
    .mean()
)

overall_means = (
    analysis_df[
        INDICATORS
    ]
    .mean()
)

priority_comparison = pd.DataFrame(
    {
        "indicator": INDICATORS,
        "priority_county_mean": [
            priority_means[i]
            for i in INDICATORS
        ],
        "overall_mean": [
            overall_means[i]
            for i in INDICATORS
        ],
    }
)

priority_comparison[
    "difference"
] = (
    priority_comparison[
        "priority_county_mean"
    ]
    -
    priority_comparison[
        "overall_mean"
    ]
)

priority_comparison[
    "percent_difference"
] = (
    priority_comparison["difference"]
    /
    priority_comparison["overall_mean"]
    * 100
)

priority_comparison = (
    priority_comparison
    .sort_values(
        "percent_difference",
        ascending=False
    )
)


print(
    priority_comparison.round(3).to_string(
        index=False
    )
)


# ============================================================
# SAVE PRIORITY COMPARISON
# ============================================================

priority_output = (
    OUTPUT_DIR
    / "priority_indicator_comparison.csv"
)

priority_comparison.to_csv(
    priority_output,
    index=False
)

print(
    f"\nSaved:"
    f"\n{priority_output}"
)


# ============================================================
# COMPLETE
# ============================================================

print("\n")
print("=" * 80)
print("INDICATOR ANALYSIS COMPLETE")
print("=" * 80)

print("\nOutput files created:")

print(
    "- indicator_burden_relationships.csv"
)

print(
    "- indicator_correlation_matrix.csv"
)

print(
    "- indicator_pair_correlations.csv"
)

print(
    "- priority_indicator_comparison.csv"
)