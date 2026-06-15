-- =============================================================
-- STAGE D - PROCEDURES
-- Business goal: demonstrate operational task routing and order
-- dispatching using explicit and implicit cursor logic.
-- =============================================================

-- -------------------------------------------------------------
-- Procedure 1: Shift Handover
-- transfer_chef_tasks(p_old_chef_id INT, p_new_chef_id INT)
-- Uses an explicit cursor, FETCH loop, exception handling, and DML UPDATE.
-- -------------------------------------------------------------
DROP PROCEDURE IF EXISTS public.transfer_chef_tasks(INT, INT);

CREATE OR REPLACE PROCEDURE public.transfer_chef_tasks(
    p_old_chef_id INT,
    p_new_chef_id INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_new_chef_on_shift BOOLEAN;
    v_task_cursor CURSOR FOR
        SELECT *
        FROM public.preparation_task
        WHERE chef_id = p_old_chef_id
          AND status = 'Pending'
        ORDER BY task_id;
    v_task_row public.preparation_task%ROWTYPE;
BEGIN
    SELECT is_on_shift
    INTO v_new_chef_on_shift
    FROM public.chef
    WHERE chef_id = p_new_chef_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Chef % does not exist.', p_new_chef_id;
    ELSIF v_new_chef_on_shift IS DISTINCT FROM TRUE THEN
        RAISE EXCEPTION 'Chef % must be on shift before receiving tasks.', p_new_chef_id;
    END IF;

    OPEN v_task_cursor;
    LOOP
        FETCH v_task_cursor INTO v_task_row;
        EXIT WHEN NOT FOUND;

        UPDATE public.preparation_task
        SET chef_id = p_new_chef_id,
            status = 'In-Prep'
        WHERE task_id = v_task_row.task_id;
    END LOOP;
    CLOSE v_task_cursor;

EXCEPTION
    WHEN OTHERS THEN
        IF v_task_cursor%ISOPEN THEN
            CLOSE v_task_cursor;
        END IF;
        RAISE;
END;
$$;

-- -------------------------------------------------------------
-- Procedure 2: Order Dispatcher
-- dispatch_kitchen_order(p_order_id INT)
-- Uses an implicit cursor inside a FOR loop to pick active stations,
-- then inserts three preparation tasks for the given order.
-- Demonstrates: implicit cursor, FOR loop, DML INSERT, branching.
-- -------------------------------------------------------------
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
BEGIN
    FOR v_station_record IN
        SELECT station_id
        FROM public.kitchen_station
        WHERE is_active = TRUE
        ORDER BY random()
        LIMIT 3
    LOOP
        v_task_index := v_task_index + 1;

        SELECT c.chef_id
        INTO v_chef_id
        FROM public.chef c
        WHERE c.current_station_id = v_station_record.station_id
          AND c.is_on_shift = TRUE
        ORDER BY random()
        LIMIT 1;

        IF v_chef_id IS NULL THEN
            SELECT c.chef_id
            INTO v_chef_id
            FROM public.chef c
            WHERE c.is_on_shift = TRUE
            ORDER BY random()
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
END;
$$;
