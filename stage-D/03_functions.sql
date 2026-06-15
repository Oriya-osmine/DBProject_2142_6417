-- =============================================================
-- STAGE D - FUNCTIONS
-- Business goal: demonstrate reporting logic using ref cursors
-- and aggregate workload calculation.
-- =============================================================

-- -------------------------------------------------------------
-- Function 1: Station Readiness Report
-- get_active_station_menu(p_station_id INT)
-- Returns a refcursor with all available menu items for a station.
-- Demonstrates: returning a refcursor and query joins.
-- -------------------------------------------------------------
DROP FUNCTION IF EXISTS public.get_active_station_menu(INT);

CREATE OR REPLACE FUNCTION public.get_active_station_menu(p_station_id INT)
RETURNS refcursor
LANGUAGE plpgsql
AS $$
DECLARE
    v_cursor refcursor;
BEGIN
    v_cursor := format('station_menu_cursor_%s', p_station_id);

    OPEN v_cursor FOR
        SELECT
            ks.station_id,
            ks.station_name,
            mi.menu_item_id,
            mi.item_name,
            mi.price,
            mi.is_available
        FROM public.kitchen_station ks
        JOIN mappings.station_menu_item_link smil
            ON ks.station_id = smil.local_station_id
        JOIN partners.menu_item mi
            ON smil.menu_item_id = mi.menu_item_id
        WHERE ks.station_id = p_station_id
          AND ks.is_active = TRUE
          AND mi.is_available = TRUE
        ORDER BY mi.item_name;

    RETURN v_cursor;
END;
$$;

-- -------------------------------------------------------------
-- Function 2: Chef Workload Calculator
-- calculate_chef_workload(p_chef_id INT)
-- Returns the sum of priority_level for all pending tasks.
-- Demonstrates: LOOP, exception handling, and validation logic.
-- -------------------------------------------------------------
DROP FUNCTION IF EXISTS public.calculate_chef_workload(INT);

CREATE OR REPLACE FUNCTION public.calculate_chef_workload(p_chef_id INT)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_workload INTEGER := 0;
    v_task_row RECORD;
    v_chef_exists BOOLEAN;
BEGIN
    SELECT TRUE
    INTO v_chef_exists
    FROM public.chef
    WHERE chef_id = p_chef_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Chef % was not found in public.chef.', p_chef_id;
    END IF;

    FOR v_task_row IN
        SELECT priority_level
        FROM public.preparation_task
        WHERE chef_id = p_chef_id
          AND status = 'Pending'
    LOOP
        v_workload := v_workload + COALESCE(v_task_row.priority_level, 0);
    END LOOP;

    RETURN v_workload;

EXCEPTION
    WHEN OTHERS THEN
        RAISE;
END;
$$;
