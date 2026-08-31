import json
from pathlib import Path

import pandas as pd
import plotly.express as px


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = PROJECT_ROOT / "data" / "processed" / "county_health_burden.csv"
GEOJSON_PATH = PROJECT_ROOT / "data" / "geography" / "us_counties.geojson"
OUTPUT_PATH = PROJECT_ROOT / "data" / "visualizations" / "county_map_test.html"


print("Loading data...")

df = pd.read_csv(DATA_PATH, low_memory=False)

df = df[df["health_burden_score"].notna()].copy()

df["fips"] = (
    df["locationid"]
    .astype(int)
    .astype(str)
    .str.zfill(5)
)

print(f"County records: {len(df):,}")


print("Loading GeoJSON...")

with open(GEOJSON_PATH, "r") as f:
    geojson = json.load(f)

print(f"GeoJSON counties: {len(geojson['features']):,}")


# Make absolutely sure every GeoJSON ID is a string
for feature in geojson["features"]:
    feature["id"] = str(feature["id"]).zfill(5)


# Test matching
geo_ids = {feature["id"] for feature in geojson["features"]}
data_ids = set(df["fips"])

matches = geo_ids.intersection(data_ids)

print(f"Matching counties: {len(matches):,}")


# Keep ONLY counties we know exist in the GeoJSON
df = df[df["fips"].isin(matches)].copy()

print(f"Records being mapped: {len(df):,}")


print("Creating map...")


fig = px.choropleth(
    df,
    geojson=geojson,
    locations="fips",
    featureidkey="id",
    color="health_burden_score",
    color_continuous_scale="RdYlBu_r",
    scope="usa",
    hover_name="locationname",
    hover_data=[
        "statedesc",
        "health_burden_score",
        "burden_percentile",
    ],
)


# IMPORTANT:
# Do NOT use fitbounds here.

fig.update_geos(
    visible=True,
    showcountries=True,
    showsubunits=True,
    showcoastlines=True,
    showland=True,
)


fig.update_layout(
    title="U.S. County Health Burden — 2023",
    height=800,
)


fig.write_html(
    OUTPUT_PATH,
    include_plotlyjs=True,
)


print()
print("=" * 60)
print("MAP TEST COMPLETE")
print("=" * 60)
print(f"Mapped counties: {len(df):,}")
print(f"Output: {OUTPUT_PATH}")
print()