import plotly.express as px
import plotly.graph_objects as go


def create_burden_distribution(county_df):
    fig = px.histogram(
        county_df,
        x="health_burden_score",
        nbins=40,
        color="burden_category",
        title="Distribution of County Health Burden",
        labels={
            "health_burden_score": "Relative Health Burden Score",
            "count": "Number of Counties",
        },
    )

    fig.update_layout(
        template="plotly_white",
        height=450,
        margin=dict(l=60, r=30, t=90, b=60),
        hovermode="x unified",
    )

    return fig


def create_state_ranking(state_df):
    plot_df = state_df.sort_values(
        "mean_burden",
        ascending=True
    )

    fig = px.bar(
        plot_df,
        x="mean_burden",
        y="statedesc",
        orientation="h",
        title="State Health Burden",
        labels={
            "mean_burden": "Mean Relative Health Burden",
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
        margin=dict(l=90, r=30, t=90, b=60),
        hovermode="y unified",
    )

    return fig


def create_indicator_relationship(indicator_df):
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
            "correlation_with_burden": "Correlation with Burden Score",
            "indicator": "Indicator",
        },
        text_auto=".3f",
    )

    fig.update_layout(
        template="plotly_white",
        height=550,
        margin=dict(l=80, r=30, t=90, b=60),
        xaxis_range=[-1, 1],
        hovermode="y unified",
    )

    fig.add_vline(
        x=0,
        line_width=1,
        line_dash="dash",
    )

    return fig


def create_priority_indicator_comparison(priority_df):
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
            "percent_difference": "Difference from Overall Average (%)",
            "indicator": "Indicator",
        },
        text_auto=".1f",
    )

    fig.update_layout(
        template="plotly_white",
        height=550,
        margin=dict(l=80, r=30, t=90, b=60),
        hovermode="y unified",
    )

    fig.add_vline(
        x=0,
        line_width=1,
        line_dash="dash",
    )

    return fig


def create_county_profile(county_row):
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
        margin=dict(l=60, r=60, t=90, b=60),
        showlegend=False,
    )

    return fig