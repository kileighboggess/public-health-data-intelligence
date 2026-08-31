"""
Create dashboard-ready datasets for the County Health Burden Index.

This script:
1. Classifies counties into relative burden categories.
2. Creates a state-level burden dashboard dataset.
3. Creates priority county profiles.
4. Performs automated quality checks.
5. Prints an executive-level summary.

Burden categories are percentile-based and are intended for
relative comparison across counties, not clinical risk classification.
"""

from pathlib import Path

import pandas as pd
import numpy as np


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "county_health_burden.csv"
)

INDICATOR_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "indicator_burden_relationship.csv"
)

PRIORITY_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "priority_counties.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"

COUNTY_OUTPUT = OUTPUT_DIR / "county_burden_classification.csv"
STATE_OUTPUT = OUTPUT_DIR / "state_burden_dashboard.csv"
PRIORITY_OUTPUT = OUTPUT_DIR / "priority_county_profiles.csv"


INDICATORS = [
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


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def classify_burden(percentile):
    """
    Classify counties based on burden percentile.

    These categories are relative to the analytical population
    and are NOT clinical risk categories.
    """

    if pd.isna(percentile):
        return np.nan

    if percentile <= 20:
        return "Very Low"
    elif percentile <= 40:
        return "Low"
    elif percentile <= 60:
        return "Moderate"
    elif percentile <= 80:
        return "High"
    else:
        return "Very High"


def calculate_top_indicators(row, n=3):
    """
    Return the top n standardized indicators for a county.

    Higher z-scores represent greater relative burden.
    """

    values = {}

    for indicator in INDICATORS:
        z_column = f"{indicator}_z"

        if z_column in row.index and pd.notna(row[z_column]):
            values[indicator] = row[z_column]

    sorted_indicators = sorted(
        values.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return [indicator for indicator, _ in sorted_indicators[:n]]


def safe_percentage(numerator, denominator):
    """Calculate percentage while protecting against division by zero."""

    if denominator == 0:
        return 0.0

    return (numerator / denominator) * 100


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 60)
print("CREATING BURDEN DASHBOARD DATA")
print("=" * 60)

print(f"\nLoading county burden dataset:")
print(INPUT_FILE)

df = pd.read_csv(INPUT_FILE, low_memory=False)

print(f"Dataset loaded: {len(df):,} records")


# ============================================================
# FILTER VALID BURDEN SCORES
# ============================================================

valid = df[df["health_burden_score"].notna()].copy()

print(f"Records with valid burden scores: {len(valid):,}")

if valid.empty:
    raise ValueError("No valid burden scores found.")


# ============================================================
# COUNTY BURDEN CLASSIFICATION
# ============================================================

print("\n" + "=" * 60)
print("COUNTY BURDEN CLASSIFICATION")
print("=" * 60)

valid["burden_category"] = valid["burden_percentile"].apply(
    classify_burden
)

valid["high_burden_flag"] = (
    valid["burden_category"].isin(["High", "Very High"])
)

valid["very_high_burden_flag"] = (
    valid["burden_category"] == "Very High"
)

valid["priority_flag"] = False


# ============================================================
# PRIORITY COUNTY MATCHING
# ============================================================

if PRIORITY_FILE.exists():

    priority_df = pd.read_csv(
        PRIORITY_FILE,
        low_memory=False
    )

    if "locationid" in priority_df.columns:

        priority_ids = set(
            priority_df["locationid"]
            .dropna()
            .astype(int)
        )

        valid["priority_flag"] = (
            valid["locationid"]
            .astype(int)
            .isin(priority_ids)
        )

        print(
            f"Priority counties matched: "
            f"{valid['priority_flag'].sum():,}"
        )

else:

    print(
        "WARNING: priority_counties.csv not found. "
        "Priority flags will remain False."
    )


# ============================================================
# COUNTY OUTPUT
# ============================================================

county_columns = [
    "year",
    "stateabbr",
    "statedesc",
    "locationname",
    "locationid",
    "totalpopulation",
    "indicator_count",
    "indicator_completeness",
    "health_burden_score",
    "burden_rank",
    "burden_percentile",
    "burden_category",
    "high_burden_flag",
    "very_high_burden_flag",
    "priority_flag",
]

county_output = valid[county_columns].copy()

county_output = county_output.sort_values(
    "health_burden_score",
    ascending=False
)

county_output.to_csv(
    COUNTY_OUTPUT,
    index=False
)

print(f"\nSaved county classification:")
print(COUNTY_OUTPUT)


# ============================================================
# STATE-LEVEL DASHBOARD DATA
# ============================================================

print("\n" + "=" * 60)
print("CREATING STATE-LEVEL DASHBOARD DATA")
print("=" * 60)


state_records = []

for (stateabbr, statedesc), group in valid.groupby(
    ["stateabbr", "statedesc"]
):

        total_counties = len(group)

        category_counts = (
        group["burden_category"]
        .value_counts()
    )

    # Count burden categories directly.
    # Categories are mutually exclusive, so these counts
    # cannot double-count counties.
        very_low_count = category_counts.get("Very Low", 0)
        low_count = category_counts.get("Low", 0)
        moderate_count = category_counts.get("Moderate", 0)
        high_count = category_counts.get("High", 0)
        very_high_count = category_counts.get("Very High", 0)

        high_or_very_high_count = (
        high_count + very_high_count
    )

        priority_count = (
        group["priority_flag"]
        .sum()
    )

    # Internal consistency checks
        category_total = (
        very_low_count
        + low_count
        + moderate_count
        + high_count
        + very_high_count
    )

        assert category_total == total_counties, (
        f"Category count mismatch for {stateabbr}: "
        f"{category_total} categories vs "
        f"{total_counties} counties"
    )

        assert high_or_very_high_count <= total_counties, (
        f"High-burden count exceeds total counties for "
        f"{stateabbr}"
    )

        state_records.append(
        {
            "stateabbr": stateabbr,
            "statedesc": statedesc,
            "counties_analyzed": total_counties,
            "mean_burden": group["health_burden_score"].mean(),
            "median_burden": group["health_burden_score"].median(),
            "max_burden": group["health_burden_score"].max(),
            "min_burden": group["health_burden_score"].min(),
            "mean_percentile": group["burden_percentile"].mean(),
                        "very_low_count": int(very_low_count),
            "low_count": int(low_count),
            "moderate_count": int(moderate_count),
            "high_count": int(high_count),
            "very_high_count": int(very_high_count),
            "high_burden_count": int(high_count),
            "very_high_burden_count": int(very_high_count),
            "high_or_very_high_count": int(
                high_or_very_high_count
            ),
            "high_or_very_high_pct": safe_percentage(
                high_or_very_high_count,
                total_counties
            ),
        }
    )


state_output = pd.DataFrame(state_records)

state_output = state_output.sort_values(
    "mean_burden",
    ascending=False
)

state_output["state_burden_rank"] = (
    state_output["mean_burden"]
    .rank(
        ascending=False,
        method="min"
    )
    .astype(int)
)

state_output.to_csv(
    STATE_OUTPUT,
    index=False
)

print(f"Saved state dashboard dataset:")
print(STATE_OUTPUT)


# ============================================================
# PRIORITY COUNTY PROFILES
# ============================================================

print("\n" + "=" * 60)
print("CREATING PRIORITY COUNTY PROFILES")
print("=" * 60)

priority = valid[
    valid["priority_flag"]
].copy()

profile_records = []

for _, row in priority.iterrows():

    top_indicators = calculate_top_indicators(
        row,
        n=3
    )

    profile_records.append(
        {
            "stateabbr": row["stateabbr"],
            "statedesc": row["statedesc"],
            "locationname": row["locationname"],
            "locationid": row["locationid"],
            "totalpopulation": row["totalpopulation"],
            "health_burden_score": row[
                "health_burden_score"
            ],
            "burden_percentile": row[
                "burden_percentile"
            ],
            "burden_category": row[
                "burden_category"
            ],
            "indicator_count": row[
                "indicator_count"
            ],
            "indicator_completeness": row[
                "indicator_completeness"
            ],
            "top_indicator_1": (
                top_indicators[0]
                if len(top_indicators) > 0
                else np.nan
            ),
            "top_indicator_2": (
                top_indicators[1]
                if len(top_indicators) > 1
                else np.nan
            ),
            "top_indicator_3": (
                top_indicators[2]
                if len(top_indicators) > 2
                else np.nan
            ),
        }
    )


priority_output = pd.DataFrame(
    profile_records
)

priority_output = priority_output.sort_values(
    "health_burden_score",
    ascending=False
)

priority_output.to_csv(
    PRIORITY_OUTPUT,
    index=False
)

print(f"Saved priority county profiles:")
print(PRIORITY_OUTPUT)


# ============================================================
# QUALITY CHECKS
# ============================================================

print("\n" + "=" * 60)
print("QUALITY CHECKS")
print("=" * 60)


# County count
assert len(county_output) == len(valid), (
    "County output record count does not match "
    "valid burden records."
)

# Location IDs should be unique
assert county_output["locationid"].is_unique, (
    "Duplicate location IDs detected."
)

# Burden scores should not be missing
assert county_output["health_burden_score"].notna().all(), (
    "Missing burden scores detected."
)

# Percentiles should be between 0 and 100
assert (
    county_output["burden_percentile"]
    .between(0, 100)
    .all()
), "Invalid burden percentiles detected."

# Categories should be valid
valid_categories = {
    "Very Low",
    "Low",
    "Moderate",
    "High",
    "Very High",
}

assert set(
    county_output["burden_category"].dropna().unique()
).issubset(valid_categories), (
    "Unexpected burden category detected."
)

# State output should have unique states
assert state_output["stateabbr"].is_unique, (
    "Duplicate states detected."
)

# Priority IDs should be unique
if not priority_output.empty:
    assert priority_output["locationid"].is_unique, (
        "Duplicate priority county IDs detected."
    )


print("✓ County record count validated")
print("✓ County FIPS/location IDs are unique")
print("✓ No missing valid burden scores")
print("✓ Burden percentiles are within 0–100")
print("✓ Burden categories are valid")
print("✓ State records are unique")
print("✓ Priority county IDs are unique")


# ============================================================
# EXECUTIVE SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("EXECUTIVE SUMMARY")
print("=" * 60)

category_summary = (
    county_output["burden_category"]
    .value_counts()
    .reindex(
        [
            "Very Low",
            "Low",
            "Moderate",
            "High",
            "Very High",
        ],
        fill_value=0
    )
)

print("\nCounty burden distribution:")

for category, count in category_summary.items():

    percentage = safe_percentage(
        count,
        len(county_output)
    )

    print(
        f"{category:12s}: "
        f"{count:4,} counties "
        f"({percentage:5.1f}%)"
    )


print("\nHighest-burden states:")

print(
    state_output[
        [
            "stateabbr",
            "statedesc",
            "mean_burden",
            "high_or_very_high_pct",
        ]
    ]
    .head(10)
    .to_string(index=False)
)


print("\nPriority counties:")
print(
    f"{len(priority_output):,}"
)

print("\nHighest-priority county:")

if not priority_output.empty:

    top_priority = priority_output.iloc[0]

    print(
        f"{top_priority['locationname']}, "
        f"{top_priority['statedesc']}"
    )

    print(
        f"Burden score: "
        f"{top_priority['health_burden_score']:.3f}"
    )

    print(
        f"Percentile: "
        f"{top_priority['burden_percentile']:.2f}"
    )

    print(
        "Top indicators: "
        f"{top_priority['top_indicator_1']}, "
        f"{top_priority['top_indicator_2']}, "
        f"{top_priority['top_indicator_3']}"
    )


# ============================================================
# FINAL OUTPUT
# ============================================================

print("\n" + "=" * 60)
print("DASHBOARD DATA PIPELINE COMPLETE")
print("=" * 60)

print("\nOutput files created:")

print(f"- {COUNTY_OUTPUT.name}")
print(f"- {STATE_OUTPUT.name}")
print(f"- {PRIORITY_OUTPUT.name}")

print(
    "\nThese datasets are ready for "
    "dashboard development and portfolio visualization."
)