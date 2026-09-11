-- =========================================================
-- CONSTRUCTION COST INTELLIGENCE
-- BUSINESS ANALYSIS QUERIES
-- =========================================================


-- 1. OVERALL COST SUMMARY
SELECT
    ROUND(SUM(estimated_cost), 2) AS total_estimated_cost,
    ROUND(SUM(actual_cost), 2) AS total_actual_cost,
    ROUND(SUM(cost_variance), 2) AS total_variance,
    ROUND(
        SUM(cost_variance) / SUM(estimated_cost) * 100,
        2
    ) AS overall_variance_pct
FROM cost_analysis;


-- =========================================================
-- 2. COST ANALYSIS BY CATEGORY
-- =========================================================

SELECT
    category,
    ROUND(SUM(estimated_cost), 2) AS estimated_cost,
    ROUND(SUM(actual_cost), 2) AS actual_cost,
    ROUND(SUM(cost_variance), 2) AS variance,
    ROUND(
        SUM(cost_variance) / SUM(estimated_cost) * 100,
        2
    ) AS variance_pct
FROM cost_analysis
GROUP BY category
ORDER BY variance DESC;


-- =========================================================
-- 3. TOP 10 PROJECTS BY DOLLAR OVERRUN
-- =========================================================

SELECT
    project_id,
    project_name,
    ROUND(SUM(estimated_cost), 2) AS estimated_cost,
    ROUND(SUM(actual_cost), 2) AS actual_cost,
    ROUND(SUM(cost_variance), 2) AS variance,
    ROUND(
        SUM(cost_variance) / SUM(estimated_cost) * 100,
        2
    ) AS variance_pct
FROM cost_analysis
GROUP BY
    project_id,
    project_name
ORDER BY variance DESC
LIMIT 10;

-- =========================================================
-- 4. TOP 10 PROJECTS BY PERCENTAGE OVERRUN
-- =========================================================

SELECT
    project_id,
    project_name,
    ROUND(SUM(estimated_cost), 2) AS estimated_cost,
    ROUND(SUM(actual_cost), 2) AS actual_cost,
    ROUND(
        SUM(cost_variance) / SUM(estimated_cost) * 100,
        2
    ) AS variance_pct
FROM cost_analysis
GROUP BY
    project_id,
    project_name
HAVING SUM(estimated_cost) > 0
ORDER BY variance_pct DESC
LIMIT 10;

-- =========================================================
-- 5. BUDGET STATUS DISTRIBUTION
-- =========================================================

SELECT
    budget_status,
    COUNT(*) AS record_count
FROM cost_analysis
GROUP BY budget_status
ORDER BY record_count DESC;


-- =========================================================
-- 6. COST ANALYSIS BY SUBCATEGORY
-- =========================================================

SELECT
    category,
    subcategory,
    ROUND(SUM(estimated_cost), 2) AS estimated_cost,
    ROUND(SUM(actual_cost), 2) AS actual_cost,
    ROUND(SUM(cost_variance), 2) AS variance,
    ROUND(
        SUM(cost_variance) / SUM(estimated_cost) * 100,
        2
    ) AS variance_pct
FROM cost_analysis
GROUP BY
    category,
    subcategory
ORDER BY variance DESC;


-- =========================================================
-- 7. OVER-BUDGET LINE ITEMS
-- =========================================================

SELECT
    project_id,
    project_name,
    category,
    subcategory,
    estimated_cost,
    actual_cost,
    cost_variance,
    cost_variance_pct
FROM cost_analysis
WHERE cost_variance_pct > 10
ORDER BY cost_variance DESC;

-- =========================================================
-- 8. PROJECT ANALYSIS BY COMPLEXITY
-- =========================================================

SELECT
    complexity,
    COUNT(DISTINCT project_id) AS project_count,
    ROUND(SUM(estimated_cost), 2) AS estimated_cost,
    ROUND(SUM(actual_cost), 2) AS actual_cost,
    ROUND(SUM(cost_variance), 2) AS variance,
    ROUND(
        SUM(cost_variance) / SUM(estimated_cost) * 100,
        2
    ) AS variance_pct
FROM cost_analysis
GROUP BY complexity
ORDER BY variance_pct DESC;


-- =========================================================
-- 9. PROJECT ANALYSIS BY LOCATION
-- =========================================================

SELECT
    location,
    COUNT(DISTINCT project_id) AS project_count,
    ROUND(SUM(estimated_cost), 2) AS estimated_cost,
    ROUND(SUM(actual_cost), 2) AS actual_cost,
    ROUND(SUM(cost_variance), 2) AS variance,
    ROUND(
        SUM(cost_variance) / SUM(estimated_cost) * 100,
        2
    ) AS variance_pct
FROM cost_analysis
GROUP BY location
ORDER BY variance DESC;


-- =========================================================
-- 10. QUANTITY VS UNIT-COST VARIANCE
-- =========================================================

SELECT
    category,
    ROUND(AVG(quantity_variance_pct), 2) AS avg_quantity_variance_pct,
    ROUND(AVG(unit_cost_variance_pct), 2) AS avg_unit_cost_variance_pct,
    ROUND(AVG(cost_variance_pct), 2) AS avg_cost_variance_pct
FROM cost_analysis
GROUP BY category
ORDER BY avg_cost_variance_pct DESC;