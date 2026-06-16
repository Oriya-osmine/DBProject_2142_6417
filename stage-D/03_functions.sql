-- =============================================================
-- STAGE D - FUNCTIONS (OPTIMIZED)
-- Business goal: demonstrate reporting logic using ref cursors
-- and highly efficient set-based aggregate calculations.
-- =============================================================

-- -------------------------------------------------------------
-- Function 1: Station Readiness Report
-- get_active_station_menu(p_station_id INT)
-- Returns a refcursor with all available menu items for a station.
-- Optimization: Added early validation. The refcursor itself is 
-- already highly efficient for streaming data to applications!
-- -------------------------------------------------------------
DROP FUNCTION IF EXISTS public.get_active_station_menu(INT);

CREATE OR REPLACE FUNCTION public.get_active_station_menu(p_station_id INT)
RETURNS refcursor
LANGUAGE plpgsql
AS $$
DECLARE
    v_cursor refcursor;
    v_station_exists BOOLEAN;
BEGIN
    -- 1. Validate Input (Fails fast if the station doesn't exist)
    SELECT EXISTS(SELECT 1 FROM public.kitchen_station WHERE station_id = p_station_id) INTO v_station_exists;
    
    IF NOT v_station_exists THEN
        RAISE EXCEPTION 'Station ID % does not exist.', p_station_id;
    END IF;

    -- 2. Setup dynamic cursor name
    v_cursor := format('station_menu_cursor_%s', p_station_id);

    -- 3. Open Cursor (This is efficient because it doesn't load 
    -- all data into memory at once; it creates a live stream).
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
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Failed to generate station menu: %', SQLERRM;
END;
$$;

-- -------------------------------------------------------------
-- Function 2: Chef Workload Calculator
-- calculate_chef_workload(p_chef_id INT)
-- Optimization: Completely removes the slow FOR...LOOP (RBAR) 
-- and replaces it with a blazing fast set-based SUM aggregate.
-- -------------------------------------------------------------
DROP FUNCTION IF EXISTS public.calculate_chef_workload(INT);

CREATE OR REPLACE FUNCTION public.calculate_chef_workload(p_chef_id INT)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_workload INTEGER := 0;
    v_chef_exists BOOLEAN;
BEGIN
    -- 1. Validate Input
    SELECT EXISTS(SELECT 1 FROM public.chef WHERE chef_id = p_chef_id) INTO v_chef_exists;
    
    IF NOT v_chef_exists THEN
        RAISE EXCEPTION 'Chef ID % was not found in public.chef.', p_chef_id;
    END IF;

    -- 2. Set-Based Aggregate Calculation
    -- Instead of pulling rows into memory one by one, we tell the 
    -- database engine to do the math instantly at the disk level.
    SELECT COALESCE(SUM(priority_level), 0)
    INTO v_workload
    FROM public.preparation_task
    WHERE chef_id = p_chef_id
      AND status = 'Pending';

    RETURN v_workload;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Workload calculation failed: %', SQLERRM;
END;
$$;