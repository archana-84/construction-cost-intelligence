import pandas as pd
import sqlite3
from pathlib import Path

# -----------------------------
# Project paths
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"


# -----------------------------
# Load datasets
# -----------------------------
projects = pd.read_csv(RAW_DATA_DIR / "projects.csv")
cost_codes = pd.read_csv(RAW_DATA_DIR / "cost_codes.csv")
estimates = pd.read_csv(RAW_DATA_DIR / "estimates.csv")
actual_costs = pd.read_csv(RAW_DATA_DIR / "actual_costs.csv")
project_variance = pd.read_csv(RAW_DATA_DIR / "project_variance.csv")


# -----------------------------
# Basic dataset information
# -----------------------------
datasets = {
    "projects": projects,
    "cost_codes": cost_codes,
    "estimates": estimates,
    "actual_costs": actual_costs,
    "project_variance": project_variance,
}


print("\n=== DATASET SHAPES ===")

for name, df in datasets.items():
    print(f"{name}: {df.shape}")


print("\n=== COLUMN NAMES ===")

for name, df in datasets.items():
    print(f"\n{name}")
    print(df.columns.tolist())


print("\n=== MISSING VALUES ===")

for name, df in datasets.items():
    print(f"\n{name}")
    print(df.isnull().sum())


print("\n=== DUPLICATE ROWS ===")

for name, df in datasets.items():
    duplicate_count = df.duplicated().sum()
    print(f"{name}: {duplicate_count}")


print("\n=== FIRST 5 PROJECTS ===")
print(projects.head())


print("\n=== FIRST 5 ESTIMATES ===")
print(estimates.head())


print("\n=== FIRST 5 ACTUAL COST RECORDS ===")
print(actual_costs.head())


print("\n=== FIRST 5 VARIANCE RECORDS ===")
print(project_variance.head())



# ============================================================
# DATA RELATIONSHIP VALIDATION
# ============================================================

print("\n=== RELATIONSHIP VALIDATION ===")


# 1. Check unique project IDs
print(f"Unique projects in projects table: {projects['project_id'].nunique()}")
print(f"Unique projects in estimates table: {estimates['project_id'].nunique()}")
print(f"Unique projects in actual costs table: {actual_costs['project_id'].nunique()}")


# 2. Check for invalid project IDs in estimates
invalid_estimate_projects = set(estimates["project_id"]) - set(projects["project_id"])

print(
    f"Invalid project IDs in estimates: "
    f"{len(invalid_estimate_projects)}"
)


# 3. Check for invalid project IDs in actual costs
invalid_actual_projects = set(actual_costs["project_id"]) - set(projects["project_id"])

print(
    f"Invalid project IDs in actual costs: "
    f"{len(invalid_actual_projects)}"
)


# 4. Check cost codes
invalid_estimate_codes = set(estimates["cost_code"]) - set(cost_codes["cost_code"])

invalid_actual_codes = set(actual_costs["cost_code"]) - set(cost_codes["cost_code"])

print(
    f"Invalid cost codes in estimates: "
    f"{len(invalid_estimate_codes)}"
)

print(
    f"Invalid cost codes in actual costs: "
    f"{len(invalid_actual_codes)}"
)


# 5. Check estimate-to-actual matching
estimate_keys = set(
    zip(
        estimates["project_id"],
        estimates["cost_code"]
    )
)

actual_keys = set(
    zip(
        actual_costs["project_id"],
        actual_costs["cost_code"]
    )
)

missing_actuals = estimate_keys - actual_keys
missing_estimates = actual_keys - estimate_keys

print(
    f"Estimate records without matching actual records: "
    f"{len(missing_actuals)}"
)

print(
    f"Actual records without matching estimate records: "
    f"{len(missing_estimates)}"
)


# 6. Check expected number of project-cost combinations
expected_combinations = len(projects) * len(cost_codes)

print(f"Expected project-cost combinations: {expected_combinations}")
print(f"Actual estimate records: {len(estimates)}")
print(f"Actual cost records: {len(actual_costs)}")


# 7. Overall validation result
validation_passed = (
    len(invalid_estimate_projects) == 0
    and len(invalid_actual_projects) == 0
    and len(invalid_estimate_codes) == 0
    and len(invalid_actual_codes) == 0
    and len(missing_actuals) == 0
    and len(missing_estimates) == 0
)

if validation_passed:
    print("\nDATA RELATIONSHIP VALIDATION: PASSED")
else:
    print("\nDATA RELATIONSHIP VALIDATION: FAILED")

# ============================================================
# DATA TYPE AND BUSINESS-RULE VALIDATION
# ============================================================

print("\n=== DATA TYPE AND BUSINESS-RULE VALIDATION ===")


# 1. Convert date columns
projects["start_date"] = pd.to_datetime(
    projects["start_date"],
    errors="coerce"
)

projects["end_date"] = pd.to_datetime(
    projects["end_date"],
    errors="coerce"
)


# 2. Check invalid dates
invalid_start_dates = projects["start_date"].isna().sum()
invalid_end_dates = projects["end_date"].isna().sum()

print(f"Invalid start dates: {invalid_start_dates}")
print(f"Invalid end dates: {invalid_end_dates}")


# 3. Check end date is after start date
invalid_date_order = (
    projects["end_date"] < projects["start_date"]
).sum()

print(
    f"Projects with end date before start date: "
    f"{invalid_date_order}"
)


# 4. Check duration
invalid_duration = (
    projects["duration_days"] <= 0
).sum()

print(
    f"Projects with invalid duration: "
    f"{invalid_duration}"
)


# 5. Check project size
invalid_project_size = (
    projects["project_size_sqft"] <= 0
).sum()

print(
    f"Projects with invalid project size: "
    f"{invalid_project_size}"
)


# 6. Check complexity categories
valid_complexity = {"Low", "Medium", "High"}

invalid_complexity = (
    ~projects["complexity"].isin(valid_complexity)
).sum()

print(
    f"Projects with invalid complexity: "
    f"{invalid_complexity}"
)


# 7. Validate estimates
invalid_estimated_quantity = (
    estimates["estimated_quantity"] <= 0
).sum()

invalid_estimated_unit_cost = (
    estimates["estimated_unit_cost"] <= 0
).sum()

invalid_estimated_cost = (
    estimates["estimated_cost"] <= 0
).sum()

print(
    f"Invalid estimated quantities: "
    f"{invalid_estimated_quantity}"
)

print(
    f"Invalid estimated unit costs: "
    f"{invalid_estimated_unit_cost}"
)

print(
    f"Invalid estimated costs: "
    f"{invalid_estimated_cost}"
)


# 8. Validate actual costs
invalid_actual_quantity = (
    actual_costs["actual_quantity"] <= 0
).sum()

invalid_actual_unit_cost = (
    actual_costs["actual_unit_cost"] <= 0
).sum()

invalid_actual_cost = (
    actual_costs["actual_cost"] <= 0
).sum()

print(
    f"Invalid actual quantities: "
    f"{invalid_actual_quantity}"
)

print(
    f"Invalid actual unit costs: "
    f"{invalid_actual_unit_cost}"
)

print(
    f"Invalid actual costs: "
    f"{invalid_actual_cost}"
)


# 9. Verify variance calculation
calculated_variance = (
    project_variance["actual_cost"]
    - project_variance["estimated_cost"]
)

variance_difference = (
    calculated_variance
    - project_variance["variance"]
).abs()

incorrect_variance = (
    variance_difference > 0.01
).sum()

print(
    f"Incorrect variance calculations: "
    f"{incorrect_variance}"
)


# 10. Verify variance percentage
calculated_variance_pct = (
    calculated_variance
    / project_variance["estimated_cost"]
) * 100

variance_pct_difference = (
    calculated_variance_pct
    - project_variance["variance_pct"]
).abs()

incorrect_variance_pct = (
    variance_pct_difference > 0.01
).sum()

print(
    f"Incorrect variance percentage calculations: "
    f"{incorrect_variance_pct}"
)


# 11. Final business-rule validation
business_rules_passed = all([
    invalid_start_dates == 0,
    invalid_end_dates == 0,
    invalid_date_order == 0,
    invalid_duration == 0,
    invalid_project_size == 0,
    invalid_complexity == 0,
    invalid_estimated_quantity == 0,
    invalid_estimated_unit_cost == 0,
    invalid_estimated_cost == 0,
    invalid_actual_quantity == 0,
    invalid_actual_unit_cost == 0,
    invalid_actual_cost == 0,
    incorrect_variance == 0,
    incorrect_variance_pct == 0,
])


if business_rules_passed:
    print("\nBUSINESS-RULE VALIDATION: PASSED")
else:
    print("\nBUSINESS-RULE VALIDATION: FAILED")

# ============================================================
# BUILD PROCESSED ANALYTICAL DATASET
# ============================================================

print("\n=== BUILDING PROCESSED DATASET ===")


# Merge estimated costs with actual costs
processed_data = estimates.merge(
    actual_costs,
    on=[
        "project_id",
        "cost_code",
        "category",
        "subcategory",
        "unit"
    ],
    how="inner"
)


# Add project-level information
processed_data = processed_data.merge(
    projects[
        [
            "project_id",
            "project_name",
            "project_type",
            "location",
            "start_date",
            "end_date",
            "duration_days",
            "project_size_sqft",
            "complexity"
        ]
    ],
    on="project_id",
    how="left"
)


# Calculate cost variance
processed_data["cost_variance"] = (
    processed_data["actual_cost"]
    - processed_data["estimated_cost"]
)


# Calculate cost variance percentage
processed_data["cost_variance_pct"] = (
    processed_data["cost_variance"]
    / processed_data["estimated_cost"]
) * 100


# Calculate quantity variance
processed_data["quantity_variance"] = (
    processed_data["actual_quantity"]
    - processed_data["estimated_quantity"]
)


# Calculate quantity variance percentage
processed_data["quantity_variance_pct"] = (
    processed_data["quantity_variance"]
    / processed_data["estimated_quantity"]
) * 100


# Calculate unit-cost variance
processed_data["unit_cost_variance"] = (
    processed_data["actual_unit_cost"]
    - processed_data["estimated_unit_cost"]
)


# Calculate unit-cost variance percentage
processed_data["unit_cost_variance_pct"] = (
    processed_data["unit_cost_variance"]
    / processed_data["estimated_unit_cost"]
) * 100


# Create budget-status classification
processed_data["budget_status"] = "On Budget"

processed_data.loc[
    processed_data["cost_variance_pct"] > 10,
    "budget_status"
] = "Over Budget"

processed_data.loc[
    (processed_data["cost_variance_pct"] > 5)
    & (processed_data["cost_variance_pct"] <= 10),
    "budget_status"
] = "Watch"

processed_data.loc[
    processed_data["cost_variance_pct"] < -5,
    "budget_status"
] = "Under Budget"


# Round analytical values
columns_to_round = [
    "cost_variance",
    "cost_variance_pct",
    "quantity_variance_pct",
    "unit_cost_variance",
    "unit_cost_variance_pct"
]

processed_data[columns_to_round] = (
    processed_data[columns_to_round].round(2)
)


# Create processed-data directory if necessary
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

PROCESSED_DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# Save analytical dataset
output_file = (
    PROCESSED_DATA_DIR
    / "construction_cost_analysis.csv"
)

processed_data.to_csv(
    output_file,
    index=False
)


print(
    f"Processed dataset created successfully: "
    f"{output_file}"
)

print(
    f"Processed dataset shape: "
    f"{processed_data.shape}"
)


print("\n=== PROCESSED DATA SAMPLE ===")

print(
    processed_data[
        [
            "project_id",
            "category",
            "subcategory",
            "estimated_cost",
            "actual_cost",
            "cost_variance",
            "cost_variance_pct",
            "budget_status"
        ]
    ].head(10)
)


# ============================================================
# ANALYTICAL SUMMARY AND SANITY CHECKS
# ============================================================

print("\n=== ANALYTICAL SUMMARY ===")


# Overall cost metrics
total_estimated_cost = processed_data["estimated_cost"].sum()
total_actual_cost = processed_data["actual_cost"].sum()

total_cost_variance = (
    total_actual_cost - total_estimated_cost
)

overall_variance_pct = (
    total_cost_variance / total_estimated_cost
) * 100


print(f"Total Estimated Cost: ${total_estimated_cost:,.2f}")
print(f"Total Actual Cost: ${total_actual_cost:,.2f}")
print(f"Total Cost Variance: ${total_cost_variance:,.2f}")
print(f"Overall Variance %: {overall_variance_pct:.2f}%")


# ============================================================
# BUDGET STATUS DISTRIBUTION
# ============================================================

print("\n=== BUDGET STATUS DISTRIBUTION ===")

budget_distribution = (
    processed_data["budget_status"]
    .value_counts()
)

print(budget_distribution)


# ============================================================
# CATEGORY-LEVEL ANALYSIS
# ============================================================

print("\n=== COST ANALYSIS BY CATEGORY ===")

category_summary = (
    processed_data
    .groupby("category")
    .agg(
        estimated_cost=("estimated_cost", "sum"),
        actual_cost=("actual_cost", "sum")
    )
    .reset_index()
)


category_summary["variance"] = (
    category_summary["actual_cost"]
    - category_summary["estimated_cost"]
)


category_summary["variance_pct"] = (
    category_summary["variance"]
    / category_summary["estimated_cost"]
) * 100


category_summary[
    [
        "estimated_cost",
        "actual_cost",
        "variance",
        "variance_pct"
    ]
] = category_summary[
    [
        "estimated_cost",
        "actual_cost",
        "variance",
        "variance_pct"
    ]
].round(2)


print(category_summary)


# ============================================================
# PROJECT-LEVEL ANALYSIS
# ============================================================

print("\n=== TOP 10 PROJECTS BY COST OVERRUN ===")

project_summary = (
    processed_data
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


project_summary["variance"] = (
    project_summary["actual_cost"]
    - project_summary["estimated_cost"]
)


project_summary["variance_pct"] = (
    project_summary["variance"]
    / project_summary["estimated_cost"]
) * 100


project_summary = project_summary.sort_values(
    "variance",
    ascending=False
)


print(
    project_summary[
        [
            "project_id",
            "project_name",
            "estimated_cost",
            "actual_cost",
            "variance",
            "variance_pct"
        ]
    ].head(10)
)


# ============================================================
# FINAL DATASET SANITY CHECK
# ============================================================

print("\n=== FINAL SANITY CHECK ===")


checks = {
    "Processed dataset contains records":
        len(processed_data) > 0,

    "No missing project IDs":
        processed_data["project_id"].isna().sum() == 0,

    "No missing cost codes":
        processed_data["cost_code"].isna().sum() == 0,

    "No missing estimated costs":
        processed_data["estimated_cost"].isna().sum() == 0,

    "No missing actual costs":
        processed_data["actual_cost"].isna().sum() == 0,

    "No zero/negative estimated costs":
        (processed_data["estimated_cost"] <= 0).sum() == 0,

    "No zero/negative actual costs":
        (processed_data["actual_cost"] <= 0).sum() == 0
}


for check_name, result in checks.items():

    status = "PASS" if result else "FAIL"

    print(f"{status}: {check_name}")


all_checks_passed = all(checks.values())


if all_checks_passed:
    print("\nFINAL DATASET VALIDATION: PASSED")
else:
    print("\nFINAL DATASET VALIDATION: FAILED")


# ============================================================
# LOAD DATA INTO SQLITE DATABASE
# ============================================================

print("\n=== CREATING SQLITE DATABASE ===")


# Database directory
DATABASE_DIR = BASE_DIR / "database"

DATABASE_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# Database file
DATABASE_PATH = (
    DATABASE_DIR / "construction.db"
)


# Create database connection
connection = sqlite3.connect(
    DATABASE_PATH
)


# ============================================================
# LOAD TABLES
# ============================================================

projects.to_sql(
    "projects",
    connection,
    if_exists="replace",
    index=False
)


cost_codes.to_sql(
    "cost_codes",
    connection,
    if_exists="replace",
    index=False
)


estimates.to_sql(
    "estimates",
    connection,
    if_exists="replace",
    index=False
)


actual_costs.to_sql(
    "actual_costs",
    connection,
    if_exists="replace",
    index=False
)


processed_data.to_sql(
    "cost_analysis",
    connection,
    if_exists="replace",
    index=False
)


# ============================================================
# VERIFY DATABASE TABLES
# ============================================================

tables = pd.read_sql_query(
    """
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name;
    """,
    connection
)


print("\nDatabase tables:")

print(tables)


# ============================================================
# VERIFY RECORD COUNTS
# ============================================================

print("\n=== DATABASE RECORD COUNTS ===")


table_names = [
    "projects",
    "cost_codes",
    "estimates",
    "actual_costs",
    "cost_analysis"
]


for table_name in table_names:

    query = f"""
    SELECT COUNT(*) AS record_count
    FROM {table_name};
    """

    result = pd.read_sql_query(
        query,
        connection
    )

    record_count = result.loc[
        0,
        "record_count"
    ]

    print(
        f"{table_name}: "
        f"{record_count} records"
    )


# Close database connection
connection.close()


print(
    f"\nSQLite database created successfully: "
    f"{DATABASE_PATH}"
)