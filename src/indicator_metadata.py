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

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "indicator_metadata.csv"
)


# --------------------------------------------------
# LOAD PROCESSED DATA
# --------------------------------------------------

print(f"Loading processed dataset: {DATA_PATH}")

df = pd.read_csv(
    DATA_PATH,
    low_memory=False
)

print(f"Dataset loaded: {len(df):,} records")


# --------------------------------------------------
# CREATE INDICATOR METADATA
# --------------------------------------------------

metadata_columns = [
    "measureid",
    "measure",
    "category",
    "datavaluetypeid",
    "data_value_unit"
]

metadata = (
    df[metadata_columns]
    .drop_duplicates()
    .sort_values(
        ["category", "measure"]
    )
    .reset_index(drop=True)
)


# --------------------------------------------------
# RENAME FOR READABILITY
# --------------------------------------------------

metadata = metadata.rename(
    columns={
        "measureid": "measure_id",
        "datavaluetypeid": "data_value_type"
    }
)


# --------------------------------------------------
# SAVE METADATA
# --------------------------------------------------

metadata.to_csv(
    OUTPUT_PATH,
    index=False
)


# --------------------------------------------------
# VALIDATION / SUMMARY
# --------------------------------------------------

print()
print("Indicator metadata created successfully!")
print("-" * 60)

print(f"Unique indicators: {metadata['measure_id'].nunique()}")
print(f"Unique categories: {metadata['category'].nunique()}")

print()
print("Indicators by category:")

print(
    metadata["category"]
    .value_counts()
    .sort_index()
)

print()
print("Sample indicators:")

print(
    metadata.head(15).to_string(index=False)
)

print("-" * 60)

print()
print("Metadata file created:")
print(OUTPUT_PATH)