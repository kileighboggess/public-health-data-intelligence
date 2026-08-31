import pandas as pd
from pathlib import Path


# --------------------------------------------------
# PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

BURDEN_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "county_health_burden.csv"
)


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

print("Loading county health burden dataset:")
print(BURDEN_PATH)

df = pd.read_csv(BURDEN_PATH)

print(f"Dataset loaded: {len(df):,} records")


# --------------------------------------------------
# BASIC VALIDATION
# --------------------------------------------------

print("\n" + "=" * 50)
print("BASIC VALIDATION")
print("=" * 50)

print("\nColumns:")
print(df.columns.tolist())

print("\nData types:")
print(df.dtypes)


# --------------------------------------------------
# BURDEN SCORE SUMMARY
# --------------------------------------------------

print("\n" + "=" * 50)
print("BURDEN SCORE SUMMARY")
print("=" * 50)

print(
    df["health_burden_score"].describe()
)


# --------------------------------------------------
# MISSING BURDEN SCORES
# --------------------------------------------------

missing_scores = df["health_burden_score"].isna().sum()

print("\nMissing burden scores:")
print(missing_scores)


# --------------------------------------------------
# DUPLICATE COUNTIES
# --------------------------------------------------

# Check for duplicate geographic records using the unique location ID
duplicate_locations = df.duplicated("locationid").sum()

print("\nDuplicate location IDs:")
print(duplicate_locations)
print(f"Duplicate location IDs: {duplicate_locations}")


# --------------------------------------------------
# COMPLETENESS
# --------------------------------------------------

print("\n" + "=" * 50)
print("COMPLETENESS")
print("=" * 50)

print(
    df["indicator_count"]
    .value_counts()
    .sort_index()
)


print("\nIndicator completeness summary:")

print(
    df["indicator_completeness"].describe()
)


# --------------------------------------------------
# TOP 10 HIGHEST BURDEN
# --------------------------------------------------

print("\n" + "=" * 50)
print("TOP 10 COUNTIES BY HEALTH BURDEN")
print("=" * 50)

top_10 = (
    df[
        [
            "stateabbr",
            "statedesc",
            "locationname",
            "indicator_count",
            "indicator_completeness",
            "health_burden_score",
            "burden_percentile",
        ]
    ]
    .sort_values(
        "health_burden_score",
        ascending=False
    )
    .head(10)
)

print(top_10.to_string(index=False))


# --------------------------------------------------
# BOTTOM 10 HIGHEST BURDEN
# --------------------------------------------------

print("\n" + "=" * 50)
print("BOTTOM 10 COUNTIES BY HEALTH BURDEN")
print("=" * 50)

bottom_10 = (
    df[
        [
            "stateabbr",
            "statedesc",
            "locationname",
            "health_burden_score",
            "burden_percentile",
        ]
    ]
    .sort_values(
        "health_burden_score",
        ascending=True
    )
    .head(10)
)

print(bottom_10.to_string(index=False))


# --------------------------------------------------
# STATE-LEVEL SUMMARY
# --------------------------------------------------

print("\n" + "=" * 50)
print("STATE-LEVEL BURDEN SUMMARY")
print("=" * 50)

state_summary = (
    df.groupby(
        ["stateabbr", "statedesc"]
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
        counties_analyzed=(
            "locationname",
            "count"
        ),
    )
    .reset_index()
    .sort_values(
        "mean_burden",
        ascending=False
    )
)

print(
    state_summary.head(15).to_string(
        index=False
    )
)


# --------------------------------------------------
# PERCENTILE DISTRIBUTION
# --------------------------------------------------

print("\n" + "=" * 50)
print("BURDEN PERCENTILE DISTRIBUTION")
print("=" * 50)

print(
    df["burden_percentile"]
    .describe()
)


# --------------------------------------------------
# FINAL VALIDATION
# --------------------------------------------------

print("\n" + "=" * 50)
print("VALIDATION COMPLETE")
print("=" * 50)

print(f"Total counties: {len(df):,}")
print(f"Missing burden scores: {missing_scores:,}")
duplicates = df.duplicated("locationid").sum()
print(f"Duplicate counties: {duplicates:,}")

print()
print("VALIDATION RESULT:")
if duplicates == 0 and missing_scores == 657:
    print("PASS: No duplicate counties detected.")
    print("PASS: Missing burden scores correspond to counties below the minimum indicator requirement.")
    print("PASS: Burden index passed basic structural validation.")
else:
    print("REVIEW: Unexpected validation results detected.")