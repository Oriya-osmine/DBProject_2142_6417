-- ====================================================================
-- STAGE B: QUERIES - Kitchen Management System
-- ====================================================================
-- This file contains:
-- · 8 SELECT queries (4 dual approaches, 4 single)
-- · 3 UPDATE queries
-- · 3 DELETE queries
-- ====================================================================

-- ====================================================================
-- GROUP 1: SELECT QUERIES (DUAL APPROACHES)
-- ====================================================================

-- ────────────────────────────────────────────────────────────────────
-- PAIR 1: Stations Workload - Orders by Status Distribution
-- Business Need: Track pending/active orders per station to balance 
-- workload and identify bottlenecks for efficiency optimization
-- ────────────────────────────────────────────────────────────────────

-- APPROACH 1A: Using JOIN + GROUP BY (Standard SQL, explicit joins)
-- Suitable for: Clear table relationships, easy to optimize with indexes
SELECT 
    ks.station_id,
    ks.station_name,
    COUNT(ko.kitchen_order_id) as total_orders,
    SUM(CASE WHEN ko.status = 'Pending' THEN 1 ELSE 0 END) as pending_orders,
    SUM(CASE WHEN ko.status = 'In-Prep' THEN 1 ELSE 0 END) as in_prep_orders,
    SUM(CASE WHEN ko.status = 'Ready' THEN 1 ELSE 0 END) as ready_orders,
    SUM(CASE WHEN ko.status = 'Served' THEN 1 ELSE 0 END) as served_orders,
    SUM(CASE WHEN ko.status = 'Cancelled' THEN 1 ELSE 0 END) as cancelled_orders
FROM kitchen_station ks
LEFT JOIN kitchen_order ko ON ks.station_id = ko.station_id
GROUP BY ks.station_id, ks.station_name
ORDER BY pending_orders DESC, in_prep_orders DESC;

-- APPROACH 1B: Using Subqueries for each status (CTE-style clarity)
-- Suitable for: Breaking down complex logic, easier to maintain and debug
WITH status_summary AS (
    SELECT 
        station_id,
        status,
        COUNT(*) as count
    FROM kitchen_order
    GROUP BY station_id, status
)
SELECT 
    ks.station_id,
    ks.station_name,
    COALESCE(SUM(ss.count), 0) as total_orders,
    COALESCE(MAX(CASE WHEN ss.status = 'Pending' THEN ss.count END), 0) as pending_orders,
    COALESCE(MAX(CASE WHEN ss.status = 'In-Prep' THEN ss.count END), 0) as in_prep_orders,
    COALESCE(MAX(CASE WHEN ss.status = 'Ready' THEN ss.count END), 0) as ready_orders,
    COALESCE(MAX(CASE WHEN ss.status = 'Served' THEN ss.count END), 0) as served_orders,
    COALESCE(MAX(CASE WHEN ss.status = 'Cancelled' THEN ss.count END), 0) as cancelled_orders
FROM kitchen_station ks
LEFT JOIN status_summary ss ON ks.station_id = ss.station_id
GROUP BY ks.station_id, ks.station_name
ORDER BY pending_orders DESC, in_prep_orders DESC;

-- Efficiency Comparison:
-- APPROACH 1A (JOIN): Direct aggregation, single scan, better for large datasets
-- APPROACH 1B (CTE): More readable, easier to extend, similar performance with good indexes

-- ────────────────────────────────────────────────────────────────────
-- PAIR 2: Chefs with High Priority Tasks - IN vs EXISTS
-- Business Need: Identify chefs with critical-priority tasks for 
-- workload distribution and urgent task assignment
-- ────────────────────────────────────────────────────────────────────

-- APPROACH 2A: Using IN clause (Simple subquery)
-- Suitable for: Smaller result sets, when subquery returns limited rows
SELECT 
    c.chef_id,
    CONCAT(c.first_name, ' ', c.last_name) as chef_name,
    c.specialization,
    COUNT(pt.task_id) as high_priority_tasks
FROM chef c
LEFT JOIN preparation_task pt ON c.chef_id = pt.chef_id 
    AND pt.priority_level >= 4 
    AND pt.status IN ('Pending', 'In-Prep')
WHERE c.chef_id IN (
    SELECT DISTINCT chef_id
    FROM preparation_task
    WHERE priority_level >= 4 AND status IN ('Pending', 'In-Prep')
)
GROUP BY c.chef_id, c.first_name, c.last_name, c.specialization
ORDER BY high_priority_tasks DESC;

-- APPROACH 2B: Using EXISTS (Correlated subquery)
-- Suitable for: Larger datasets, EXISTS stops after finding first match
SELECT 
    c.chef_id,
    CONCAT(c.first_name, ' ', c.last_name) as chef_name,
    c.specialization,
    COUNT(pt.task_id) as high_priority_tasks
FROM chef c
LEFT JOIN preparation_task pt ON c.chef_id = pt.chef_id 
    AND pt.priority_level >= 4 
    AND pt.status IN ('Pending', 'In-Prep')
WHERE EXISTS (
    SELECT 1
    FROM preparation_task
    WHERE chef_id = c.chef_id 
    AND priority_level >= 4 
    AND status IN ('Pending', 'In-Prep')
)
GROUP BY c.chef_id, c.first_name, c.last_name, c.specialization
ORDER BY high_priority_tasks DESC;

-- Efficiency Comparison:
-- APPROACH 2A (IN): Creates temporary list, better when subquery < 1000 rows
-- APPROACH 2B (EXISTS): Stops on first match, superior for large datasets

-- ────────────────────────────────────────────────────────────────────
-- PAIR 3: Order Preparation Duration - Date Arithmetic Methods
-- Business Need: Identify slow orders for SLA compliance and process 
-- improvement analysis (by month/year breakdown)
-- ────────────────────────────────────────────────────────────────────

-- APPROACH 3A: Using EXTRACT with date arithmetic
-- Suitable for: Detailed date part analysis, easier to read
SELECT 
    ko.kitchen_order_id,
    ko.order_id,
    ks.station_name,
    ko.start_time,
    ko.finish_time,
    EXTRACT(YEAR FROM ko.start_time) as order_year,
    EXTRACT(MONTH FROM ko.start_time) as order_month,
    EXTRACT(DAY FROM ko.start_time) as order_day,
    ROUND(
        EXTRACT(EPOCH FROM (ko.finish_time - ko.start_time)) / 60.0, 
        2
    ) as preparation_minutes,
    CASE 
        WHEN ROUND(EXTRACT(EPOCH FROM (ko.finish_time - ko.start_time)) / 60.0, 2) > 60 
            THEN 'Slow (>60 min)'
        WHEN ROUND(EXTRACT(EPOCH FROM (ko.finish_time - ko.start_time)) / 60.0, 2) > 30 
            THEN 'Medium (30-60 min)'
        ELSE 'Fast (<30 min)'
    END as duration_category
FROM kitchen_order ko
JOIN kitchen_station ks ON ko.station_id = ks.station_id
WHERE ko.finish_time IS NOT NULL AND ko.status IN ('Ready', 'Served')
ORDER BY preparation_minutes DESC;

-- APPROACH 3B: Using DATE_TRUNC with interval calculation
-- Suitable for: Grouping by time periods, consistency with time zones
SELECT 
    ko.kitchen_order_id,
    ko.order_id,
    ks.station_name,
    ko.start_time,
    ko.finish_time,
    CAST(DATE_TRUNC('day', ko.start_time) AS DATE) as order_date,
    EXTRACT(YEAR FROM DATE_TRUNC('month', ko.start_time)) as order_year,
    EXTRACT(MONTH FROM DATE_TRUNC('month', ko.start_time)) as order_month,
    ROUND(
        EXTRACT(EPOCH FROM (ko.finish_time - ko.start_time)) / 60.0, 
        2
    ) as preparation_minutes,
    CASE 
        WHEN ROUND(EXTRACT(EPOCH FROM (ko.finish_time - ko.start_time)) / 60.0, 2) > 60 
            THEN 'Slow (>60 min)'
        WHEN ROUND(EXTRACT(EPOCH FROM (ko.finish_time - ko.start_time)) / 60.0, 2) > 30 
            THEN 'Medium (30-60 min)'
        ELSE 'Fast (<30 min)'
    END as duration_category
FROM kitchen_order ko
JOIN kitchen_station ks ON ko.station_id = ks.station_id
WHERE ko.finish_time IS NOT NULL AND ko.status IN ('Ready', 'Served')
ORDER BY preparation_minutes DESC;

-- Efficiency Comparison:
-- APPROACH 3A (EXTRACT): More flexible, precise control over date parts
-- APPROACH 3B (DATE_TRUNC): Better for time zone handling, consistent grouping

-- ────────────────────────────────────────────────────────────────────
-- PAIR 4: Monthly Station Workload Trends - Aggregation Methods
-- Business Need: Analyze monthly capacity per station to forecast 
-- staffing needs and prevent seasonal bottlenecks
-- ────────────────────────────────────────────────────────────────────

-- APPROACH 4A: Using GROUP BY with EXTRACT
-- Suitable for: Simple aggregations, direct date decomposition
SELECT 
    ks.station_id,
    ks.station_name,
    EXTRACT(YEAR FROM ko.start_time) as work_year,
    EXTRACT(MONTH FROM ko.start_time) as work_month,
    TO_CHAR(ko.start_time, 'YYYY-MM') as year_month,
    COUNT(DISTINCT ko.kitchen_order_id) as total_orders,
    SUM(CASE WHEN ko.status = 'Served' THEN 1 ELSE 0 END) as completed_orders,
    ROUND(
        AVG(EXTRACT(EPOCH FROM (ko.finish_time - ko.start_time)) / 60.0),
        2
    ) as avg_prep_time_minutes
FROM kitchen_order ko
JOIN kitchen_station ks ON ko.station_id = ks.station_id
WHERE ko.finish_time IS NOT NULL
GROUP BY 
    ks.station_id,
    ks.station_name,
    EXTRACT(YEAR FROM ko.start_time),
    EXTRACT(MONTH FROM ko.start_time),
    TO_CHAR(ko.start_time, 'YYYY-MM')
ORDER BY work_year DESC, work_month DESC, ks.station_id;

-- APPROACH 4B: Using GROUP BY with DATE_TRUNC
-- Suitable for: Time-period grouping, timezone-aware operations
SELECT 
    ks.station_id,
    ks.station_name,
    DATE_TRUNC('month', ko.start_time)::DATE as month_start,
    EXTRACT(YEAR FROM DATE_TRUNC('month', ko.start_time)) as work_year,
    EXTRACT(MONTH FROM DATE_TRUNC('month', ko.start_time)) as work_month,
    COUNT(DISTINCT ko.kitchen_order_id) as total_orders,
    SUM(CASE WHEN ko.status = 'Served' THEN 1 ELSE 0 END) as completed_orders,
    ROUND(
        AVG(EXTRACT(EPOCH FROM (ko.finish_time - ko.start_time)) / 60.0),
        2
    ) as avg_prep_time_minutes
FROM kitchen_order ko
JOIN kitchen_station ks ON ko.station_id = ks.station_id
WHERE ko.finish_time IS NOT NULL
GROUP BY 
    ks.station_id,
    ks.station_name,
    DATE_TRUNC('month', ko.start_time)
ORDER BY month_start DESC, ks.station_id;

-- Efficiency Comparison:
-- APPROACH 4A (EXTRACT): Multiple function calls per row, flexible output format
-- APPROACH 4B (DATE_TRUNC): Single operation, more efficient for aggregation

-- ====================================================================
-- ADDITIONAL SELECT QUERIES (Single Approach)
-- ====================================================================

-- ────────────────────────────────────────────────────────────────────
-- QUERY 5: Hygiene Inspection Scores by Station and Month
-- Business Need: Monitor hygiene compliance trends per station across 
-- time to ensure food safety standards and identify problem areas
-- ────────────────────────────────────────────────────────────────────
SELECT 
    ks.station_id,
    ks.station_name,
    EXTRACT(YEAR FROM hi.inspection_date) as inspection_year,
    EXTRACT(MONTH FROM hi.inspection_date) as inspection_month,
    COUNT(hi.inspection_id) as total_inspections,
    ROUND(AVG(hi.cleanliness_score), 2) as avg_cleanliness_score,
    MIN(hi.cleanliness_score) as min_cleanliness,
    MAX(hi.cleanliness_score) as max_cleanliness,
    ROUND(AVG(hi.temperature_check), 2) as avg_temperature_check
FROM hygiene_inspection hi
JOIN kitchen_station ks ON hi.station_id = ks.station_id
WHERE hi.inspection_date IS NOT NULL
GROUP BY 
    ks.station_id,
    ks.station_name,
    EXTRACT(YEAR FROM hi.inspection_date),
    EXTRACT(MONTH FROM hi.inspection_date)
ORDER BY inspection_year DESC, inspection_month DESC, ks.station_id;

-- ────────────────────────────────────────────────────────────────────
-- QUERY 6: Chef Productivity - Average Prep Time per Chef by Month
-- Business Need: Evaluate individual chef performance and training 
-- effectiveness through preparation time analysis over time
-- ────────────────────────────────────────────────────────────────────
SELECT 
    c.chef_id,
    CONCAT(c.first_name, ' ', c.last_name) as chef_name,
    c.specialization,
    EXTRACT(YEAR FROM fpl.prep_date) as work_year,
    EXTRACT(MONTH FROM fpl.prep_date) as work_month,
    COUNT(fpl.log_id) as total_items_prepped,
    ROUND(AVG(fpl.preparation_time), 2) as avg_prep_time_minutes,
    MIN(fpl.preparation_time) as fastest_prep,
    MAX(fpl.preparation_time) as slowest_prep
FROM food_prep_log fpl
JOIN chef c ON fpl.chef_id = c.chef_id
WHERE fpl.prep_date IS NOT NULL
GROUP BY 
    c.chef_id,
    c.first_name,
    c.last_name,
    c.specialization,
    EXTRACT(YEAR FROM fpl.prep_date),
    EXTRACT(MONTH FROM fpl.prep_date)
HAVING COUNT(fpl.log_id) > 5
ORDER BY work_year DESC, work_month DESC, avg_prep_time_minutes ASC;

-- ────────────────────────────────────────────────────────────────────
-- QUERY 7: Active Tasks by Priority - Workload Assessment
-- Business Need: Identify critical pending tasks across all chefs to 
-- support real-time dispatch and priority queue management
-- ────────────────────────────────────────────────────────────────────
SELECT 
    ko.station_id,
    ks.station_name,
    pt.task_id,
    pt.chef_id,
    CONCAT(c.first_name, ' ', c.last_name) as chef_name,
    pt.task_description,
    pt.priority_level,
    pt.status,
    ko.kitchen_order_id,
    ko.order_id,
    ko.start_time,
    ROUND(
        EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - ko.start_time)) / 60.0,
        2
    ) as minutes_elapsed
FROM preparation_task pt
JOIN kitchen_order ko ON pt.kitchen_order_id = ko.kitchen_order_id
JOIN kitchen_station ks ON ko.station_id = ks.station_id
JOIN chef c ON pt.chef_id = c.chef_id
WHERE pt.status IN ('Pending', 'In-Prep') AND pt.priority_level >= 3
ORDER BY 
    pt.priority_level DESC,
    ko.start_time ASC,
    ks.station_id;

-- ────────────────────────────────────────────────────────────────────
-- QUERY 8: Temperature Anomalies in Hygiene Inspections
-- Business Need: Detect refrigeration and cooking equipment failures 
-- or anomalies that could compromise food safety
-- ────────────────────────────────────────────────────────────────────
SELECT 
    hi.inspection_id,
    ks.station_id,
    ks.station_name,
    EXTRACT(YEAR FROM hi.inspection_date) as inspection_year,
    EXTRACT(MONTH FROM hi.inspection_date) as inspection_month,
    EXTRACT(DAY FROM hi.inspection_date) as inspection_day,
    hi.inspection_date,
    hi.temperature_check,
    hi.status,
    CONCAT(c.first_name, ' ', c.last_name) as inspector_name,
    hi.comments,
    CASE 
        WHEN hi.temperature_check < 5 THEN 'Fridge OK'
        WHEN hi.temperature_check BETWEEN 5 AND 15 THEN 'Fridge WARM - Risk'
        WHEN hi.temperature_check > 15 THEN 'Fridge HOT - Critical'
        WHEN hi.temperature_check < -15 THEN 'Freezer OK'
        ELSE 'Normal Range'
    END as temperature_alert
FROM hygiene_inspection hi
JOIN kitchen_station ks ON hi.station_id = ks.station_id
JOIN chef c ON hi.inspector_id = c.chef_id
WHERE hi.temperature_check IS NOT NULL
ORDER BY 
    CASE 
        WHEN hi.temperature_check > 15 THEN 1
        WHEN hi.temperature_check BETWEEN 5 AND 15 THEN 2
        ELSE 3
    END,
    hi.inspection_date DESC;

-- ====================================================================
-- UPDATE QUERIES
-- ====================================================================

-- ────────────────────────────────────────────────────────────────────
-- UPDATE 1: Mark Orders as Ready When All Tasks Complete
-- Business Need: Automate order status progression when all assigned 
-- tasks reach completion, triggering kitchen handoff and serving
-- ────────────────────────────────────────────────────────────────────
UPDATE kitchen_order ko
SET status = 'Ready'
WHERE ko.kitchen_order_id IN (
    SELECT DISTINCT ko2.kitchen_order_id
    FROM kitchen_order ko2
    WHERE ko2.status = 'In-Prep'
    AND NOT EXISTS (
        SELECT 1
        FROM preparation_task pt
        WHERE pt.kitchen_order_id = ko2.kitchen_order_id
        AND pt.status NOT IN ('Ready', 'Completed')
    )
)
AND ko.status = 'In-Prep';

-- ────────────────────────────────────────────────────────────────────
-- UPDATE 2: Update Chef Current Station Assignment
-- Business Need: Reassign chef to new station to optimize workload 
-- distribution based on current task allocation
-- ────────────────────────────────────────────────────────────────────
UPDATE chef 
SET current_station_id = 3
WHERE chef_id = 5 
AND current_station_id IS NOT NULL;

-- ────────────────────────────────────────────────────────────────────
-- UPDATE 3: Set Next Hygiene Inspection Date (7 days after current)
-- Business Need: Automatically schedule next inspection to maintain 
-- consistent food safety audit intervals
-- ────────────────────────────────────────────────────────────────────
UPDATE hygiene_inspection
SET next_inspection_date = inspection_date + INTERVAL '7 days'
WHERE next_inspection_date IS NULL 
AND inspection_date IS NOT NULL
AND EXTRACT(MONTH FROM inspection_date) = 2;

-- ====================================================================
-- DELETE QUERIES
-- ====================================================================

-- ────────────────────────────────────────────────────────────────────
-- DELETE 1: Remove Cancelled Orders Older Than 90 Days
-- Business Need: Archive/clean obsolete cancelled orders to reduce 
-- database bloat and improve query performance on active orders
-- ────────────────────────────────────────────────────────────────────
DELETE FROM preparation_task
WHERE kitchen_order_id IN (
    SELECT kitchen_order_id
    FROM kitchen_order
    WHERE status = 'Cancelled' 
    AND start_time < (CURRENT_DATE - INTERVAL '90 days')
);

-- ────────────────────────────────────────────────────────────────────
-- DELETE 2: Remove Duplicate Food Prep Logs (Keep Earliest)
-- Business Need: Clean duplicate entries from data import errors while 
-- preserving the first/original log entry
-- ────────────────────────────────────────────────────────────────────
DELETE FROM food_prep_log fpl
WHERE log_id NOT IN (
    SELECT MIN(log_id)
    FROM food_prep_log
    GROUP BY chef_id, menu_item_id, prep_date
);

-- ────────────────────────────────────────────────────────────────────
-- DELETE 3: Remove Tasks for Cancelled Orders
-- Business Need: Clean up orphaned task records for cancelled orders 
-- to maintain referential integrity and reduce clutter
-- ────────────────────────────────────────────────────────────────────
DELETE FROM preparation_task
WHERE kitchen_order_id IN (
    SELECT kitchen_order_id
    FROM kitchen_order
    WHERE status = 'Cancelled'
    AND finish_time < (CURRENT_DATE - INTERVAL '60 days')
);

-- ====================================================================
-- End of Queries.sql
-- ====================================================================
