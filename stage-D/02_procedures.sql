-- =============================================================
-- STAGE D - PROCEDURES (OPTIMIZED)
-- Business goal: demonstrate operational task routing and order
-- dispatching using highly efficient set-based logic and TABLESAMPLE.
-- =============================================================

-- -------------------------------------------------------------
-- Procedure 1: Shift Handover
-- transfer_chef_tasks(p_old_chef_id INT, p_new_chef_id INT)
-- -------------------------------------------------------------
CREATE OR REPLACE PROCEDURE public.transfer_chef_tasks(p_old_chef_id INT, p_new_chef_id INT)
LANGUAGE plpgsql
AS $$
DECLARE
    v_old_chef_exists BOOLEAN;
    v_new_chef_exists BOOLEAN;
    v_rows_updated INT; -- Variable to hold the count of updated rows
BEGIN
    -- 1. Validate Source Chef
    SELECT EXISTS(SELECT 1 FROM public.chef WHERE chef_id = p_old_chef_id) INTO v_old_chef_exists;
    IF NOT v_old_chef_exists THEN
        RAISE EXCEPTION 'Source Chef ID % does not exist in the system. Cannot transfer tasks.', p_old_chef_id;
    END IF;

    -- 2. Validate Target Chef
    SELECT EXISTS(SELECT 1 FROM public.chef WHERE chef_id = p_new_chef_id) INTO v_new_chef_exists;
    IF NOT v_new_chef_exists THEN
        RAISE EXCEPTION 'Target Chef ID % does not exist in the system.', p_new_chef_id;
    END IF;

    -- 3. Set-Based Bulk Update
    UPDATE public.preparation_task
    SET chef_id = p_new_chef_id,
        status = 'In-Prep'
    WHERE chef_id = p_old_chef_id AND status = 'Pending';
    
    -- 4. Get the exact number of rows that were changed
    GET DIAGNOSTICS v_rows_updated = ROW_COUNT;

    RAISE NOTICE 'Tasks transferred successfully. Total tasks moved: %', v_rows_updated;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'An error occurred: %', SQLERRM;
END;
$$;

-- -------------------------------------------------------------
-- Procedure 2: Order Dispatcher
-- dispatch_kitchen_order(p_order_id INT)
-- Uses TABLESAMPLE instead of ORDER BY random() to avoid sorting
-- the entire table, making it highly scalable for massive databases.
-- -------------------------------------------------------------
-- ====================================================================
-- REAL-WORLD ARCHITECTURE NOTE (PRODUCTION INTEGRATION)
-- ====================================================================
-- In a full enterprise production system, this dispatch procedure would 
-- directly query 'mappings.view_partner_recipe_routing' instead of 
-- generating generic placeholder tasks or using a random chef sample.
--
-- How it would look in production code:
--
--  -- 1. Fetch the physical station and recipe for the ordered menu item
--  SELECT prepared_at_station, recipe_instructions 
--  INTO v_target_station, v_recipe_text
--  FROM mappings.view_partner_recipe_routing
--  WHERE item_name = v_ordered_item_name;
--
--  -- 2. Target only an on-shift chef assigned to that specific station
--  SELECT chef_id INTO v_chef_id FROM public.chef 
--  WHERE current_station_id = v_target_station AND is_on_shift = TRUE 
--  LIMIT 1;
--
--  -- 3. Insert the exact partner recipe steps into the task ticket
--  INSERT INTO public.preparation_task (kitchen_order_id, chef_id, task_description)
--  VALUES (p_order_id, v_chef_id, v_recipe_text);
-- ====================================================================
DROP PROCEDURE IF EXISTS public.dispatch_kitchen_order(INT);

CREATE OR REPLACE PROCEDURE public.dispatch_kitchen_order(p_order_id INT)
LANGUAGE plpgsql
AS $$
DECLARE
    v_station_record RECORD;
    v_chef_id INT;
    v_task_description TEXT;
    v_priority INT;
    v_task_index INT := 0;
    v_current_status VARCHAR(50);
BEGIN

    SELECT status INTO v_current_status 
    FROM public.kitchen_order 
    WHERE kitchen_order_id = p_order_id;

    IF v_current_status IS NULL THEN
        RAISE EXCEPTION 'Cannot dispatch: Order ID % does not exist.', p_order_id;
    ELSIF v_current_status != 'Pending' THEN
        RAISE EXCEPTION 'Cannot dispatch: Order % is already %.', p_order_id, v_current_status;
    END IF;
    -- Using TABLESAMPLE BERNOULLI(50) grabs a random ~50% of the table without sorting.
    -- (We use BERNOULLI instead of SYSTEM because SYSTEM doesn't work well on tiny tables).
    FOR v_station_record IN
        SELECT station_id
        FROM public.kitchen_station TABLESAMPLE BERNOULLI (50)
        WHERE is_active = TRUE
        LIMIT 3
    LOOP
        v_task_index := v_task_index + 1;

        -- Find a chef using TABLESAMPLE
        SELECT c.chef_id
        INTO v_chef_id
        FROM public.chef c TABLESAMPLE BERNOULLI (50)
        WHERE c.current_station_id = v_station_record.station_id
          AND c.is_on_shift = TRUE
        LIMIT 1;

        -- Fallback: If no chef at the specific station is found, find any chef
        IF v_chef_id IS NULL THEN
            SELECT c.chef_id
            INTO v_chef_id
            FROM public.chef c TABLESAMPLE BERNOULLI (50)
            WHERE c.is_on_shift = TRUE
            LIMIT 1;
        END IF;

        IF v_chef_id IS NULL THEN
            RAISE EXCEPTION 'No available on-shift chef found for order %.', p_order_id;
        END IF;

        v_task_description := CASE v_task_index
            WHEN 1 THEN 'Dispatch task: receiving and staging'
            WHEN 2 THEN 'Dispatch task: preparation and cooking'
            ELSE 'Dispatch task: plating and quality check'
        END;

        v_priority := CASE v_task_index
            WHEN 1 THEN 1
            WHEN 2 THEN 2
            ELSE 3
        END;

        INSERT INTO public.preparation_task (
            kitchen_order_id,
            chef_id,
            task_description,
            status,
            priority_level
        )
        VALUES (
            p_order_id,
            v_chef_id,
            v_task_description,
            'Pending',
            v_priority
        );
    END LOOP;

    IF v_task_index = 0 THEN
        RAISE EXCEPTION 'No active stations were available to dispatch order %.', p_order_id;
    END IF;

    UPDATE public.kitchen_order 
    SET status = 'In-Prep'
    WHERE kitchen_order_id = p_order_id;
END;
$$;