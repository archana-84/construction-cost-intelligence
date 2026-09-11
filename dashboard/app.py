import pandas as pd
import streamlit as st
from pathlib import Path
import plotly.express as px

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Construction Cost Intelligence",
    page_icon="🏗️",
    layout="wide"
)


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "construction_cost_analysis.csv"
)

ANOMALY_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "project_anomalies.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():
    """Load the processed construction cost dataset."""

    df = pd.read_csv(DATA_PATH)

    df["start_date"] = pd.to_datetime(
        df["start_date"]
    )

    df["end_date"] = pd.to_datetime(
        df["end_date"]
    )

    return df




@st.cache_data
def load_anomaly_data():

    if ANOMALY_PATH.exists():

        anomaly_df = pd.read_csv(
            ANOMALY_PATH
        )

        return anomaly_df

    return pd.DataFrame()

df = load_data()

anomaly_df = load_anomaly_data()

# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("Dashboard Filters")


# Location filter
location_options = sorted(
    df["location"].dropna().unique()
)

selected_locations = st.sidebar.multiselect(
    "Location",
    options=location_options,
    default=location_options
)


# Project type filter
project_type_options = sorted(
    df["project_type"].dropna().unique()
)

selected_project_types = st.sidebar.multiselect(
    "Project Type",
    options=project_type_options,
    default=project_type_options
)


# Complexity filter
complexity_options = sorted(
    df["complexity"].dropna().unique()
)

selected_complexities = st.sidebar.multiselect(
    "Complexity",
    options=complexity_options,
    default=complexity_options
)


# Category filter
category_options = sorted(
    df["category"].dropna().unique()
)

selected_categories = st.sidebar.multiselect(
    "Cost Category",
    options=category_options,
    default=category_options
)


# Project filter
project_options = (
    df[
        [
            "project_id",
            "project_name"
        ]
    ]
    .drop_duplicates()
    .sort_values("project_name")
)

project_display_options = (
    project_options["project_id"]
    + " - "
    + project_options["project_name"]
)

selected_projects = st.sidebar.multiselect(
    "Project",
    options=project_display_options,
    default=project_display_options
)


# Convert selected project labels back to project IDs
selected_project_ids = [
    project.split(" - ")[0]
    for project in selected_projects
]


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = df[
    df["location"].isin(selected_locations)
    & df["project_type"].isin(selected_project_types)
    & df["complexity"].isin(selected_complexities)
    & df["category"].isin(selected_categories)
    & df["project_id"].isin(selected_project_ids)
].copy()
# ============================================================
# DASHBOARD HEADER
# ============================================================

st.title("🏗️ Construction Cost Intelligence Dashboard")

st.markdown(
    """
    Monitor estimated vs. actual construction costs,
    identify cost overruns, and investigate key cost drivers.
    """
)

st.divider()


# ============================================================
# OVERALL KPI CALCULATIONS
# ============================================================

total_estimated_cost = filtered_df["estimated_cost"].sum()

total_actual_cost = filtered_df["actual_cost"].sum()

total_variance = (
    total_actual_cost
    - total_estimated_cost
)

if total_estimated_cost > 0:

    overall_variance_pct = (
        total_variance
        / total_estimated_cost
    ) * 100

else:

    overall_variance_pct = 0


# ============================================================
# KPI CARDS
# ============================================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        label="Estimated Cost",
        value=f"${total_estimated_cost / 1_000_000_000:.2f}B"
    )


with col2:

    st.metric(
        label="Actual Cost",
        value=f"${total_actual_cost / 1_000_000_000:.2f}B"
    )


with col3:

    st.metric(
        label="Cost Overrun",
        value=f"${total_variance / 1_000_000:.2f}M"
    )


with col4:

    st.metric(
        label="Variance",
        value=f"{overall_variance_pct:.2f}%"
    )


st.divider()

# ============================================================
# COST ANALYSIS BY CATEGORY
# ============================================================

st.subheader("Estimated vs. Actual Cost by Category")


category_summary = (
    filtered_df
    .groupby("category")
    .agg(
        estimated_cost=("estimated_cost", "sum"),
        actual_cost=("actual_cost", "sum")
    )
    .reset_index()
)


category_chart_data = category_summary.melt(
    id_vars="category",
    value_vars=[
        "estimated_cost",
        "actual_cost"
    ],
    var_name="cost_type",
    value_name="cost"
)


category_chart_data["cost_type"] = (
    category_chart_data["cost_type"]
    .replace(
        {
            "estimated_cost": "Estimated Cost",
            "actual_cost": "Actual Cost"
        }
    )
)


fig_category = px.bar(
    category_chart_data,
    x="category",
    y="cost",
    color="cost_type",
    barmode="group",
    labels={
        "category": "Cost Category",
        "cost": "Cost",
        "cost_type": "Cost Type"
    }
)


fig_category.update_layout(
    xaxis_title="Cost Category",
    yaxis_title="Cost ($)",
    legend_title="",
    hovermode="x unified"
)


st.plotly_chart(
    fig_category,
    width="stretch"
)

# ============================================================
# COST TREND OVER TIME
# ============================================================

st.subheader("Estimated vs. Actual Cost Trend")


# Create a month column from each project's start date
trend_data = filtered_df.copy()

trend_data["start_month"] = (
    trend_data["start_date"]
    .dt.to_period("M")
    .dt.to_timestamp()
)


# Summarize estimated and actual cost by month
monthly_cost_summary = (
    trend_data
    .groupby("start_month")
    .agg(
        estimated_cost=("estimated_cost", "sum"),
        actual_cost=("actual_cost", "sum")
    )
    .reset_index()
    .sort_values("start_month")
)


# Calculate monthly cost variance
monthly_cost_summary["cost_variance"] = (
    monthly_cost_summary["actual_cost"]
    - monthly_cost_summary["estimated_cost"]
)


# Convert data to long format for Plotly
monthly_chart_data = (
    monthly_cost_summary
    .melt(
        id_vars="start_month",
        value_vars=[
            "estimated_cost",
            "actual_cost"
        ],
        var_name="cost_type",
        value_name="cost"
    )
)


# Rename values for better chart labels
monthly_chart_data["cost_type"] = (
    monthly_chart_data["cost_type"]
    .replace(
        {
            "estimated_cost": "Estimated Cost",
            "actual_cost": "Actual Cost"
        }
    )
)


# Create line chart
fig_monthly_cost = px.line(
    monthly_chart_data,
    x="start_month",
    y="cost",
    color="cost_type",
    markers=True,
    labels={
        "start_month": "Project Start Month",
        "cost": "Cost ($)",
        "cost_type": "Cost Type"
    }
)


fig_monthly_cost.update_layout(
    xaxis_title="Project Start Month",
    yaxis_title="Cost ($)",
    legend_title="",
    hovermode="x unified"
)


st.plotly_chart(
    fig_monthly_cost,
    width="stretch"
)

# ============================================================
# EXECUTIVE INSIGHTS
# ============================================================

st.subheader("Executive Insights")


# ------------------------------------------------------------
# 1. HIGHEST-OVERRUN PROJECT
# ------------------------------------------------------------

executive_project_summary = (
    filtered_df
    .groupby(
        [
            "project_id",
            "project_name"
        ]
    )
    .agg(
        estimated_cost=("estimated_cost", "sum"),
        actual_cost=("actual_cost", "sum")
    )
    .reset_index()
)


executive_project_summary["cost_variance"] = (
    executive_project_summary["actual_cost"]
    - executive_project_summary["estimated_cost"]
)


executive_project_summary["variance_pct"] = (
    executive_project_summary["cost_variance"]
    / executive_project_summary["estimated_cost"]
) * 100


highest_overrun_project = (
    executive_project_summary
    .sort_values(
        "cost_variance",
        ascending=False
    )
    .iloc[0]
)


# ------------------------------------------------------------
# 2. BIGGEST COST DRIVER
# ------------------------------------------------------------

executive_driver_summary = (
    filtered_df
    .groupby(
        [
            "category",
            "subcategory"
        ]
    )
    .agg(
        estimated_cost=("estimated_cost", "sum"),
        actual_cost=("actual_cost", "sum")
    )
    .reset_index()
)


executive_driver_summary["cost_variance"] = (
    executive_driver_summary["actual_cost"]
    - executive_driver_summary["estimated_cost"]
)


biggest_cost_driver = (
    executive_driver_summary
    .sort_values(
        "cost_variance",
        ascending=False
    )
    .iloc[0]
)


# ------------------------------------------------------------
# 3. HIGHEST VARIANCE CATEGORY
# ------------------------------------------------------------

executive_category_summary = (
    filtered_df
    .groupby("category")
    .agg(
        estimated_cost=("estimated_cost", "sum"),
        actual_cost=("actual_cost", "sum")
    )
    .reset_index()
)


executive_category_summary["cost_variance"] = (
    executive_category_summary["actual_cost"]
    - executive_category_summary["estimated_cost"]
)


executive_category_summary["variance_pct"] = (
    executive_category_summary["cost_variance"]
    / executive_category_summary["estimated_cost"]
) * 100


highest_variance_category = (
    executive_category_summary
    .sort_values(
        "variance_pct",
        ascending=False
    )
    .iloc[0]
)


# ------------------------------------------------------------
# 4. QUANTITY VS UNIT-COST DRIVER
# ------------------------------------------------------------

average_quantity_variance = (
    filtered_df["quantity_variance_pct"].mean()
)


average_unit_cost_variance = (
    filtered_df["unit_cost_variance_pct"].mean()
)


if average_quantity_variance > average_unit_cost_variance:

    primary_variance_driver = "Quantity / Usage"

else:

    primary_variance_driver = "Unit Cost / Price"


# ------------------------------------------------------------
# DISPLAY EXECUTIVE INSIGHT CARDS
# ------------------------------------------------------------

insight_col1, insight_col2 = st.columns(2)


with insight_col1:

    st.info(
        f"""
        **Largest Project Overrun**

        {highest_overrun_project['project_id']} -
        {highest_overrun_project['project_name']}

        Cost overrun:
        ${highest_overrun_project['cost_variance']:,.0f}

        Variance:
        {highest_overrun_project['variance_pct']:.2f}%
        """
    )


with insight_col2:

    st.info(
        f"""
        **Largest Cost Driver**

        {biggest_cost_driver['category']} -
        {biggest_cost_driver['subcategory']}

        Cost variance:
        ${biggest_cost_driver['cost_variance']:,.0f}
        """
    )


insight_col3, insight_col4 = st.columns(2)


with insight_col3:

    st.info(
        f"""
        **Highest Variance Category**

        {highest_variance_category['category']}

        Variance:
        {highest_variance_category['variance_pct']:.2f}%

        Cost impact:
        ${highest_variance_category['cost_variance']:,.0f}
        """
    )


with insight_col4:

    st.info(
        f"""
        **Primary Variance Driver**

        {primary_variance_driver}

        Average quantity variance:
        {average_quantity_variance:.2f}%

        Average unit-cost variance:
        {average_unit_cost_variance:.2f}%
        """
    )


st.divider()

# ============================================================
# ANOMALY & RISK MONITORING
# ============================================================

st.subheader("Anomaly & Risk Monitoring")


if not anomaly_df.empty:

    # --------------------------------------------------------
    # APPLY RELEVANT DASHBOARD FILTERS
    # --------------------------------------------------------

    filtered_anomaly_df = anomaly_df[
        anomaly_df["location"].isin(
            selected_locations
        )
        & anomaly_df["project_type"].isin(
            selected_project_types
        )
        & anomaly_df["complexity"].isin(
            selected_complexities
        )
        & anomaly_df["project_id"].isin(
            selected_project_ids
        )
    ].copy()


    # --------------------------------------------------------
    # ANOMALY KPI CALCULATIONS
    # --------------------------------------------------------

    total_ml_projects = len(
        filtered_anomaly_df
    )


    anomaly_count = (
        filtered_anomaly_df[
            "anomaly_status"
        ]
        .eq("Anomaly")
        .sum()
    )


    normal_count = (
        filtered_anomaly_df[
            "anomaly_status"
        ]
        .eq("Normal")
        .sum()
    )


    if total_ml_projects > 0:

        anomaly_rate = (
            anomaly_count
            / total_ml_projects
        ) * 100

    else:

        anomaly_rate = 0


    # --------------------------------------------------------
    # DISPLAY ML KPI CARDS
    # --------------------------------------------------------

    ml_col1, ml_col2, ml_col3, ml_col4 = (
        st.columns(4)
    )


    with ml_col1:

        st.metric(
            "Projects Analyzed",
            total_ml_projects
        )


    with ml_col2:

        st.metric(
            "Anomalies Detected",
            anomaly_count
        )


    with ml_col3:

        st.metric(
            "Normal Projects",
            normal_count
        )


    with ml_col4:

        st.metric(
            "Anomaly Rate",
            f"{anomaly_rate:.1f}%"
        )


    # --------------------------------------------------------
    # ANOMALY SCATTER PLOT
    # --------------------------------------------------------

    st.markdown(
        "#### Project Cost-Risk Pattern"
    )


    fig_anomaly = px.scatter(
        filtered_anomaly_df,
        x="variance_pct",
        y="max_line_variance_pct",
        color="anomaly_status",
        size="actual_cost",
        hover_name="project_name",
        hover_data={
            "project_id": True,
            "estimated_cost": ":,.0f",
            "actual_cost": ":,.0f",
            "cost_variance": ":,.0f",
            "variance_pct": ":.2f",
            "max_line_variance_pct": ":.2f",
            "anomaly_score": ":.4f",
            "actual_cost": False
        },
        labels={
            "variance_pct":
                "Overall Project Variance (%)",
            "max_line_variance_pct":
                "Largest Line-Item Variance (%)",
            "anomaly_status":
                "ML Classification"
        }
    )


    fig_anomaly.update_layout(
        xaxis_title=(
            "Overall Project Variance (%)"
        ),
        yaxis_title=(
            "Largest Line-Item Variance (%)"
        ),
        legend_title=(
            "ML Classification"
        )
    )


    st.plotly_chart(
        fig_anomaly,
        width="stretch"
    )


    # --------------------------------------------------------
    # MOST UNUSUAL PROJECTS
    # --------------------------------------------------------

    st.markdown(
        "#### Projects Flagged for Investigation"
    )


    detected_anomalies = (
        filtered_anomaly_df[
            filtered_anomaly_df[
                "anomaly_status"
            ]
            == "Anomaly"
        ]
        .sort_values(
            "anomaly_score",
            ascending=True
        )
    )


    if not detected_anomalies.empty:

        anomaly_display = (
            detected_anomalies[
                [
                    "project_id",
                    "project_name",
                    "project_type",
                    "location",
                    "complexity",
                    "estimated_cost",
                    "actual_cost",
                    "cost_variance",
                    "variance_pct",
                    "max_line_variance_pct",
                    "anomaly_score"
                ]
            ]
        )


        st.dataframe(
            anomaly_display,
            width="stretch"
        )

    else:

        st.success(
            "No anomalous projects were detected "
            "for the current filters."
        )


else:

    st.warning(
        """
        Anomaly results were not found.

        Run:

        python ml/anomaly_detection.py

        Then refresh the dashboard.
        """
    )


st.divider()

# ============================================================
# TOP 10 PROJECTS BY COST OVERRUN
# ============================================================

st.subheader("Top 10 Projects by Cost Overrun")


project_summary = (
    filtered_df
    .groupby(
        [
            "project_id",
            "project_name"
        ]
    )
    .agg(
        estimated_cost=("estimated_cost", "sum"),
        actual_cost=("actual_cost", "sum")
    )
    .reset_index()
)


project_summary["cost_variance"] = (
    project_summary["actual_cost"]
    - project_summary["estimated_cost"]
)


project_summary["variance_pct"] = (
    project_summary["cost_variance"]
    / project_summary["estimated_cost"]
) * 100


top_projects = (
    project_summary
    .sort_values(
        "cost_variance",
        ascending=False
    )
    .head(10)
    .copy()
)


top_projects["project_label"] = (
    top_projects["project_id"]
    + " - "
    + top_projects["project_name"]
)


fig_top_projects = px.bar(
    top_projects,
    x="cost_variance",
    y="project_label",
    orientation="h",
    labels={
        "cost_variance": "Cost Overrun ($)",
        "project_label": "Project"
    },
    hover_data={
        "estimated_cost": ":,.2f",
        "actual_cost": ":,.2f",
        "variance_pct": ":.2f",
        "project_label": False
    }
)


fig_top_projects.update_layout(
    xaxis_title="Cost Overrun ($)",
    yaxis_title="",
    yaxis={
        "categoryorder": "total ascending"
    }
)


st.plotly_chart(
    fig_top_projects,
    width="stretch"
)

# ============================================================
# COST DRIVER ANALYSIS
# ============================================================

st.subheader("Top Cost Drivers")


cost_driver_summary = (
    filtered_df
    .groupby(
        [
            "category",
            "subcategory"
        ]
    )
    .agg(
        estimated_cost=("estimated_cost", "sum"),
        actual_cost=("actual_cost", "sum")
    )
    .reset_index()
)


cost_driver_summary["cost_variance"] = (
    cost_driver_summary["actual_cost"]
    - cost_driver_summary["estimated_cost"]
)


cost_driver_summary["variance_pct"] = (
    cost_driver_summary["cost_variance"]
    / cost_driver_summary["estimated_cost"]
) * 100


top_cost_drivers = (
    cost_driver_summary
    .sort_values(
        "cost_variance",
        ascending=False
    )
    .head(10)
    .copy()
)


top_cost_drivers["driver_label"] = (
    top_cost_drivers["category"]
    + " - "
    + top_cost_drivers["subcategory"]
)


fig_cost_drivers = px.bar(
    top_cost_drivers,
    x="cost_variance",
    y="driver_label",
    orientation="h",
    labels={
        "cost_variance": "Cost Variance ($)",
        "driver_label": "Cost Driver"
    },
    hover_data={
        "estimated_cost": ":,.2f",
        "actual_cost": ":,.2f",
        "variance_pct": ":.2f",
        "driver_label": False
    }
)


fig_cost_drivers.update_layout(
    xaxis_title="Cost Variance ($)",
    yaxis_title="",
    yaxis={
        "categoryorder": "total ascending"
    }
)


st.plotly_chart(
    fig_cost_drivers,
    width="stretch"
)

# ============================================================
# QUANTITY VS UNIT-COST VARIANCE
# ============================================================

st.subheader("Quantity vs. Unit-Cost Variance")


variance_driver_summary = (
    filtered_df
    .groupby("category")
    .agg(
        avg_quantity_variance_pct=(
            "quantity_variance_pct",
            "mean"
        ),
        avg_unit_cost_variance_pct=(
            "unit_cost_variance_pct",
            "mean"
        )
    )
    .reset_index()
)


# Round values for cleaner display
variance_driver_summary[
    [
        "avg_quantity_variance_pct",
        "avg_unit_cost_variance_pct"
    ]
] = variance_driver_summary[
    [
        "avg_quantity_variance_pct",
        "avg_unit_cost_variance_pct"
    ]
].round(2)


# Convert from wide format to long format
variance_driver_chart_data = (
    variance_driver_summary.melt(
        id_vars="category",
        value_vars=[
            "avg_quantity_variance_pct",
            "avg_unit_cost_variance_pct"
        ],
        var_name="variance_type",
        value_name="variance_pct"
    )
)


# Make labels easier to understand
variance_driver_chart_data["variance_type"] = (
    variance_driver_chart_data[
        "variance_type"
    ].replace(
        {
            "avg_quantity_variance_pct":
                "Quantity Variance",
            "avg_unit_cost_variance_pct":
                "Unit-Cost Variance"
        }
    )
)


# Create chart
fig_variance_drivers = px.bar(
    variance_driver_chart_data,
    x="category",
    y="variance_pct",
    color="variance_type",
    barmode="group",
    labels={
        "category": "Cost Category",
        "variance_pct": "Average Variance (%)",
        "variance_type": "Variance Driver"
    }
)


fig_variance_drivers.update_layout(
    xaxis_title="Cost Category",
    yaxis_title="Average Variance (%)",
    legend_title="",
    hovermode="x unified"
)


st.plotly_chart(
    fig_variance_drivers,
    width="stretch"
)

# ============================================================
# PROJECT DRILL-DOWN
# ============================================================

st.subheader("Project Drill-Down")


# Create project selection options from filtered data
drilldown_projects = (
    filtered_df[
        [
            "project_id",
            "project_name"
        ]
    ]
    .drop_duplicates()
    .sort_values("project_name")
)


if not drilldown_projects.empty:

    drilldown_projects["project_label"] = (
        drilldown_projects["project_id"]
        + " - "
        + drilldown_projects["project_name"]
    )


    selected_drilldown_project = st.selectbox(
        "Select a project for detailed analysis",
        options=drilldown_projects["project_label"]
    )


    selected_drilldown_project_id = (
        selected_drilldown_project.split(" - ")[0]
    )


    project_detail = filtered_df[
        filtered_df["project_id"]
        == selected_drilldown_project_id
    ].copy()


    # ========================================================
    # PROJECT-LEVEL KPI CALCULATIONS
    # ========================================================

    project_estimated_cost = (
        project_detail["estimated_cost"].sum()
    )

    project_actual_cost = (
        project_detail["actual_cost"].sum()
    )

    project_variance = (
        project_actual_cost
        - project_estimated_cost
    )


    if project_estimated_cost > 0:

        project_variance_pct = (
            project_variance
            / project_estimated_cost
        ) * 100

    else:

        project_variance_pct = 0


    # ========================================================
    # PROJECT STATUS
    # ========================================================

    if project_variance_pct > 10:

        project_status = "Over Budget"

    elif project_variance_pct > 5:

        project_status = "Watch"

    elif project_variance_pct < -5:

        project_status = "Under Budget"

    else:

        project_status = "On Budget"


    # ========================================================
    # PROJECT KPI CARDS
    # ========================================================

    project_col1, project_col2, project_col3, project_col4 = (
        st.columns(4)
    )


    with project_col1:

        st.metric(
            "Estimated Cost",
            f"${project_estimated_cost:,.0f}"
        )


    with project_col2:

        st.metric(
            "Actual Cost",
            f"${project_actual_cost:,.0f}"
        )


    with project_col3:

        st.metric(
            "Cost Variance",
            f"${project_variance:,.0f}"
        )


    with project_col4:

        st.metric(
            "Variance %",
            f"{project_variance_pct:.2f}%"
        )


    st.markdown(
        f"**Project Status:** {project_status}"
    )


    # ========================================================
    # PROJECT COST BREAKDOWN
    # ========================================================

    st.markdown("#### Cost Breakdown")


    project_cost_summary = (
        project_detail
        .groupby(
            [
                "category",
                "subcategory"
            ]
        )
        .agg(
            estimated_cost=(
                "estimated_cost",
                "sum"
            ),
            actual_cost=(
                "actual_cost",
                "sum"
            )
        )
        .reset_index()
    )


    project_cost_summary["cost_variance"] = (
        project_cost_summary["actual_cost"]
        - project_cost_summary["estimated_cost"]
    )


    project_cost_summary["variance_pct"] = (
        project_cost_summary["cost_variance"]
        / project_cost_summary["estimated_cost"]
    ) * 100


    project_cost_summary["driver_label"] = (
        project_cost_summary["category"]
        + " - "
        + project_cost_summary["subcategory"]
    )


    # ========================================================
    # PROJECT COST VARIANCE CHART
    # ========================================================

    project_cost_chart_data = (
        project_cost_summary
        .sort_values(
            "cost_variance",
            ascending=False
        )
    )


    fig_project_drilldown = px.bar(
        project_cost_chart_data,
        x="cost_variance",
        y="driver_label",
        orientation="h",
        labels={
            "cost_variance":
                "Cost Variance ($)",
            "driver_label":
                "Cost Component"
        },
        hover_data={
            "estimated_cost": ":,.2f",
            "actual_cost": ":,.2f",
            "variance_pct": ":.2f",
            "driver_label": False
        }
    )


    fig_project_drilldown.update_layout(
        xaxis_title="Cost Variance ($)",
        yaxis_title="",
        yaxis={
            "categoryorder":
                "total ascending"
        }
    )


    st.plotly_chart(
        fig_project_drilldown,
        width="stretch"
    )


    # ========================================================
    # PROJECT DETAIL TABLE
    # ========================================================

    with st.expander(
        "View project cost details"
    ):

        project_display_table = (
            project_cost_summary[
                [
                    "category",
                    "subcategory",
                    "estimated_cost",
                    "actual_cost",
                    "cost_variance",
                    "variance_pct"
                ]
            ]
            .sort_values(
                "cost_variance",
                ascending=False
            )
        )


        st.dataframe(
            project_display_table,
            width="stretch"
        )


else:

    st.info(
        "No projects match the current dashboard filters."
    )

# ============================================================
# PROJECT-LEVEL BUDGET STATUS SUMMARY
# ============================================================

st.subheader("Project Budget Status")


project_status_summary = (
    filtered_df
    .groupby(
        [
            "project_id",
            "project_name"
        ]
    )
    .agg(
        estimated_cost=("estimated_cost", "sum"),
        actual_cost=("actual_cost", "sum")
    )
    .reset_index()
)


project_status_summary["cost_variance"] = (
    project_status_summary["actual_cost"]
    - project_status_summary["estimated_cost"]
)


project_status_summary["variance_pct"] = (
    project_status_summary["cost_variance"]
    / project_status_summary["estimated_cost"]
) * 100


def classify_project_status(variance_pct):

    if variance_pct > 10:
        return "Over Budget"

    elif variance_pct > 5:
        return "Watch"

    elif variance_pct < -5:
        return "Under Budget"

    else:
        return "On Budget"


project_status_summary["project_status"] = (
    project_status_summary["variance_pct"]
    .apply(classify_project_status)
)


status_counts = (
    project_status_summary[
        "project_status"
    ]
    .value_counts()
)


over_budget_projects = (
    status_counts.get(
        "Over Budget",
        0
    )
)

watch_projects = (
    status_counts.get(
        "Watch",
        0
    )
)

on_budget_projects = (
    status_counts.get(
        "On Budget",
        0
    )
)

under_budget_projects = (
    status_counts.get(
        "Under Budget",
        0
    )
)


status_col1, status_col2, status_col3, status_col4 = (
    st.columns(4)
)


with status_col1:

    st.metric(
        "Over Budget Projects",
        over_budget_projects
    )


with status_col2:

    st.metric(
        "Watch Projects",
        watch_projects
    )


with status_col3:

    st.metric(
        "On Budget Projects",
        on_budget_projects
    )


with status_col4:

    st.metric(
        "Under Budget Projects",
        under_budget_projects
    )

# ============================================================
# DATASET INFORMATION
# ============================================================

st.subheader("Dataset Overview")


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        label="Projects",
        value=filtered_df["project_id"].nunique()
    )


with col2:

    st.metric(
        label="Cost Categories",
        value=filtered_df["category"].nunique()
    )


with col3:

    st.metric(
        label="Cost Records",
        value=f"{len(df):,}"
    )


# ============================================================
# DATA PREVIEW
# ============================================================

with st.expander("View processed data"):

    st.dataframe(
    filtered_df.head(100),
    width="stretch"
)

# ============================================================
# PROJECT STATUS CHART
# ============================================================

status_chart_data = (
    project_status_summary[
        "project_status"
    ]
    .value_counts()
    .reset_index()
)


status_chart_data.columns = [
    "project_status",
    "project_count"
]


fig_project_status = px.bar(
    status_chart_data,
    x="project_status",
    y="project_count",
    labels={
        "project_status":
            "Project Status",
        "project_count":
            "Number of Projects"
    }
)


fig_project_status.update_layout(
    xaxis_title="Project Status",
    yaxis_title="Number of Projects"
)


st.plotly_chart(
    fig_project_status,
    width="stretch"
)