import pandas as pd
import streamlit as st
from pathlib import Path


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


df = load_data()


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

total_estimated_cost = df["estimated_cost"].sum()

total_actual_cost = df["actual_cost"].sum()

total_variance = (
    total_actual_cost
    - total_estimated_cost
)

overall_variance_pct = (
    total_variance
    / total_estimated_cost
) * 100


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
# DATASET INFORMATION
# ============================================================

st.subheader("Dataset Overview")


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        label="Projects",
        value=df["project_id"].nunique()
    )


with col2:

    st.metric(
        label="Cost Categories",
        value=df["category"].nunique()
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
    df.head(100),
    width="stretch"
)