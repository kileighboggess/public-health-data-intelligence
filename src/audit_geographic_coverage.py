"""
Audit geographic coverage throughout the County Health Burden pipeline.

Checks:
1. Expected U.S. jurisdictions
2. States represented in each processed dataset
3. Missing jurisdictions
4. Record counts by jurisdiction
5. Geographic boundary matching
6. Duplicate county IDs
7. Missing burden scores
"""

from pathlib import Path
import json
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data" / "processed"
GEOJSON_FILE = (
    PROJECT_ROOT
    / "data"
    / "geography"
    / "us_counties.geojson"
)

EXPECTED_JURISDICTIONS = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE",
    "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS",
    "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS",
    "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY",
    "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV",
    "WI", "WY", "DC",
}


FILES_TO_AUDIT = [
    "county_health_burden.csv",
    "county_burden_classification.csv",
    "priority_counties.csv",
]


# ============================================================
# HELPERS
# ============================================================

def print_section(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def audit_file(filename):
    """Audit state coverage for a processed dataset."""

    path = DATA_DIR / filename

    print_section(f"DATASET: {filename}")

    if not path.exists():
        print(f"ERROR: File not found: {path}")
        return

    df = pd.read_csv(
        path,
        low_memory=False
    )

    print(f"Records: {len(df):,}")

    if "stateabbr" not in df.columns:
        print("stateabbr column: NOT FOUND")
        return

    states = set(
        df["stateabbr"]
        .dropna()
        .astype(str)
        .str.upper()
    )

    missing = EXPECTED_JURISDICTIONS - states
    unexpected = states - EXPECTED_JURISDICTIONS

    print(f"Jurisdictions represented: {len(states)}")
    print(
        "Missing expected jurisdictions: "
        f"{len(missing)}"
    )

    if missing:
        print(
            "Missing:",
            ", ".join(sorted(missing))
        )
    else:
        print("✓ All expected jurisdictions represented")

    if unexpected:
        print(
            "Unexpected jurisdictions:",
            ", ".join(sorted(unexpected))
        )

    print("\nRecords by jurisdiction:")

    counts = (
        df["stateabbr"]
        .dropna()
        .astype(str)
        .str.upper()
        .value_counts()
        .sort_index()
    )

    print(counts.to_string())


# ============================================================
# MAIN AUDIT
# ============================================================

print_section("PIPELINE GEOGRAPHIC COVERAGE AUDIT")

print(
    f"Expected jurisdictions: "
    f"{len(EXPECTED_JURISDICTIONS)}"
)


for filename in FILES_TO_AUDIT:
    audit_file(filename)


# ============================================================
# COUNTY BURDEN DATA QUALITY
# ============================================================

print_section("COUNTY BURDEN DATA QUALITY")

burden_path = DATA_DIR / "county_health_burden.csv"

burden_df = pd.read_csv(
    burden_path,
    low_memory=False
)

print(
    f"Total records: "
    f"{len(burden_df):,}"
)

if "locationid" in burden_df.columns:

    print(
        "Unique county IDs:",
        burden_df["locationid"].nunique()
    )

    print(
        "Duplicate county IDs:",
        burden_df["locationid"].duplicated().sum()
    )

if "health_burden_score" in burden_df.columns:

    print(
        "Missing burden scores:",
        burden_df["health_burden_score"].isna().sum()
    )

if "burden_percentile" in burden_df.columns:

    valid_percentiles = burden_df[
        burden_df["burden_percentile"].notna()
    ]

    print(
        "Valid burden percentiles:",
        valid_percentiles[
            "burden_percentile"
        ].between(0, 100).all()
    )


# ============================================================
# GEOJSON MATCHING
# ============================================================

print_section("GEOJSON COUNTY MATCHING")

if not GEOJSON_FILE.exists():

    print(
        f"ERROR: GeoJSON not found: "
        f"{GEOJSON_FILE}"
    )

else:

    with open(
        GEOJSON_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        geojson = json.load(file)

    geo_ids = {
        str(feature["id"]).zfill(5)
        for feature in geojson["features"]
    }

    analytical_ids = {
        str(int(value)).zfill(5)
        for value in burden_df[
            "locationid"
        ].dropna()
    }

    matching_ids = (
        geo_ids & analytical_ids
    )

    missing_geo = (
        analytical_ids - geo_ids
    )

    unmatched_geo = (
        geo_ids - analytical_ids
    )

    print(
        f"GeoJSON county boundaries: "
        f"{len(geo_ids):,}"
    )

    print(
        f"Analytical counties: "
        f"{len(analytical_ids):,}"
    )

    print(
        f"Matching counties: "
        f"{len(matching_ids):,}"
    )

    print(
        f"Analytical match rate: "
        f"{len(matching_ids) / len(analytical_ids) * 100:.2f}%"
    )

    print(
        f"Analytical counties without boundaries: "
        f"{len(missing_geo):,}"
    )

    print(
        f"Geographic boundaries without analytical data: "
        f"{len(unmatched_geo):,}"
    )


# ============================================================
# FINAL STATUS
# ============================================================

print_section("AUDIT COMPLETE")

print(
    "Geographic coverage audit finished successfully."
)

print(
    "Use the results above to identify where "
    "jurisdictions are being lost in the pipeline."
)
