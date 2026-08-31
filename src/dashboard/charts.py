import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# --------------------------------------------------
# BURDEN DISTRIBUTION
# --------------------------------------------------

def create_burden_distribution(county_df):
    """
    Create a histogram showing the distribution
    of county health burden scores.
    """

    fig = px.histogram(
        county_df,
        x="health_burden_score",
        nbins=40,
        title="Distribution of County Health Burden Scores",
        labels={
            "health_burden_score": "Health Burden Score",
            "count": "Number of Counties",
        },
    )

    fig.update_layout(
        template="plotly_white",
        height=450,
    )

    return fig


# --------------------------------------------------
# STATE BURDEN RANKING
# --------------------------------------------------

def create_state_ranking(state_df):
    """
    Rank states by mean health burden.
    """

    plot_df = state_df.sort_values(
        "mean_burden",
        ascending=True
    )

    fig = px.bar(
        plot_df,
        x="mean_burden",
        y="statedesc",
        orientation="h",
        title="State Health Burden Ranking",
        labels={
            "mean_burden": "Mean Health Burden",
            "statedesc": "State",
        },
        hover_data=[
            "high_or_very_high_pct",
            "counties_analyzed",
        ],
    )

    fig.update_layout(
        template="plotly_white",
        height=900,
    )

    return fig


# --------------------------------------------------
# INDICATOR-BURDEN RELATIONSHIP
# --------------------------------------------------

def create_indicator_relationship(indicator_df):
    """
    Show correlation between each indicator
    and the overall health burden score.
    """

    plot_df = indicator_df.sort_values(
        "correlation_with_burden",
        ascending=True
    )

    fig = px.bar(
        plot_df,
        x="correlation_with_burden",
        y="indicator",
        orientation="h",
        title="Indicator Relationships with Overall Health Burden",
        labels={
            "correlation_with_burden": "Correlation",
            "indicator": "Indicator",
        },
        text_auto=".3f",
    )

    fig.update_layout(
        template="plotly_white",
        height=550,
        xaxis_range=[0, 1],
    )

    return fig


# --------------------------------------------------
# PRIORITY INDICATOR COMPARISON
# --------------------------------------------------

def create_priority_indicator_comparison(priority_df):
    """
    Compare indicator prevalence between priority
    counties and the overall county population.
    """

    plot_df = priority_df.sort_values(
        "percent_difference",
        ascending=True
    )

    fig = px.bar(
        plot_df,
        x="percent_difference",
        y="indicator",
        orientation="h",
        title="Priority Counties vs. Overall County Average",
        labels={
            "percent_difference": "Difference (%)",
            "indicator": "Indicator",
        },
        text_auto=".1f",
    )

    fig.update_layout(
        template="plotly_white",
        height=550,
    )

    return fig


# --------------------------------------------------
# COUNTY INDICATOR PROFILE
# --------------------------------------------------

def create_county_profile(county_row):
    """
    Create a radar chart showing the selected
    county's standardized indicator profile.
    """

    indicators = [
        "OBESITY_z",
        "DIABETES_z",
        "BPHIGH_z",
        "STROKE_z",
        "COPD_z",
        "DEPRESSION_z",
        "CSMOKING_z",
        "LPA_z",
        "GHLTH_z",
        "MHLTH_z",
        "ACCESS2_z",
    ]

    labels = [
        indicator.replace("_z", "")
        for indicator in indicators
    ]

    values = [
        float(county_row[indicator])
        for indicator in indicators
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=values + [values[0]],
            theta=labels + [labels[0]],
            fill="toself",
            name="County",
        )
    )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True
            )
        ),
        title="County Indicator Profile",
        template="plotly_white",
        height=550,
    )

    return fig
