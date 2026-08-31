"""
County Health Burden Intelligence Dashboard

Interactive Dash application for exploring county-level
public health burden across the United States.

Data year: 2023
Valid counties: 2,956
Indicators: 11
Priority counties: 148
"""

from pathlib import Path
import json

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from dash import (
    Dash,
    dcc,
    html,
    Input,
    Output,
)

from src.dashboard.charts import create_county_profile

# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data" / "processed"
GEOJSON_PATH = (
    PROJECT_ROOT
    / "data"
    / "geography"
    / "us_counties.geojson"
)


COUNTY_PATH = (
    DATA_DIR / "county_burden_classification.csv"
)

STATE_PATH = (
    DATA_DIR / "state_burden_dashboard.csv"
)

PRIORITY_PATH = (
    DATA_DIR / "priority_county_profiles.csv"
)

PRIORITY_PROFILE_PATH = (
    DATA_DIR / "dashboard_priority_profile.csv"
)

HIGH_LOW_PATH = (
    DATA_DIR / "high_vs_low_burden.csv"
)


# ============================================================
# LOAD DATA
# ============================================================
# Load county boundary GeoJSON
with open(GEOJSON_PATH, "r") as f:
    county_geojson = json.load(f)

# Normalize GeoJSON county IDs to 5-digit FIPS strings
for feature in county_geojson["features"]:
    feature["id"] = str(feature["id"]).zfill(5)

print(
    f"Loaded county GeoJSON: "
    f"{len(county_geojson['features']):,} features"
)

print("Loading dashboard datasets...")

county_df = pd.read_csv(
    COUNTY_PATH,
    low_memory=False
)

state_df = pd.read_csv(
    STATE_PATH,
    low_memory=False
)

priority_df = pd.read_csv(
    PRIORITY_PATH,
    low_memory=False
)

priority_profile_df = pd.read_csv(
    PRIORITY_PROFILE_PATH,
    low_memory=False
)

high_low_df = pd.read_csv(
    HIGH_LOW_PATH,
    low_memory=False
)


# ============================================================
# DATA PREPARATION
# ============================================================

county_df = county_df[
    county_df["health_burden_score"].notna()
].copy()


county_df["fips"] = (
    county_df["locationid"]
    .astype(int)
    .astype(str)
    .str.zfill(5)
)
# ============================================================
# GEOGRAPHIC VALIDATION
# ============================================================

geojson_ids = {
    str(feature["id"]).zfill(5)
    for feature in county_geojson["features"]
}

dashboard_ids = set(
    county_df["fips"]
)

matching_ids = geojson_ids & dashboard_ids

print(
    "\nGeographic validation:"
)

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
    f"{len(matching_ids) / len(dashboard_ids) * 100:.2f}%"
)

assert len(matching_ids) > 0, (
    "No county FIPS IDs matched the GeoJSON."
)

county_df["population_display"] = (
    county_df["totalpopulation"]
    .map(lambda x: f"{x:,.0f}")
)


county_df["score_display"] = (
    county_df["health_burden_score"]
    .map(lambda x: f"{x:.3f}")
)


county_df["percentile_display"] = (
    county_df["burden_percentile"]
    .map(lambda x: f"{x:.1f}%")
)


# ============================================================
# VALIDATION
# ============================================================

assert county_df["locationid"].is_unique
assert county_df["burden_percentile"].between(
    0, 100
).all()

assert state_df[
    "high_or_very_high_pct"
].between(0, 100).all()

assert state_df[
    "high_or_very_high_count"
].le(
    state_df["counties_analyzed"]
).all()


# ============================================================
# KPI VALUES
# ============================================================

TOTAL_COUNTIES = len(county_df)

TOTAL_GEO_COUNTIES = len(
    county_geojson["features"]
)

COUNTIES_WITHOUT_DATA = (
    TOTAL_GEO_COUNTIES
    - len(
        set(county_df["fips"])
        & {
            str(feature["id"]).zfill(5)
            for feature in county_geojson["features"]
        }
    )
)

PRIORITY_COUNTIES = len(priority_df)

INDICATOR_COUNT = 11

DATA_YEAR = int(
    county_df["year"].max()
)

VERY_HIGH_COUNTIES = int(
    (
        county_df["burden_category"]
        == "Very High"
    ).sum()
)

HIGH_OR_VERY_HIGH_COUNTIES = int(
    county_df[
        county_df["burden_category"].isin(
            ["High", "Very High"]
        )
    ].shape[0]
)


# ============================================================
# APP
# ============================================================

app = Dash(
    __name__,
    title="County Health Burden Intelligence"
)


# ============================================================
# STYLES
# ============================================================

PAGE_STYLE = {
    "fontFamily": "Arial, sans-serif",
    "backgroundColor": "#f5f7fa",
    "minHeight": "100vh",
    "paddingBottom": "40px",
}


CARD_STYLE = {
    "backgroundColor": "white",
    "borderRadius": "12px",
    "padding": "18px",
    "boxShadow": "0 2px 10px rgba(0,0,0,0.08)",
    "textAlign": "center",
    "flex": "1",
    "minWidth": "180px",
}


SECTION_STYLE = {
    "backgroundColor": "white",
    "borderRadius": "12px",
    "padding": "20px",
    "margin": "20px 30px",
    "boxShadow": "0 2px 10px rgba(0,0,0,0.06)",
}


# ============================================================
# DROPDOWN OPTIONS
# ============================================================

STATE_OPTIONS = [
    {
        "label": state,
        "value": state,
    }
    for state in sorted(
        county_df["statedesc"]
        .dropna()
        .unique()
    )
]


CATEGORY_OPTIONS = [
    {
        "label": category,
        "value": category,
    }
    for category in [
        "Very Low",
        "Low",
        "Moderate",
        "High",
        "Very High",
    ]
]


# ============================================================
# LAYOUT
# ============================================================

app.layout = html.Div(
    [

        # ====================================================
        # HEADER
        # ====================================================

        html.Div(
            [
                html.P(
    (
        "Explore county-level burden patterns using the filters below. "
        "Colored counties have valid burden scores; gray counties "
        "represent geographic areas without valid analytical data "
        "in the source dataset."
    ),
    style={
        "color": "#666",
        "lineHeight": "1.5",
    },
),

                html.P(
    (
        "U.S. County-Level Public Health "
        f"Analysis | {DATA_YEAR}"
    ),
    style={
        "fontSize": "18px",
        "color": "#555",
    },
),

html.P(
    (
        f"{county_df['stateabbr'].nunique()} jurisdictions "
        "represented | "
        f"{TOTAL_COUNTIES:,} counties with valid burden scores"
    ),
    style={
        "fontSize": "14px",
        "color": "#777",
    },
),

                html.P(
                    (
                        "A composite index integrating "
                        f"{INDICATOR_COUNT} health, behavioral, "
                        "access, and social-needs indicators."
                    ),
                    style={
                        "fontSize": "15px",
                        "color": "#777",
                    },
                ),
            ],
            style={
                "padding": "35px 30px 15px",
                "textAlign": "center",
            },
        ),


        # ====================================================
        # KPI CARDS
        # ====================================================

        html.Div(
            [

                html.Div(
                    [
                        html.H4("Counties Analyzed"),
                        html.H2(
                            f"{TOTAL_COUNTIES:,}"
                        ),
                        html.P(
                            "Counties with valid burden scores"
                        ),
                    ],
                    style=CARD_STYLE,
                ),

                html.Div(
                    [
                        html.H4("High / Very High"),
                        html.H2(
                            f"{HIGH_OR_VERY_HIGH_COUNTIES:,}"
                        ),
                        html.P(
                            "Counties in upper burden categories"
                        ),
                    ],
                    style=CARD_STYLE,
                ),

                html.Div(
                    [
                        html.H4("Priority Counties"),
                        html.H2(
                            f"{PRIORITY_COUNTIES:,}"
                        ),
                        html.P(
                            "Flagged for priority analysis"
                        ),
                    ],
                    style=CARD_STYLE,
                ),

                html.Div(
                    [
                        html.H4("Indicators"),
                        html.H2(
                            f"{INDICATOR_COUNT}"
                        ),
                        html.P(
                            "Health and social indicators"
                        ),
                    ],
                    style=CARD_STYLE,
                ),

                html.Div(
                    [
                        html.H4("Data Year"),
                        html.H2(
                            str(DATA_YEAR)
                        ),
                        html.P(
                            "Latest available year analyzed"
                        ),
                    ],
                    style=CARD_STYLE,
                ),

            ],
            style={
                "display": "flex",
                "gap": "18px",
                "padding": "0 30px",
                "flexWrap": "wrap",
            },
        ),


        # ====================================================
        # FILTERS
        # ====================================================

        html.Div(
            [

                html.H3(
                    "Explore County Burden"
                ),

                html.Div(
                    [

                        html.Div(
                            [
                                html.Label(
                                    "State"
                                ),

                                dcc.Dropdown(
                                    id="state-filter",
                                    options=STATE_OPTIONS,
                                    placeholder=(
                                        "All states"
                                    ),
                                    clearable=True,
                                ),
                            ],
                            style={
                                "flex": "1"
                            },
                        ),

                        html.Div(
                            [
                                html.Label(
                                    "Burden Category"
                                ),

                                dcc.Dropdown(
                                    id="category-filter",
                                    options=CATEGORY_OPTIONS,
                                    placeholder=(
                                        "All categories"
                                    ),
                                    clearable=True,
                                ),
                            ],
                            style={
                                "flex": "1"
                            },
                        ),

                    ],
                    style={
                        "display": "flex",
                        "gap": "20px",
                        "flexWrap": "wrap",
                    },
                ),

            ],
            style=SECTION_STYLE,
        ),


        # ====================================================
        # MAP
        # ====================================================

        html.Div(
            [

                html.H2(
                    "County Health Burden Map"
                ),

                html.P(
                    (
                        "Select a state or burden category "
                        "to explore county-level patterns."
                    ),
                    style={
                        "color": "#666"
                    },
                ),

                dcc.Graph(
                    id="burden-map",
                    style={
                        "height": "650px"
                    },
                ),

            ],
            style=SECTION_STYLE,
        ),


        # ====================================================
        # DISTRIBUTION + STATE RANKING
        # ====================================================

        html.Div(
            [

                html.Div(
                    [
                        html.H2(
                            "Burden Distribution"
                        ),

                        dcc.Graph(
                            id="burden-distribution"
                        ),
                    ],
                    style={
                        "flex": "1",
                        "minWidth": "400px",
                    },
                ),

                html.Div(
                    [
                        html.H2(
                            "State Burden Ranking"
                        ),

                        dcc.Graph(
                            id="state-ranking"
                        ),
                    ],
                    style={
                        "flex": "1",
                        "minWidth": "400px",
                    },
                ),

            ],
            style={
                "display": "flex",
                "gap": "20px",
                "margin": "20px 30px",
                "flexWrap": "wrap",
            },
        ),


        # ====================================================
        # INDICATOR ANALYSIS
        # ====================================================

        html.Div(
            [

                html.H2(
                    "High-Burden vs. Low-Burden Counties"
                ),

                html.P(
                    (
                        "Difference in average indicator prevalence "
                        "between high- and low-burden counties."
                    ),
                    style={
                        "color": "#666"
                    },
                ),

                dcc.Graph(
                    id="indicator-comparison"
                ),

            ],
            style=SECTION_STYLE,
        ),


        # ====================================================
        # PRIORITY COUNTIES
        # ====================================================

        html.Div(
            [

                html.H2(
                    "Priority County Explorer"
                ),

                html.P(
                    (
                        "Counties identified for priority analysis "
                        "based on burden and analytical criteria."
                    ),
                    style={
                        "color": "#666"
                    },
                ),

                dcc.Dropdown(
                    id="priority-county-filter",
                    options=[
                        {
                            "label": (
                                f"{row.locationname}, "
                                f"{row.statedesc}"
                            ),
                            "value": int(
                                row.locationid
                            ),
                        }
                        for row in priority_df.itertuples()
                    ],
                    placeholder=(
                        "Select a priority county"
                    ),
                    clearable=True,
                ),

                html.Div(
    id="priority-county-details",
    style={
        "marginTop": "20px"
    },
),

dcc.Graph(
    id="priority-county-profile",
    style={
        "marginTop": "20px"
    },
),

            ],
            style=SECTION_STYLE,
        ),


        # ====================================================
        # FOOTER
        # ====================================================

        html.Div(
            [
                html.P(
                    (
                        "County Health Burden Intelligence | "
                        "Python + Pandas + Plotly + Dash"
                    ),
                    style={
                        "textAlign": "center",
                        "color": "#777",
                    },
                ),

                html.P(
                    (
                        "Burden scores are relative analytical "
                        "measures and should not be interpreted "
                        "as clinical risk scores."
                    ),
                    style={
                        "textAlign": "center",
                        "fontSize": "12px",
                        "color": "#999",
                    },
                ),
            ],
            style={
                "padding": "20px"
            },
        ),

    ],
    style=PAGE_STYLE,
)

# ============================================================
# CALLBACK: MAP
# ============================================================

@app.callback(
    Output(
        "burden-map",
        "figure"
    ),
    Input(
        "state-filter",
        "value"
    ),
    Input(
        "category-filter",
        "value"
    ),
)
def update_map(
    selected_state,
    selected_category,
):

    # --------------------------------------------------------
    # START WITH COUNTY DATA
    # --------------------------------------------------------

    df = county_df.copy()

    # --------------------------------------------------------
    # APPLY STATE FILTER
    # --------------------------------------------------------

    if selected_state:
        df = df[
            df["statedesc"] == selected_state
        ].copy()

    # --------------------------------------------------------
    # APPLY BURDEN CATEGORY FILTER
    # --------------------------------------------------------

    if selected_category:
        df = df[
            df["burden_category"] == selected_category
        ].copy()

    # --------------------------------------------------------
    # KEEP VALID RECORDS
    # --------------------------------------------------------

    df = df[
        df["health_burden_score"].notna()
    ].copy()

    # --------------------------------------------------------
    # ENSURE FIPS IS A STRING
    # --------------------------------------------------------

    df["fips"] = (
        df["locationid"]
        .astype(int)
        .astype(str)
        .str.zfill(5)
    )

    # --------------------------------------------------------
    # ONLY KEEP COUNTIES THAT EXIST IN GEOJSON
    # --------------------------------------------------------

    geojson_ids = {
        str(feature["id"]).zfill(5)
        for feature in county_geojson["features"]
    }

    df = df[
        df["fips"].isin(geojson_ids)
    ].copy()

    print(
        f"Map update: {len(df):,} counties"
    )

    # --------------------------------------------------------
    # HANDLE EMPTY FILTER RESULTS
    # --------------------------------------------------------

    if df.empty:

        fig = go.Figure()

        fig.update_geos(
            visible=False,
            projection_type="albers usa",
        )

        fig.update_layout(
            title="No counties match the selected filters",
            paper_bgcolor="white",
            plot_bgcolor="white",
            margin={
                "r": 0,
                "t": 50,
                "l": 0,
                "b": 0,
            },
        )

        return fig

    # --------------------------------------------------------
    # CREATE CHOROPLETH
    # --------------------------------------------------------

    fig = go.Figure(
        go.Choropleth(
            geojson=county_geojson,
            locations=df["fips"].tolist(),
            z=df["health_burden_score"].tolist(),
            featureidkey="id",
            colorscale="RdYlBu_r",
            colorbar={
                "title": {
                    "text": "Health Burden Score"
                }
            },
            marker_line_color="white",
            marker_line_width=0.25,
            customdata=df[
                [
                    "locationname",
                    "statedesc",
                    "burden_percentile",
                    "burden_category",
                    "totalpopulation",
                ]
            ].values,
            hovertemplate=(
                "<b>%{customdata[0]} County</b><br>"
                "State: %{customdata[1]}<br>"
                "Burden Score: %{z:.3f}<br>"
                "Percentile: %{customdata[2]:.1f}%<br>"
                "Category: %{customdata[3]}<br>"
                "Population: %{customdata[4]:,.0f}"
                "<extra></extra>"
            ),
        )
    )

    # --------------------------------------------------------
    # MAP CONFIGURATION
    # --------------------------------------------------------

    fig.update_geos(
    projection_type="albers usa"
)

    fig.update_layout(
    title={
        "text": "County Health Burden Map",
        "x": 0.5,
        "xanchor": "center",
    },
    paper_bgcolor="white",
    plot_bgcolor="white",
    margin={
        "r": 20,
        "t": 55,
        "l": 20,
        "b": 20,
    },
    height=650,
)

    return fig

# ============================================================
# CALLBACK: DISTRIBUTION
# ============================================================

@app.callback(
    Output(
        "burden-distribution",
        "figure"
    ),
    Input(
        "state-filter",
        "value"
    ),
)
def update_distribution(
    selected_state
):

    df = county_df.copy()

    if selected_state:
        df = df[
            df["statedesc"]
            == selected_state
        ]

    fig = px.histogram(
        df,
        x="health_burden_score",
        nbins=30,
        color="burden_category",
        category_orders={
            "burden_category": [
                "Very Low",
                "Low",
                "Moderate",
                "High",
                "Very High",
            ]
        },
        title=(
            "Distribution of County Burden Scores"
        ),
    )

    fig.update_layout(
        xaxis_title="Health Burden Score",
        yaxis_title="Number of Counties",
        legend_title="Burden Category",
        bargap=0.05,
    )

    return fig


# ============================================================
# CALLBACK: STATE RANKING
# ============================================================

@app.callback(
    Output(
        "state-ranking",
        "figure"
    ),
    Input(
        "state-filter",
        "value"
    ),
)
def update_state_ranking(
    selected_state
):

    df = state_df.copy()

    if selected_state:
        df = df[
            df["statedesc"]
            == selected_state
        ]

    df = df.sort_values(
        "mean_burden",
        ascending=True,
    )

    fig = px.bar(
        df,
        x="mean_burden",
        y="statedesc",
        orientation="h",
        hover_data={
            "mean_burden": ":.3f",
            "high_or_very_high_pct": ":.1f",
            "counties_analyzed": True,
        },
        title="Mean County Burden by State",
    )

    fig.update_layout(
        xaxis_title="Mean Burden Score",
        yaxis_title="",
    )

    return fig


# ============================================================
# CALLBACK: INDICATOR COMPARISON
# ============================================================

@app.callback(
    Output(
        "indicator-comparison",
        "figure"
    ),
    Input(
        "state-filter",
        "value"
    ),
)
def update_indicator_comparison(
    selected_state
):

    df = high_low_df.copy()

    fig = px.bar(
        df.sort_values(
            "difference",
            ascending=True,
        ),
        x="difference",
        y="indicator",
        orientation="h",
        title=(
            "Indicator Differences: "
            "High vs. Low Burden Counties"
        ),
        hover_data={
            "high_burden_mean": ":.2f",
            "low_burden_mean": ":.2f",
            "difference": ":.2f",
        },
    )

    fig.update_layout(
        xaxis_title="Difference in Percentage Points",
        yaxis_title="",
    )

    return fig

# ============================================================
# CALLBACK: PRIORITY COUNTY DETAILS
# ============================================================

@app.callback(
    Output(
        "priority-county-details",
        "children"
    ),
    Input(
        "priority-county-filter",
        "value"
    ),
)
def update_priority_details(selected_id):

    # --------------------------------------------------------
    # EMPTY STATE
    # --------------------------------------------------------

    if not selected_id:
        return html.P(
            "Select a priority county to view its profile.",
            style={
                "color": "#777",
                "fontSize": "16px",
            },
        )

    # --------------------------------------------------------
    # FIND SELECTED COUNTY
    # --------------------------------------------------------

    row = priority_df[
        priority_df["locationid"] == selected_id
    ]

    if row.empty:
        return html.P(
            "County profile not found.",
            style={
                "color": "#777",
            },
        )

    row = row.iloc[0]

    # --------------------------------------------------------
    # TOP INDICATORS
    # --------------------------------------------------------

    top_indicators = [
        row["top_indicator_1"],
        row["top_indicator_2"],
        row["top_indicator_3"],
    ]

    # --------------------------------------------------------
    # SUMMARY CARDS
    # --------------------------------------------------------

    cards = [

        html.Div(
            [
                html.H4(
                    "County",
                    style={
                        "marginBottom": "5px"
                    },
                ),
                html.H2(
                    f"{row['locationname']}, "
                    f"{row['stateabbr']}",
                    style={
                        "marginTop": "0px"
                    },
                ),
            ],
            style=CARD_STYLE,
        ),

        html.Div(
            [
                html.H4(
                    "Burden Score",
                    style={
                        "marginBottom": "5px"
                    },
                ),
                html.H2(
                    f"{row['health_burden_score']:.3f}",
                    style={
                        "marginTop": "0px"
                    },
                ),
            ],
            style=CARD_STYLE,
        ),

        html.Div(
            [
                html.H4(
                    "Burden Percentile",
                    style={
                        "marginBottom": "5px"
                    },
                ),
                html.H2(
                    f"{row['burden_percentile']:.1f}%",
                    style={
                        "marginTop": "0px"
                    },
                ),
            ],
            style=CARD_STYLE,
        ),

        html.Div(
            [
                html.H4(
                    "Population",
                    style={
                        "marginBottom": "5px"
                    },
                ),
                html.H2(
                    f"{row['totalpopulation']:,.0f}",
                    style={
                        "marginTop": "0px"
                    },
                ),
            ],
            style=CARD_STYLE,
        ),

    ]

    # --------------------------------------------------------
    # RETURN PROFILE SUMMARY
    # --------------------------------------------------------

    return html.Div(
        [

            html.Div(
                cards,
                style={
                    "display": "flex",
                    "gap": "15px",
                    "flexWrap": "wrap",
                },
            ),

            html.Div(
                [

                    html.H3(
                        "Top Indicators",
                        style={
                            "marginBottom": "10px"
                        },
                    ),

                    html.Ul(
                        [
                            html.Li(
                                indicator
                            )
                            for indicator
                            in top_indicators
                        ],
                        style={
                            "lineHeight": "1.8",
                        },
                    ),

                ],
                style={
                    "marginTop": "20px",
                },
            ),

        ]
    )


# ============================================================
# CALLBACK: PRIORITY COUNTY PROFILE
# ============================================================

@app.callback(
    Output(
        "priority-county-profile",
        "figure"
    ),
    Input(
        "priority-county-filter",
        "value"
    ),
)
def update_priority_profile(selected_id):

    # --------------------------------------------------------
    # EMPTY STATE
    # --------------------------------------------------------

    if not selected_id:

        fig = go.Figure()

        fig.update_layout(
            title=(
                "Select a priority county "
                "to view its indicator profile"
            ),
            template="plotly_white",
            height=550,
        )

        return fig

    # --------------------------------------------------------
    # FIND SELECTED COUNTY
    # --------------------------------------------------------

    row = priority_profile_df[
        priority_profile_df["locationid"] == selected_id
    ]

    if row.empty:

        fig = go.Figure()

        fig.update_layout(
            title="County profile not found",
            template="plotly_white",
            height=550,
        )

        return fig

    # --------------------------------------------------------
    # CREATE RADAR PROFILE
    # --------------------------------------------------------

    county_row = row.iloc[0]

    fig = create_county_profile(
        county_row
    )

    # --------------------------------------------------------
    # COUNTY TITLE
    # --------------------------------------------------------

    county_name = (
        f"{county_row['locationname']}, "
        f"{county_row['stateabbr']}"
    )

    fig.update_layout(
        title=(
            f"{county_name} — "
            "Standardized Indicator Profile"
        ),
        height=550,
        margin={
            "r": 40,
            "t": 80,
            "l": 40,
            "b": 40,
        },
    )

    return fig


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    print(
        "\nStarting County Health Burden Dashboard..."
    )

    print(
        "Open http://127.0.0.1:8050/ "
        "in your browser."
    )

    app.run(
        debug=True
    )
