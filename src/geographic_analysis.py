from pathlib import Path
import pandas as pd


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "places_county_clean.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

print(f"Loading processed dataset: {DATA_PATH}")

df = pd.read_csv(
    DATA_PATH,
    low_memory=False
)

print(f"Dataset loaded: {len(df):,} records")


# --------------------------------------------------
# FILTER TO AGE-ADJUSTED PREVALENCE
# --------------------------------------------------

analysis_df = df[
    df["datavaluetypeid"] == "AgeAdjPrv"
].copy()

print(
    f"Age-adjusted records retained: "
    f"{len(analysis_df):,}"
)


# --------------------------------------------------
# INDICATOR-LEVEL GEOGRAPHIC VARIABILITY
# --------------------------------------------------

indicator_summary = (
    analysis_df
    .groupby(
        [
            "measureid",
            "measure",
            "category"
        ]
    )["data_value"]
    .agg(
        observations="count",
        mean_prevalence="mean",
        median_prevalence="median",
        std_prevalence="std",
        min_prevalence="min",
        max_prevalence="max"
    )
    .reset_index()
)


# Calculate geographic range

indicator_summary["range"] = (
    indicator_summary["max_prevalence"]
    - indicator_summary["min_prevalence"]
)


# --------------------------------------------------
# ROUND VALUES
# --------------------------------------------------

numeric_columns = [
    "mean_prevalence",
    "median_prevalence",
    "std_prevalence",
    "min_prevalence",
    "max_prevalence",
    "range"
]

indicator_summary[numeric_columns] = (
    indicator_summary[numeric_columns]
    .round(2)
)


# --------------------------------------------------
# SAVE INDICATOR SUMMARY
# --------------------------------------------------

indicator_output = (
    OUTPUT_DIR
    / "indicator_geographic_summary.csv"
)

indicator_summary.to_csv(
    indicator_output,
    index=False
)


# --------------------------------------------------
# STATE-LEVEL SUMMARY
# --------------------------------------------------

state_summary = (
    analysis_df
    .groupby(
        [
            "stateabbr",
            "statedesc",
            "measureid",
            "measure",
            "category"
        ]
    )["data_value"]
    .agg(
        county_count="count",
        mean_prevalence="mean",
        median_prevalence="median",
        min_prevalence="min",
        max_prevalence="max"
    )
    .reset_index()
)


state_summary[
    [
        "mean_prevalence",
        "median_prevalence",
        "min_prevalence",
        "max_prevalence"
    ]
] = (
    state_summary[
        [
            "mean_prevalence",
            "median_prevalence",
            "min_prevalence",
            "max_prevalence"
        ]
    ].round(2)
)


# --------------------------------------------------
# SAVE STATE SUMMARY
# --------------------------------------------------

state_output = (
    OUTPUT_DIR
    / "state_indicator_summary.csv"
)

state_summary.to_csv(
    state_output,
    index=False
)


# --------------------------------------------------
# IDENTIFY HIGH-BURDEN COUNTIES
# --------------------------------------------------

high_burden_df = analysis_df.copy()


# Calculate 90th percentile within each indicator

high_burden_df["indicator_90th_percentile"] = (
    high_burden_df
    .groupby("measureid")["data_value"]
    .transform("quantile", 0.90)
)


high_burden_df["high_burden"] = (
    high_burden_df["data_value"]
    >= high_burden_df["indicator_90th_percentile"]
)


high_burden_counties = high_burden_df[
    high_burden_df["high_burden"]
].copy()


# --------------------------------------------------
# SELECT OUTPUT COLUMNS
# --------------------------------------------------

high_burden_counties = high_burden_counties[
    [
        "stateabbr",
        "statedesc",
        "locationname",
        "measureid",
        "measure",
        "category",
        "data_value",
        "indicator_90th_percentile"
    ]
].copy()


high_burden_counties[
    [
        "data_value",
        "indicator_90th_percentile"
    ]
] = (
    high_burden_counties[
        [
            "data_value",
            "indicator_90th_percentile"
        ]
    ].round(2)
)


# --------------------------------------------------
# SAVE HIGH-BURDEN COUNTIES
# --------------------------------------------------

high_burden_output = (
    OUTPUT_DIR
    / "high_burden_counties.csv"
)

high_burden_counties.to_csv(
    high_burden_output,
    index=False
)


# --------------------------------------------------
# REPORT RESULTS
# --------------------------------------------------

print()
print("=" * 60)
print("GEOGRAPHIC ANALYSIS COMPLETE")
print("=" * 60)

print()
print(
    f"Indicators analyzed: "
    f"{indicator_summary['measureid'].nunique()}"
)

print(
    f"States analyzed: "
    f"{state_summary['stateabbr'].nunique()}"
)

print(
    f"High-burden county observations: "
    f"{len(high_burden_counties):,}"
)

print()
print("Most geographically variable indicators:")
print("-" * 60)

print(
    indicator_summary
    .sort_values(
        "range",
        ascending=False
    )
    [
        [
            "measure",
            "category",
            "mean_prevalence",
            "min_prevalence",
            "max_prevalence",
            "range"
        ]
    ]
    .head(10)
    .to_string(index=False)
)

print()
print("Output files:")
print("-" * 60)
print(indicator_output)
print(state_output)
print(high_burden_output)

print("=" * 60)