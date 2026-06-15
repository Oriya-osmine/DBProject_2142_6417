-- =============================================================
-- STAGE D - MAIN PROGRAMS / ANONYMOUS BLOCKS
-- Business goal: demonstrate end-to-end orchestration of the
-- function and procedure components.
-- =============================================================

-- -------------------------------------------------------------
-- Main Block 1
-- Calls the refcursor function, prints rows with RAISE NOTICE,
-- and then calls the Shift Handover procedure.
-- -------------------------------------------------------------
DO $$
DECLARE
    v_cursor refcursor;
    v_row RECORD;
    v_old_chef_id INT;
    v_new_chef_id INT;
BEGIN
    v_cursor := public.get_active_station_menu(1);

    LOOP
        FETCH v_cursor INTO v_row;
        EXIT WHEN NOT FOUND;

        RAISE NOTICE 'Station % | Item % | Price % | Available %',
            v_row.station_name,
            v_row.item_name,
            v_row.price,
            v_row.is_available;
    END LOOP;

    CLOSE v_cursor;

    SELECT pt.chef_id
    INTO v_old_chef_id
    FROM public.preparation_task pt
    WHERE pt.status = 'Pending'
    ORDER BY pt.task_id
    LIMIT 1;

    SELECT c.chef_id
    INTO v_new_chef_id
    FROM public.chef c
    WHERE c.is_on_shift = TRUE
      AND c.chef_id <> COALESCE(v_old_chef_id, -1)
    ORDER BY c.chef_id
    LIMIT 1;

    IF v_old_chef_id IS NULL OR v_new_chef_id IS NULL THEN
        RAISE EXCEPTION 'Could not find valid chefs for transfer_chef_tasks.';
    END IF;

    CALL public.transfer_chef_tasks(v_old_chef_id, v_new_chef_id);

EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Main Block 1 failed: %', SQLERRM;
END;
$$;

-- -------------------------------------------------------------
-- Main Block 2
-- Calls the workload function, prints the result, and then calls
-- the order dispatcher procedure.
-- -------------------------------------------------------------
DO $$
DECLARE
    v_chef_id INT;
    v_order_id INT;
    v_workload INTEGER;
BEGIN
    SELECT c.chef_id
    INTO v_chef_id
    FROM public.chef c
    ORDER BY c.chef_id
    LIMIT 1;

    IF v_chef_id IS NULL THEN
        RAISE EXCEPTION 'No chef found for workload calculation.';
    END IF;

    v_workload := public.calculate_chef_workload(v_chef_id);
    RAISE NOTICE 'Chef % workload: %', v_chef_id, v_workload;

    SELECT ko.kitchen_order_id
    INTO v_order_id
    FROM public.kitchen_order ko
    ORDER BY ko.kitchen_order_id
    LIMIT 1;

    IF v_order_id IS NULL THEN
        RAISE EXCEPTION 'No kitchen order found for dispatching.';
    END IF;

    CALL public.dispatch_kitchen_order(v_order_id);

END;
$$;
