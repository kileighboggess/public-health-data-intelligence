from pathlib import Path
import pandas as pd


# ============================================================
# PUBLIC HEALTH BURDEN — DASHBOARD DATA MODEL
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data" / "processed"


# ============================================================
# INPUT FILES
# ============================================================

COUNTY_FILE = DATA_DIR / "county_health_burden.csv"
CLASSIFICATION_FILE = DATA_DIR / "county_burden_classification.csv"
STATE_FILE = DATA_DIR / "state_burden_dashboard.csv"
PRIORITY_FILE = DATA_DIR / "priority_county_profiles.csv"
RELATIONSHIP_FILE = DATA_DIR / "indicator_burden_relationships.csv"
COMPARISON_FILE = DATA_DIR / "priority_indicator_comparison.csv"


# ============================================================
# OUTPUT FILES
# ============================================================

DASHBOARD_COUNTY = DATA_DIR / "dashboard_county.csv"
DASHBOARD_STATE = DATA_DIR / "dashboard_state.csv"
DASHBOARD_INDICATOR = DATA_DIR / "dashboard_indicator.csv"
DASHBOARD_PRIORITY = DATA_DIR / "dashboard_priority.csv"


print("=" * 80)
print("PUBLIC HEALTH BURDEN — DASHBOARD DATA MODEL")
print("=" * 80)


# ============================================================
# LOAD DATA
# ============================================================

print("\nLoading source tables...")

county = pd.read_csv(COUNTY_FILE, low_memory=False)
classification = pd.read_csv(CLASSIFICATION_FILE, low_memory=False)
state = pd.read_csv(STATE_FILE, low_memory=False)
priority = pd.read_csv(PRIORITY_FILE, low_memory=False)
relationships = pd.read_csv(RELATIONSHIP_FILE, low_memory=False)
comparison = pd.read_csv(COMPARISON_FILE, low_memory=False)

print(f"County records:       {len(county):,}")
print(f"Classification rows:  {len(classification):,}")
print(f"State records:        {len(state):,}")
print(f"Priority counties:    {len(priority):,}")
print(f"Indicators:           {len(relationships):,}")


# ============================================================
# 1. COUNTY DASHBOARD TABLE
# ============================================================

print("\nCreating county dashboard table...")

county_dashboard = county.merge(
    classification[
        [
            "locationid",
            "burden_category",
            "high_burden_flag",
            "very_high_burden_flag",
            "priority_flag",
        ]
    ],
    on="locationid",
    how="left",
    validate="one_to_one",
)

county_dashboard = county_dashboard.sort_values(
    ["stateabbr", "health_burden_score"],
    ascending=[True, False]
).reset_index(drop=True)


# ============================================================
# 2. STATE DASHBOARD TABLE
# ============================================================

print("Creating state dashboard table...")

state_dashboard = state.copy()

state_dashboard = state_dashboard.sort_values(
    "state_burden_rank"
).reset_index(drop=True)


# ============================================================
# 3. INDICATOR DASHBOARD TABLE
# ============================================================

print("Creating indicator dashboard table...")

indicator_dashboard = relationships.merge(
    comparison,
    on="indicator",
    how="left",
    validate="one_to_one",
)

indicator_dashboard = indicator_dashboard.sort_values(
    "correlation_with_burden",
    ascending=False
).reset_index(drop=True)


# ============================================================
# 4. PRIORITY COUNTY TABLE
# ============================================================

print("Creating priority county dashboard table...")

priority_dashboard = priority.copy()

priority_dashboard = priority_dashboard.sort_values(
    "burden_percentile",
    ascending=False
).reset_index(drop=True)


# ============================================================
# SAVE TABLES
# ============================================================

print("\nSaving dashboard tables...")

county_dashboard.to_csv(
    DASHBOARD_COUNTY,
    index=False
)

state_dashboard.to_csv(
    DASHBOARD_STATE,
    index=False
)

indicator_dashboard.to_csv(
    DASHBOARD_INDICATOR,
    index=False
)

priority_dashboard.to_csv(
    DASHBOARD_PRIORITY,
    index=False
)


# ============================================================
# QUALITY CHECKS
# ============================================================

print("\n" + "=" * 80)
print("QUALITY CHECKS")
print("=" * 80)

assert len(county_dashboard) == len(county)

assert county_dashboard["locationid"].nunique() == len(
    county_dashboard
)

assert county_dashboard["health_burden_score"].notna().all()

assert county_dashboard["burden_percentile"].between(
    0, 100
).all()

assert len(state_dashboard) == state["stateabbr"].nunique()

assert len(indicator_dashboard) == len(relationships)

assert len(priority_dashboard) == len(priority)

assert priority_dashboard["locationid"].nunique() == len(
    priority_dashboard
)

print("✓ County row count validated")
print("✓ County IDs unique")
print("✓ Burden scores complete")
print("✓ Burden percentiles valid")
print("✓ State table validated")
print("✓ Indicator table validated")
print("✓ Priority county table validated")


# ============================================================
# EXECUTIVE SUMMARY
# ============================================================

print("\n" + "=" * 80)
print("DASHBOARD DATA MODEL SUMMARY")
print("=" * 80)

print(f"""
County records:              {len(county_dashboard):,}
State records:               {len(state_dashboard):,}
Priority counties:           {len(priority_dashboard):,}
Indicators analyzed:         {len(indicator_dashboard):,}

Highest burden county:
    {county_dashboard.loc[
        county_dashboard["health_burden_score"].idxmax(),
        "locationname"
    ]}

Highest burden state:
    {state_dashboard.iloc[0]["statedesc"]}

Top indicator by burden relationship:
    {indicator_dashboard.iloc[0]["indicator"]}
""")


print("=" * 80)
print("DASHBOARD DATA MODEL COMPLETE")
print("=" * 80)