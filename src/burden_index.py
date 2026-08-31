from pathlib import Path

import pandas as pd


# --------------------------------------------------
# PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "places_county_clean.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "county_health_burden.csv"
)


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

print(f"Loading processed dataset: {DATA_PATH}")

df = pd.read_csv(
    DATA_PATH,
    low_memory=False
)
# Keep only the latest available year
latest_year = df["year"].max()
df = df[df["year"] == latest_year].copy()

print(f"Latest year selected: {latest_year}")
print(f"Records after latest-year filter: {len(df):,}")

print(f"Dataset loaded: {len(df):,} records")


# --------------------------------------------------
# SELECT AGE-ADJUSTED RECORDS
# --------------------------------------------------

df = df[
    df["datavaluetypeid"] == "AgeAdjPrv"
].copy()

print(
    f"Age-adjusted records retained: {len(df):,}"
)


# --------------------------------------------------
# INDICATORS INCLUDED IN CORE BURDEN INDEX
# --------------------------------------------------

BURDEN_INDICATORS = [
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


# --------------------------------------------------
# INDICATORS EXCLUDED FROM CORE INDEX
# --------------------------------------------------

EXCLUDED_INDICATORS = [
    "FOODINSECU",
    "HOUSINSECU",
    "LACKTRPT",
    "SLEEP",
]

print("\nExcluded indicators from core index:")
for indicator in EXCLUDED_INDICATORS:
    print(f"  - {indicator}")

# --------------------------------------------------
# FILTER INDICATORS
# --------------------------------------------------

analysis_df = df[
    df["measureid"].isin(BURDEN_INDICATORS)
].copy()

print(
    f"Burden-index observations: "
    f"{len(analysis_df):,}"
)


# --------------------------------------------------
# CHECK INDICATOR COVERAGE
# --------------------------------------------------

print("\nIndicators included:")

print(
    analysis_df[
        [
            "measureid",
            "measure",
            "category"
        ]
    ]
    .drop_duplicates()
    .sort_values("measureid")
    .to_string(index=False)
)


# --------------------------------------------------
# CREATE WIDE COUNTY DATASET
# --------------------------------------------------

wide_df = analysis_df.pivot_table(
    index=[
        "year",
        "stateabbr",
        "statedesc",
        "locationname",
        "locationid",
        "totalpopulation"
    ],
    columns="measureid",
    values="data_value"
).reset_index()


# --------------------------------------------------
# STANDARDIZE INDICATORS
# --------------------------------------------------

for indicator in BURDEN_INDICATORS:

    if indicator not in wide_df.columns:
        print(
            f"WARNING: {indicator} "
            f"not found in dataset."
        )
        continue

    mean_value = wide_df[indicator].mean()
    std_value = wide_df[indicator].std()

    wide_df[f"{indicator}_z"] = (
        (wide_df[indicator] - mean_value)
        / std_value
    )


# --------------------------------------------------
# IDENTIFY Z-SCORE COLUMNS
# --------------------------------------------------

z_columns = [
    f"{indicator}_z"
    for indicator in BURDEN_INDICATORS
    if f"{indicator}_z" in wide_df.columns
]


print(
    f"\nZ-score indicators created: "
    f"{len(z_columns)}"
)


# --------------------------------------------------
# DATA COMPLETENESS
# --------------------------------------------------

wide_df["indicator_count"] = (
    wide_df[z_columns]
    .notna()
    .sum(axis=1)
)

wide_df["indicator_completeness"] = (
    wide_df["indicator_count"]
    / len(z_columns)
)


# --------------------------------------------------
# CALCULATE HEALTH BURDEN SCORE
# --------------------------------------------------

wide_df["health_burden_score"] = (
    wide_df[z_columns]
    .mean(axis=1)
)


# --------------------------------------------------
# APPLY COMPLETENESS THRESHOLD
# --------------------------------------------------

MIN_INDICATORS = len(BURDEN_INDICATORS)

wide_df.loc[
    wide_df["indicator_count"] < MIN_INDICATORS,
    "health_burden_score"
] = pd.NA


# --------------------------------------------------
# CALCULATE HEALTH BURDEN SCORE
# --------------------------------------------------

wide_df["health_burden_score"] = (
    wide_df[z_columns]
    .mean(axis=1)
)


# --------------------------------------------------
# APPLY COMPLETENESS THRESHOLD
# --------------------------------------------------

MIN_INDICATORS = len(BURDEN_INDICATORS)

wide_df.loc[
    wide_df["indicator_count"] < MIN_INDICATORS,
    "health_burden_score"
] = pd.NA


# --------------------------------------------------
# DATA COMPLETENESS SUMMARY
# --------------------------------------------------

print("\nData completeness by indicator count:")

print(
    wide_df["indicator_count"]
    .value_counts()
    .sort_index()
)


print("\nCompleteness summary:")

print(
    wide_df["indicator_completeness"]
    .describe()
)


print(
    f"\nMinimum indicators required: "
    f"{MIN_INDICATORS}"
)

print(
    f"Counties meeting minimum requirement: "
    f"{wide_df['health_burden_score'].notna().sum():,}"
)


# --------------------------------------------------
# RANK COUNTIES
# --------------------------------------------------

wide_df["burden_rank"] = (
    wide_df["health_burden_score"]
    .rank(
        ascending=False,
        method="min",
        na_option="keep"
    )
)


# --------------------------------------------------
# CREATE PERCENTILE
# --------------------------------------------------

wide_df["burden_percentile"] = (
    wide_df["health_burden_score"]
    .rank(
        pct=True,
        na_option="keep"
    )
    * 100
)


# --------------------------------------------------
# SORT
# --------------------------------------------------

wide_df = wide_df.sort_values(
    "health_burden_score",
    ascending=False
)


# --------------------------------------------------
# SAVE
# --------------------------------------------------

wide_df.to_csv(
    OUTPUT_PATH,
    index=False
)


# --------------------------------------------------
# FINAL SUMMARY
# --------------------------------------------------

print("\n")
print("==============================================")
print("COUNTY HEALTH BURDEN INDEX CREATED")
print("==============================================")

print(
    f"Counties analyzed: "
    f"{wide_df['locationid'].nunique():,}"
)

print(
    f"Counties with valid burden scores: "
    f"{wide_df['health_burden_score'].notna().sum():,}"
)

print(
    f"Indicators included: "
    f"{len(z_columns)}"
)

print(
    f"Output file: "
    f"{OUTPUT_PATH}"
)


# --------------------------------------------------
# TOP 20 COUNTIES
# --------------------------------------------------

print("\nTop 20 counties by health burden:")

print(
    wide_df[
        [
            "stateabbr",
            "statedesc",
            "locationname",
            "indicator_count",
            "indicator_completeness",
            "health_burden_score",
            "burden_percentile"
        ]
    ]
    .dropna(subset=["health_burden_score"])
    .head(20)
    .to_string(index=False)
)
