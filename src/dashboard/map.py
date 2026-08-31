import json
from pathlib import Path

import pandas as pd
import plotly.express as px


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

GEOJSON_PATH = (
    PROJECT_ROOT
    / "data"
    / "geography"
    / "us_counties.geojson"
)


# --------------------------------------------------
# LOAD GEOJSON
# --------------------------------------------------

def load_county_geojson():
    """
    Load and normalize U.S. county GeoJSON boundaries.
    """

    with open(GEOJSON_PATH, "r") as f:
        geojson = json.load(f)

    for feature in geojson["features"]:
        feature["id"] = str(feature["id"]).zfill(5)

    return geojson


# --------------------------------------------------
# PREPARE COUNTY DATA
# --------------------------------------------------

def prepare_county_map_data(county_df):
    """
    Prepare county-level burden data for geographic mapping.
    """

    map_df = county_df.copy()

    map_df["fips"] = (
        map_df["locationid"]
        .astype(int)
        .astype(str)
        .str.zfill(5)
    )

    map_df["county_label"] = (
        map_df["locationname"]
        + ", "
        + map_df["statedesc"]
    )

    map_df["population_display"] = (
        map_df["totalpopulation"]
        .map(lambda x: f"{x:,.0f}")
    )

    map_df["score_display"] = (
        map_df["health_burden_score"]
        .map(lambda x: f"{x:.3f}")
    )

    map_df["percentile_display"] = (
        map_df["burden_percentile"]
        .map(lambda x: f"{x:.1f}%")
    )

    return map_df


# --------------------------------------------------
# VALIDATE GEOGRAPHIC COVERAGE
# --------------------------------------------------

def validate_map_data(county_df, geojson):
    """
    Validate that county data and geographic boundaries
    can be joined using FIPS IDs.
    """

    geojson_ids = {
        str(feature["id"]).zfill(5)
        for feature in geojson["features"]
    }

    dashboard_ids = set(
        county_df["fips"]
    )

    matching_ids = geojson_ids & dashboard_ids

    match_rate = (
        len(matching_ids)
        / len(dashboard_ids)
        * 100
    )

    print("\nGeographic validation:")
    print(
        f"GeoJSON counties: "
        f"{len(geojson_ids):,}"
    )
    print(
        f"Dashboard counties: "
        f"{len(dashboard_ids):,}"
    )
    print(
        f"Matching FIPS IDs: "
        f"{len(matching_ids):,}"
    )
    print(
        f"Dashboard match rate: "
        f"{match_rate:.2f}%"
    )

    if len(matching_ids) == 0:
        raise ValueError(
            "No matching county FIPS IDs found."
        )

    return match_rate


# --------------------------------------------------
# CREATE BURDEN MAP
# --------------------------------------------------

def create_burden_map(county_df):
    """
    Create an interactive county-level health burden map.
    """

    geojson = load_county_geojson()

    map_df = prepare_county_map_data(
        county_df
    )

    validate_map_data(
        map_df,
        geojson
    )

    fig = px.choropleth(
        map_df,
        geojson=geojson,
        locations="fips",
        color="health_burden_score",
        color_continuous_scale="RdYlGn_r",
        scope="usa",
        hover_name="county_label",
        hover_data={
            "fips": False,
            "health_burden_score": False,
            "score_display": True,
            "percentile_display": True,
            "burden_category": True,
            "population_display": True,
            "priority_flag": True,
        },
        labels={
            "score_display": "Burden Score",
            "percentile_display": "Burden Percentile",
            "burden_category": "Category",
            "population_display": "Population",
            "priority_flag": "Priority County",
        },
        featureidkey="id",
        title="County Health Burden — 2023",
    )

    fig.update_geos(
        fitbounds="locations",
        visible=False,
    )

    fig.update_layout(
        template="plotly_white",
        height=700,
        margin={
            "l": 10,
            "r": 10,
            "t": 60,
            "b": 10,
        },
        coloraxis_colorbar=dict(
            title="Health<br>Burden"
        ),
    )

    return fig


# --------------------------------------------------
# MODULE TEST
# --------------------------------------------------

if __name__ == "__main__":

    print("=" * 70)
    print("PUBLIC HEALTH BURDEN — COUNTY MAP TEST")
    print("=" * 70)

    data_path = (
        PROJECT_ROOT
        / "data"
        / "processed"
        / "dashboard_county.csv"
    )

    county_data = pd.read_csv(
        data_path,
        low_memory=False
    )

    print(
        f"\nCounty records loaded: "
        f"{len(county_data):,}"
    )

    figure = create_burden_map(
        county_data
    )

    print("\n✓ County burden map created successfully")
    print(
        f"Map traces: {len(figure.data)}"
    )
    print(
        f"Map height: "
        f"{figure.layout.height}px"
    )

    print("\n✓ Geographic visualization test passed")
    print("=" * 70)
