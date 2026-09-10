# Public Health Data Intelligence Dashboard

> Interactive county-level public health analytics using CDC PLACES data.

[🔴 **View Live Dashboard**](https://public-health-data-intelligence.onrender.com)

---

## Overview

This project develops an end-to-end public health data analytics pipeline and interactive dashboard for exploring relative health burden across U.S. counties.

Using CDC PLACES county-level data, the project standardizes 11 public health indicators into a composite relative burden measure and provides interactive geographic, state-level, county-level, and indicator-level analysis.

The resulting Dash application allows users to explore geographic patterns, compare burden across states, identify counties selected for priority analysis, and examine indicator profiles for individual counties.
---

## Dashboard Preview

### County Health Burden Map

![County Health Burden Map](images/dashboard-map.png)

The interactive map provides a national view of relative county-level health burden and allows users to filter results by state and burden category.

### Distribution and State-Level Analysis

![Distribution and State Burden](images/dashboard-state-analysis.png)

The dashboard summarizes the distribution of relative burden scores and compares mean burden across states.

### High-Burden vs. Low-Burden Analysis

![High-Burden vs. Low-Burden Comparison](images/dashboard-high-low.png)

Indicator-level comparisons highlight differences in average prevalence between high- and low-burden county groups.

### Priority County Explorer

![Priority County Explorer](images/dashboard-county-explorer.png)

Users can select an individual priority county to review its burden score, percentile, population, top indicators, and standardized 11-indicator profile.

## Project Highlights

- **2,956 U.S. counties** included in the final analytical model
- **11 standardized public health indicators**
- **148 priority counties** selected for additional analysis
- **99.56% geographic FIPS match rate** between analytical data and county GeoJSON
- Interactive U.S. county-level choropleth map
- State-level burden comparison
- County burden distribution analysis
- High-burden vs. low-burden indicator comparison
- Interactive priority county explorer
- County-level 11-indicator profile visualization
- Production deployment using Dash, Gunicorn, and Render

## Methodology

The analytical workflow follows an end-to-end data preparation and modeling process:

1. Load and profile CDC PLACES county-level data.
2. Clean and validate county-level observations.
3. Standardize the selected public health indicators.
4. Calculate a composite relative health burden score.
5. Convert county scores into percentile rankings.
6. Classify counties into five relative burden categories.
7. Aggregate results for state-level comparison.
8. Identify counties selected for priority analysis.
9. Generate indicator-level comparisons and county profiles.
10. Serve the resulting analytical datasets through an interactive Dash application.

---

### Burden Categories

| Relative Score Percentile | Category |
|---|---|
| 0–20 | Very Low |
| 20–40 | Low |
| 40–60 | Moderate |
| 60–80 | High |
| 80–100 | Very High |
---

## Data Source

The primary data source for this project is the **CDC PLACES** county-level public health dataset.

The analysis uses the **2023 data year** and focuses on county-level measures that can be consistently incorporated into the final 11-indicator analytical model.

Geographic visualization uses U.S. county boundary data represented through GeoJSON and matched to analytical records using FIPS identifiers.

---

> **Interpretation:** The composite burden score is a project-created relative analytical measure. It is not an official CDC score, clinical risk score, or diagnostic measure. The analysis is intended to support exploratory comparison and data visualization.

---

## Limitations

Several considerations should be kept in mind when interpreting the results:

- The composite burden score is a project-created analytical measure rather than an official public health index.
- Scores are relative to the counties included in the analytical dataset.
- The analysis describes associations and geographic patterns rather than causal relationships.
- County-level aggregation can obscure variation within individual communities.
- Some geographic areas do not have corresponding analytical observations and are therefore displayed without a calculated burden score.
- CDC PLACES estimates represent modeled public health measures and should be interpreted within the context of the underlying dataset.

---

## Indicators

The final standardized model uses 11 indicators shared across the analyzed county dataset:

- Obesity
- Diabetes
- High blood pressure
- Stroke
- COPD
- Depression
- Current smoking
- Physical inactivity
- Fair or poor general health
- Poor mental health
- Lack of health insurance/access to care

---

## Key Analytical Findings

The analysis demonstrates substantial geographic variation in relative health burden across U.S. counties.

Comparisons between higher- and lower-burden county groups showed the largest observed prevalence differences across several indicators, including:

- Physical inactivity
- Fair or poor general health
- Obesity
- High blood pressure
- Current smoking

These differences describe observed relationships within the dataset and should not be interpreted as evidence of causation.

---

## Technology Stack

**Data & Analysis**
- Python
- Pandas
- NumPy

**Visualization**
- Plotly
- Dash

**Data Storage / Processing**
- CSV
- SQLite

**Development**
- Jupyter Notebook
- VS Code
- Git / GitHub

**Deployment**
- Gunicorn
- Render
---

## Repository Structure

```text
public-health-data-intelligence/
├── data/
│   ├── raw/
│   └── processed/
├── images/
├── notebooks/
├── reports/
├── src/
│   ├── app.py
│   ├── build_dashboard_model.py
│   ├── burden_analysis.py
│   ├── burden_dashboard_data.py
│   └── dashboard/
│       ├── charts.py
│       ├── data_loader.py
│       └── map.py
├── .gitignore
├── README.md
├── requirements.txt
└── ...
