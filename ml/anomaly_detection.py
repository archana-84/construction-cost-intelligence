import pandas as pd
from pathlib import Path
from sklearn.ensemble import IsolationForest


# ============================================================
# FILE PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "construction_cost_analysis.csv"
)

OUTPUT_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "project_anomalies.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(DATA_PATH)

print("Dataset loaded successfully.")
print(f"Rows: {len(df):,}")


# ============================================================
# CREATE PROJECT-LEVEL FEATURES
# ============================================================

project_features = (
    df
    .groupby(
        [
            "project_id",
            "project_name",
            "project_type",
            "location",
            "complexity"
        ]
    )
    .agg(
        estimated_cost=("estimated_cost", "sum"),
        actual_cost=("actual_cost", "sum"),

        avg_quantity_variance_pct=(
            "quantity_variance_pct",
            "mean"
        ),

        avg_unit_cost_variance_pct=(
            "unit_cost_variance_pct",
            "mean"
        ),

        max_line_variance_pct=(
            "cost_variance_pct",
            "max"
        )
    )
    .reset_index()
)


# ============================================================
# CALCULATE PROJECT COST VARIANCE
# ============================================================

project_features["cost_variance"] = (
    project_features["actual_cost"]
    - project_features["estimated_cost"]
)


project_features["variance_pct"] = (
    project_features["cost_variance"]
    / project_features["estimated_cost"]
) * 100


print(
    f"Unique projects: "
    f"{len(project_features):,}"
)


# ============================================================
# SELECT MACHINE-LEARNING FEATURES
# ============================================================

ml_features = [
    "variance_pct",
    "avg_quantity_variance_pct",
    "avg_unit_cost_variance_pct",
    "max_line_variance_pct"
]


X = project_features[ml_features]


print("\nFeatures used by the model:")

for feature in ml_features:
    print(f"- {feature}")


# ============================================================
# BUILD ISOLATION FOREST MODEL
# ============================================================

model = IsolationForest(
    n_estimators=200,
    contamination=0.05,
    random_state=42
)


# ============================================================
# TRAIN MODEL AND GENERATE PREDICTIONS
# ============================================================

project_features["anomaly_prediction"] = (
    model.fit_predict(X)
)


project_features["anomaly_score"] = (
    model.decision_function(X)
)


# Isolation Forest returns:
#
#  1  = normal
# -1  = anomaly

project_features["anomaly_status"] = (
    project_features[
        "anomaly_prediction"
    ]
    .map(
        {
            1: "Normal",
            -1: "Anomaly"
        }
    )
)


# ============================================================
# COUNT RESULTS
# ============================================================

normal_projects = (
    project_features[
        "anomaly_status"
    ]
    .eq("Normal")
    .sum()
)


anomalous_projects = (
    project_features[
        "anomaly_status"
    ]
    .eq("Anomaly")
    .sum()
)


print("\nMODEL RESULTS")
print("=" * 50)

print(
    f"Normal projects: "
    f"{normal_projects}"
)

print(
    f"Anomalous projects: "
    f"{anomalous_projects}"
)


# ============================================================
# DISPLAY MOST UNUSUAL PROJECTS
# ============================================================

anomaly_results = (
    project_features[
        project_features[
            "anomaly_status"
        ]
        == "Anomaly"
    ]
    .sort_values(
        "anomaly_score",
        ascending=True
    )
)


print(
    "\nMOST UNUSUAL PROJECTS"
)

print("=" * 50)


print(
    anomaly_results[
        [
            "project_id",
            "project_name",
            "estimated_cost",
            "actual_cost",
            "cost_variance",
            "variance_pct",
            "avg_quantity_variance_pct",
            "avg_unit_cost_variance_pct",
            "max_line_variance_pct",
            "anomaly_score"
        ]
    ]
    .head(15)
    .to_string(
        index=False
    )
)


# ============================================================
# SAVE RESULTS
# ============================================================

project_features.to_csv(
    OUTPUT_PATH,
    index=False
)


print(
    f"\nAnomaly results saved to:\n"
    f"{OUTPUT_PATH}"
)