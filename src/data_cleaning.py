from pathlib import Path
import pandas as pd

# --------------------------------------------------
# Project paths
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
# Load processed dataset
# --------------------------------------------------

print(f"Loading processed dataset: {DATA_PATH}")

df = pd.read_csv(DATA_PATH)

print(f"Dataset loaded: {len(df):,} records")

# --------------------------------------------------
# Create indicator metadata
# --------------------------------------------------

indicator_metadata = (
    df[
        [
            "MeasureId",
            "Measure",
            "Category",
            "DataValueTypeID",
            "Data_Value_Unit"
        ]
    ]
    .drop_duplicates()
    .sort_values(["Category", "Measure"])
    .reset_index(drop=True)
)

# --------------------------------------------------
# Rename columns
# --------------------------------------------------

indicator_metadata = indicator_metadata.rename(
    columns={
        "MeasureId": "measure_id",
        "Measure": "measure",
        "Category": "category",
        "DataValueTypeID": "data_value_type",
        "Data_Value_Unit": "unit"
    }
)

# --------------------------------------------------
# Display results
# --------------------------------------------------

print("\nIndicator Metadata")
print("-" * 80)

print(indicator_metadata.to_string(index=False))

print("\n")
print(f"Unique indicators: {indicator_metadata['measure_id'].nunique()}")
print(f"Unique categories: {indicator_metadata['category'].nunique()}")

# --------------------------------------------------
# Save metadata
# --------------------------------------------------

indicator_metadata.to_csv(
    OUTPUT_PATH,
    index=False
)

print("\nMetadata file created:")
print(OUTPUT_PATH)