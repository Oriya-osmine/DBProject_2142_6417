-- ====================================================================
-- STAGE B: CONSTRAINTS - Additional Business Rules & Data Integrity
-- ====================================================================
-- This file adds additional constraints to enforce data quality and
-- business logic rules using ALTER TABLE commands. Each constraint
-- includes a demonstration of violation attempt.
-- ====================================================================

-- ====================================================================
-- CONSTRAINT 1: Kitchen Orders - Finish Time Must Be After Start Time
-- Business Rule: No order can be marked as finished before it started;
-- ensures chronological integrity and prevents data entry errors
-- ====================================================================

ALTER TABLE kitchen_order
ADD CONSTRAINT check_finish_after_start 
CHECK (finish_time IS NULL OR finish_time >= start_time);

-- Demonstration: Attempt to insert order with finish_time before start_time
-- Expected: ERROR - violation of CHECK constraint
INSERT INTO kitchen_order (order_id, status, start_time, finish_time, station_id)
VALUES (99999, 'Served', '2026-01-20 10:00:00', '2026-01-20 09:00:00', 5);
-- ↑ This will fail: finish_time (09:00) < start_time (10:00)

-- ====================================================================
-- CONSTRAINT 2: Food Prep Log - Preparation Time Must Be Positive
-- Business Rule: No item can have negative or zero preparation time;
-- ensures realistic and measurable cooking durations
-- ====================================================================

ALTER TABLE food_prep_log
ADD CONSTRAINT check_positive_prep_time 
CHECK (preparation_time > 0);

-- Demonstration: Attempt to insert log with zero preparation time
-- Expected: ERROR - violation of CHECK constraint
INSERT INTO food_prep_log (chef_id, menu_item_id, preparation_time, prep_date, notes)
VALUES (15, 50, 0, '2026-03-01', 'Invalid zero time');
-- ↑ This will fail: preparation_time must be > 0

-- ====================================================================
-- CONSTRAINT 3: Hygiene Inspection - Next Inspection Must Be After Current
-- Business Rule: Next scheduled inspection cannot be before current inspection;
-- prevents scheduling conflicts and ensures proper audit intervals
-- ====================================================================

ALTER TABLE hygiene_inspection
ADD CONSTRAINT check_next_inspection_date 
CHECK (next_inspection_date IS NULL OR next_inspection_date > inspection_date);

-- Demonstration: Attempt to set next inspection before current inspection
-- Expected: ERROR - violation of CHECK constraint
UPDATE hygiene_inspection
SET next_inspection_date = inspection_date - INTERVAL '1 day'
WHERE inspection_id = 1;
-- ↑ This will fail: next_inspection_date cannot be before inspection_date

-- ====================================================================
-- CONSTRAINT 4: Preparation Task - Valid Status Values
-- Business Rule: Tasks can only have predefined status values;
-- prevents invalid workflow states and ensures consistent tracking
-- ====================================================================

ALTER TABLE preparation_task
ADD CONSTRAINT check_valid_task_status 
CHECK (status IN ('Pending', 'In-Prep', 'Ready', 'Completed', 'Cancelled'));

-- Demonstration: Attempt to insert task with invalid status
-- Expected: ERROR - violation of CHECK constraint
INSERT INTO preparation_task (kitchen_order_id, chef_id, task_description, status, priority_level)
VALUES (100, 25, 'Test task', 'InvalidStatus', 3);
-- ↑ This will fail: 'InvalidStatus' is not in allowed values

-- ====================================================================
-- CONSTRAINT 5: Kitchen Station - Station Name Must Be Unique
-- Business Rule: No two stations can have identical names;
-- prevents confusion and ensures unique station identification
-- ====================================================================

ALTER TABLE kitchen_station
ADD CONSTRAINT unique_station_name 
UNIQUE (station_name);

-- Demonstration: Attempt to insert station with duplicate name
-- First, check existing station name:
SELECT station_name FROM kitchen_station LIMIT 1;
-- Then try to insert duplicate (example - adjust name based on actual stations):
-- Expected: ERROR - violation of UNIQUE constraint
INSERT INTO kitchen_station (station_name, description, is_active)
VALUES ('Grill Station', 'Duplicate station (will fail)', TRUE);
-- ↑ This will fail if 'Grill Station' already exists

-- ====================================================================
-- CONSTRAINT 6: Chef - Hire Date Cannot Be in Future
-- Business Rule: Chef hire_date must be in the past or today;
-- prevents data entry errors and maintains realistic employment records
-- ====================================================================

ALTER TABLE chef
ADD CONSTRAINT check_hire_date_not_future 
CHECK (hire_date <= CURRENT_DATE);

-- Demonstration: Attempt to insert chef with future hire date
-- Expected: ERROR - violation of CHECK constraint
INSERT INTO chef (first_name, last_name, specialization, hire_date, current_station_id, is_on_shift)
VALUES ('John', 'FutureChef', 'Pastry Chef', '2099-12-31', 1, FALSE);
-- ↑ This will fail: hire_date is in the future

-- ====================================================================
-- CONSTRAINT 7: Preparation Task - Priority Level Already Constrained
-- Note: This constraint already exists in the base schema (CHECK priority_level BETWEEN 1 AND 5)
-- Demonstration: Attempt to insert task with invalid priority level
-- Expected: ERROR - violation of CHECK constraint
INSERT INTO preparation_task (kitchen_order_id, chef_id, task_description, status, priority_level)
VALUES (100, 25, 'Test task', 'Pending', 99);
-- ↑ This will fail: priority_level must be BETWEEN 1 AND 5

-- ====================================================================
-- CONSTRAINT 8: Hygiene Inspection - Cleanliness Score Range
-- Note: This constraint already exists in base schema (CHECK between 1.0 and 10.0)
-- Demonstration: Attempt to insert inspection with invalid cleanliness score
-- Expected: ERROR - violation of CHECK constraint
INSERT INTO hygiene_inspection (station_id, inspector_id, inspection_date, cleanliness_score, status)
VALUES (1, 5, CURRENT_DATE, 15.5, 'Good');
-- ↑ This will fail: cleanliness_score must be BETWEEN 1.0 AND 10.0

-- ====================================================================
-- End of Constraints.sql
-- ====================================================================
