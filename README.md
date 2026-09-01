# County Health Burden Intelligence Dashboard

An interactive county-level public health analytics platform designed to explore geographic patterns in 
health burden across the United States.

The project integrates 11 health, behavioral, healthcare access, and social-needs indicators into a 
composite county health burden index and provides interactive tools for geographic exploration, 
state-level comparison, and priority-county analysis.

---

## Project Overview

Public health conditions vary substantially across geographic areas. This project was developed to 
examine those differences at the county level and create an analytical framework for identifying areas 
with elevated health burden.

The final product combines:

- Data cleaning and validation
- County-level statistical analysis
- Composite index construction
- Geographic analysis
- Indicator correlation analysis
- Priority-county identification
- Interactive visualization
- Dashboard development

The result is an interactive Dash application that allows users to move from national patterns to 
individual county-level profiles.

---

## Dashboard

The dashboard provides an interactive view of county-level health burden across the United States.

### Key Dashboard Features

- Interactive U.S. county-level burden map
- State filtering
- Burden-category filtering
- County burden distribution
- State burden ranking
- High-burden vs. low-burden indicator comparison
- Priority County Explorer
- County-level standardized indicator profiles
- Population and burden metrics for selected priority counties

---

## Key Project Metrics

| Metric | Value |
|---|---:|
| Jurisdictions represented | 49 |
| Counties with valid burden scores | 2,956 |
| Priority counties | 148 |
| Health indicators | 11 |
| Data year analyzed | 2023 |
| Geographic features in reference GeoJSON | 3,221 |
| Counties matched to analytical data | 2,943 |

---

## Analytical Framework

### Composite Health Burden Index

The project combines multiple public health indicators into a standardized composite burden score.

Indicators included in the analytical model include:

- Obesity
- Diabetes
- High blood pressure
- Stroke
- COPD
- Depression
- Current smoking
- Physical inactivity
- General health
- Mental health
- Healthcare access

Indicators were standardized to support comparison across measures with different prevalence 
distributions and scales.

The resulting composite score provides a relative measure of county-level health burden.

---

## Geographic Analysis

A county-level geographic analysis was performed using FIPS identifiers to connect analytical data with 
county boundary geometry.

Geographic validation produced:

- 3,221 county features in the reference GeoJSON
- 2,956 counties represented in the analytical dashboard dataset
- 2,943 matching FIPS identifiers
- 99.56% dashboard geographic match rate

Counties without valid analytical scores are displayed separately from counties with available burden 
measurements.

---

## Priority County Analysis

The Priority County Explorer provides a deeper analytical view of counties identified for priority 
analysis.

For each selected county, the dashboard provides:

- County name and state
- Composite burden score
- Burden percentile
- Population
- Top contributing indicators
- Standardized indicator profile

This allows users to move beyond a single composite score and examine the underlying health indicators 
contributing to a county's profile.

---

## Selected Analytical Findings

The high-burden vs. low-burden analysis shows meaningful differences across the 11 indicators.

The largest observed prevalence differences in the project include:

1. Physical inactivity (LPA)
2. General health (GHLTH)
3. Obesity
4. High blood pressure
5. Current smoking

These results describe observed differences between county groups and should not be interpreted as 
evidence of causal relationships.

The geographic analysis also demonstrates substantial variation in county burden across the United 
States, highlighting the importance of examining public health conditions below the state level.

---

## Technology Stack

### Programming & Analysis

- Python
- Pandas
- NumPy

### Visualization

- Plotly
- Plotly Express
- Plotly Graph Objects

### Dashboard

- Dash
- Flask

### Data & Geographic Analysis

- CSV-based analytical datasets
- County FIPS identifiers
- GeoJSON
- Statistical standardization
- Geographic validation

### Development

- Git
- GitHub
- Python virtual environments

---

## Project Structure

```text
public-health-data-intelligence/
│
├── data/
│   ├── geography/
│   │   └── us_counties.geojson
│   │
│   ├── processed/
│   │   ├── county_burden_classification.csv
│   │   ├── county_health_burden.csv
│   │   ├── dashboard_county.csv
│   │   ├── dashboard_indicator.csv
│   │   ├── dashboard_priority.csv
│   │   ├── dashboard_priority_profile.csv
│   │   ├── dashboard_state.csv
│   │   ├── high_burden_counties.csv
│   │   ├── high_vs_low_burden.csv
│   │   ├── indicator_burden_relationship.csv
│   │   ├── indicator_burden_relationships.csv
│   │   ├── indicator_correlation_matrix.csv
│   │   ├── indicator_geographic_summary.csv
│   │   ├── indicator_metadata.csv
│   │   ├── indicator_pair_correlations.csv
│   │   ├── priority_indicator_comparison.csv
│   │   ├── state_burden_dashboard.csv
│   │   ├── state_burden_summary.csv
│   │   └── state_indicator_summary.csv
│   │
│   └── visualizations/
│       ├── county_burden_distribution.png
│       ├── high_vs_low_burden_indicators.png
│       ├── state_burden_ranking.png
│       └── top_20_counties_by_burden.png
│
├── notebooks/
│   └── 01_data_exploration.ipynb
│
├── src/
│   ├── app.py
│   ├── audit_geographic_coverage.py
│   ├── build_dashboard_model.py
│   ├── burden_analysis.py
│   ├── burden_dashboard_data.py
│   ├── burden_index.py
│   ├── county_burden_map.py
│   ├── dashboard_metrics.py
│   ├── data_cleaning.py
│   ├── geographic_analysis.py
│   ├── indicator_analysis.py
│   ├── indicator_metadata.py
│   ├── validate_burden_index.py
│   ├── validate_index_statistics.py
│   ├── visualize_burden.py
│   │
│   └── dashboard/
│       ├── __init__.py
│       ├── charts.py
│       ├── data_loader.py
│       └── map.py
│
├── .gitignore
└── README.md
