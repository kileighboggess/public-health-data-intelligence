from pathlib import Path

import pandas as pd


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = PROJECT_ROOT / "data" / "processed"


# --------------------------------------------------
# DATA LOADER
# --------------------------------------------------

def load_dashboard_data():
    """
    Load all prepared dashboard datasets.

    Returns
    -------
    dict
        Dictionary containing county, state, priority,
        and indicator-level dashboard tables.
    """

    county = pd.read_csv(
        DATA_PATH / "dashboard_county.csv",
        low_memory=False
    )

    state = pd.read_csv(
        DATA_PATH / "dashboard_state.csv",
        low_memory=False
    )

    indicator = pd.read_csv(
        DATA_PATH / "dashboard_indicator.csv",
        low_memory=False
    )

    priority = pd.read_csv(
        DATA_PATH / "dashboard_priority.csv",
        low_memory=False
    )

    return {
        "county": county,
        "state": state,
        "indicator": indicator,
        "priority": priority,
    }


# --------------------------------------------------
# DATA VALIDATION
# --------------------------------------------------

def validate_dashboard_data(data):
    """
    Perform basic validation on dashboard datasets.
    """

    required_tables = {
        "county",
        "state",
        "indicator",
        "priority",
    }

    missing_tables = required_tables - set(data.keys())

    if missing_tables:
        raise ValueError(
            f"Missing dashboard tables: {sorted(missing_tables)}"
        )

    if data["county"].empty:
        raise ValueError("County dashboard table is empty.")

    if data["state"].empty:
        raise ValueError("State dashboard table is empty.")

    if data["indicator"].empty:
        raise ValueError("Indicator dashboard table is empty.")

    if data["priority"].empty:
        raise ValueError("Priority county table is empty.")

    if data["county"]["locationid"].duplicated().any():
        raise ValueError(
            "Duplicate county location IDs detected."
        )

    if data["county"]["health_burden_score"].isna().any():
        raise ValueError(
            "Missing health burden scores detected."
        )

    if not data["county"]["burden_percentile"].between(
        0, 100
    ).all():
        raise ValueError(
            "Invalid burden percentiles detected."
        )

    return True


# --------------------------------------------------
# MAIN TEST
# --------------------------------------------------

if __name__ == "__main__":

    print("=" * 70)
    print("PUBLIC HEALTH BURDEN — DASHBOARD DATA LOADER")
    print("=" * 70)

    dashboard_data = load_dashboard_data()

    validate_dashboard_data(dashboard_data)

    print("\nDashboard tables loaded successfully:")

    for name, dataframe in dashboard_data.items():
        print(
            f"  {name:<12} "
            f"{len(dataframe):>6,} rows × "
            f"{len(dataframe.columns):>2} columns"
        )

    print("\n✓ Dashboard data validation passed")
    print("=" * 70)
