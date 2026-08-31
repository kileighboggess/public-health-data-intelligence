"""
Public Health Data Intelligence
County Health Burden Visualization

Creates portfolio-ready visualizations from the
County Health Burden Index.
"""

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "county_health_burden.csv"
)

STATE_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "state_burden_summary.csv"
)

HIGH_LOW_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "high_vs_low_burden.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "visualizations"
)


# Create visualization directory if it doesn't exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

print("Loading county burden dataset:")
print(DATA_PATH)

df = pd.read_csv(DATA_PATH, low_memory=False)

print(f"Dataset loaded: {len(df):,} records")


# Keep only counties with valid burden scores
df_valid = df.dropna(
    subset=["health_burden_score"]
).copy()

print(
    f"Records with valid burden scores: "
    f"{len(df_valid):,}"
)


# ============================================================
# VISUALIZATION 1
# COUNTY BURDEN DISTRIBUTION
# ============================================================

print("\nCreating county burden distribution...")


plt.figure(figsize=(10, 6))

plt.hist(
    df_valid["health_burden_score"],
    bins=30
)

plt.axvline(
    df_valid["health_burden_score"].mean(),
    linestyle="--",
    linewidth=2,
    label="Mean burden"
)

plt.xlabel("Health Burden Score")

plt.ylabel("Number of Counties")

plt.title(
    "Distribution of County Health Burden Scores"
)

plt.legend()

plt.tight_layout()

distribution_path = (
    OUTPUT_DIR
    / "county_burden_distribution.png"
)

plt.savefig(
    distribution_path,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print(
    f"Saved: {distribution_path}"
)


# ============================================================
# VISUALIZATION 2
# TOP 20 COUNTIES
# ============================================================

print("\nCreating top 20 county visualization...")


top_counties = (
    df_valid
    .sort_values(
        "health_burden_score",
        ascending=False
    )
    .head(20)
    .copy()
)

# Create readable county labels
top_counties["county_label"] = (
    top_counties["locationname"]
    + ", "
    + top_counties["stateabbr"]
)

top_counties = top_counties.sort_values(
    "health_burden_score"
)


plt.figure(figsize=(10, 8))

plt.barh(
    top_counties["county_label"],
    top_counties["health_burden_score"]
)

plt.xlabel("Health Burden Score")

plt.ylabel("County")

plt.title(
    "Top 20 Counties by Health Burden"
)

plt.tight_layout()

top_counties_path = (
    OUTPUT_DIR
    / "top_20_counties_by_burden.png"
)

plt.savefig(
    top_counties_path,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print(
    f"Saved: {top_counties_path}"
)


# ============================================================
# VISUALIZATION 3
# STATE BURDEN RANKING
# ============================================================

print("\nCreating state burden ranking...")


state_df = pd.read_csv(
    STATE_DATA_PATH
)

state_df = (
    state_df
    .sort_values(
        "mean_burden",
        ascending=True
    )
)


plt.figure(figsize=(10, 10))

plt.barh(
    state_df["statedesc"],
    state_df["mean_burden"]
)

plt.axvline(
    0,
    linestyle="--",
    linewidth=1
)

plt.xlabel("Mean County Health Burden")

plt.ylabel("State")

plt.title(
    "Mean County Health Burden by State"
)

plt.tight_layout()

state_path = (
    OUTPUT_DIR
    / "state_burden_ranking.png"
)

plt.savefig(
    state_path,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print(
    f"Saved: {state_path}"
)


# ============================================================
# VISUALIZATION 4
# HIGH VS LOW BURDEN
# ============================================================

print(
    "\nCreating high-burden vs low-burden comparison..."
)


comparison_df = pd.read_csv(
    HIGH_LOW_DATA_PATH
)

comparison_df = (
    comparison_df
    .sort_values(
        "difference",
        ascending=True
    )
)


plt.figure(figsize=(10, 8))

plt.barh(
    comparison_df["indicator"],
    comparison_df["difference"]
)

plt.xlabel(
    "Difference in Prevalence "
    "(High-Burden − Low-Burden)"
)

plt.ylabel("Indicator")

plt.title(
    "Health Indicator Differences Between "
    "High- and Low-Burden Counties"
)

plt.tight_layout()

comparison_path = (
    OUTPUT_DIR
    / "high_vs_low_burden_indicators.png"
)

plt.savefig(
    comparison_path,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print(
    f"Saved: {comparison_path}"
)


# ============================================================
# SUMMARY
# ============================================================

print("\n")
print("=" * 55)
print("BURDEN VISUALIZATION COMPLETE")
print("=" * 55)

print(
    f"Visualizations saved to:\n"
    f"{OUTPUT_DIR}"
)

print("\nFiles created:")

print("- county_burden_distribution.png")
print("- top_20_counties_by_burden.png")
print("- state_burden_ranking.png")
print("- high_vs_low_burden_indicators.png")

print("\nVisualization pipeline finished successfully.")