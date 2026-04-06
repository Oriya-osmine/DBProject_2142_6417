-- ====================================================================
-- STAGE B: ROLLBACK & COMMIT - Transaction Management Demonstration
-- ====================================================================
-- This file demonstrates two transaction scenarios:
-- Scenario 1: Transaction with ROLLBACK (changes are undone)
-- Scenario 2: Transaction with COMMIT (changes are permanent)
-- ====================================================================

-- ════════════════════════════════════════════════════════════════════
-- SCENARIO 1: TRANSACTION WITH ROLLBACK
-- Demonstrates how ROLLBACK reverts all changes within a transaction
-- ════════════════════════════════════════════════════════════════════

-- STEP 1: Begin transaction, show initial state
BEGIN;
-- Check initial state of a sample task before update
SELECT 
    task_id, 
    kitchen_order_id, 
    chef_id, 
    status, 
    priority_level 
FROM preparation_task 
WHERE task_id = 1
LIMIT 1;

-- STEP 2: Update task status - moving from Pending to In-Prep
UPDATE preparation_task
SET status = 'In-Prep', priority_level = 5
WHERE task_id = 1;

-- STEP 3: Verify update - show new state (still in transaction)
SELECT 
    task_id, 
    kitchen_order_id, 
    chef_id, 
    status, 
    priority_level 
FROM preparation_task 
WHERE task_id = 1
LIMIT 1;

-- STEP 4: Rollback transaction - UNDO all changes
ROLLBACK;

-- STEP 5: Verify rollback - task returns to original state
SELECT 
    task_id, 
    kitchen_order_id, 
    chef_id, 
    status, 
    priority_level 
FROM preparation_task 
WHERE task_id = 1
LIMIT 1;

-- ════════════════════════════════════════════════════════════════════
-- SCENARIO 2: TRANSACTION WITH COMMIT
-- Demonstrates how COMMIT makes all changes permanent
-- ════════════════════════════════════════════════════════════════════

-- STEP 1: Begin transaction, show initial state
BEGIN;
-- Check initial state of a sample chef before update
SELECT 
    chef_id, 
    first_name, 
    last_name, 
    current_station_id, 
    is_on_shift 
FROM chef 
WHERE chef_id = 3
LIMIT 1;

-- STEP 2: Update chef assignment - change station and shift status
UPDATE chef
SET current_station_id = 7, is_on_shift = TRUE
WHERE chef_id = 3;

-- STEP 3: Verify update - show new state (still in transaction)
SELECT 
    chef_id, 
    first_name, 
    last_name, 
    current_station_id, 
    is_on_shift 
FROM chef 
WHERE chef_id = 3
LIMIT 1;

-- STEP 4: Commit transaction - MAKE all changes PERMANENT
COMMIT;

-- STEP 5: Verify commit - chef station remains updated
SELECT 
    chef_id, 
    first_name, 
    last_name, 
    current_station_id, 
    is_on_shift 
FROM chef 
WHERE chef_id = 3
LIMIT 1;

-- ════════════════════════════════════════════════════════════════════
-- SCENARIO 3 (BONUS): NESTED TRANSACTION EXAMPLE WITH SAVEPOINT
-- Demonstrates fine-grained rollback using SAVEPOINT
-- ════════════════════════════════════════════════════════════════════

BEGIN;
-- Initial state check
SELECT COUNT(*) as total_inspections FROM hygiene_inspection;

-- Create savepoint BEFORE first update
SAVEPOINT before_delete;

-- STEP 1: Delete old cancelled orders
DELETE FROM kitchen_order 
WHERE status = 'Cancelled' 
AND finish_time < (CURRENT_DATE - INTERVAL '1000 days');

-- Check state after delete
SELECT COUNT(*) as completed_orders FROM kitchen_order WHERE status = 'Served';

-- Create savepoint BEFORE second update
SAVEPOINT before_chef_update;

-- STEP 2: Update chef assignments
UPDATE chef 
SET is_on_shift = FALSE 
WHERE hire_date < '2023-01-01';

-- Check state after chef update
SELECT COUNT(*) as inactive_chefs FROM chef WHERE is_on_shift = FALSE;

-- STEP 3: Roll back to previous savepoint (undo only chef update)
ROLLBACK TO before_chef_update;

-- Verify: chef updates are undone, but delete is still pending
SELECT COUNT(*) as inactive_chefs FROM chef WHERE is_on_shift = FALSE;

-- STEP 4: Commit only the delete operation
COMMIT;

-- STEP 5: Final verification - only the delete persists
SELECT COUNT(*) as completed_orders FROM kitchen_order WHERE status = 'Served';

-- ════════════════════════════════════════════════════════════════════
-- End of RollbackCommit.sql
-- ════════════════════════════════════════════════════════════════════
