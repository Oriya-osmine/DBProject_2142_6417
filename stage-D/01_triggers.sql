-- =============================================================
-- STAGE D - TRIGGERS
-- Business goal: demonstrate row-level automation for menu tracking
-- and hygiene-driven station deactivation.
-- =============================================================

CREATE SCHEMA IF NOT EXISTS partners;

CREATE TABLE IF NOT EXISTS partners.menu_change_log (
    log_id SERIAL PRIMARY KEY,
    change_description TEXT,
    menu_item_id INT,
    change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- -------------------------------------------------------------
-- Trigger 1: Menu Version Control
-- On UPDATE of partners.menu_item, compare OLD and NEW values for
-- price and is_available. If anything changed, write a log row.
-- Demonstrates: OLD/NEW records, branching, and DML INSERT.
-- -------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_menu_version_control ON partners.menu_item;
DROP FUNCTION IF EXISTS partners.fn_menu_version_control();

CREATE OR REPLACE FUNCTION partners.fn_menu_version_control()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_change_description TEXT;
BEGIN
    IF NEW.price IS DISTINCT FROM OLD.price AND NEW.is_available IS DISTINCT FROM OLD.is_available THEN
        v_change_description := format(
            'Menu item %s updated: price changed from %s to %s and availability changed from %s to %s',
            NEW.menu_item_id,
            OLD.price,
            NEW.price,
            OLD.is_available,
            NEW.is_available
        );
    ELSIF NEW.price IS DISTINCT FROM OLD.price THEN
        v_change_description := format(
            'Menu item %s updated: price changed from %s to %s',
            NEW.menu_item_id,
            OLD.price,
            NEW.price
        );
    ELSIF NEW.is_available IS DISTINCT FROM OLD.is_available THEN
        v_change_description := format(
            'Menu item %s updated: availability changed from %s to %s',
            NEW.menu_item_id,
            OLD.is_available,
            NEW.is_available
        );
    ELSE
        RETURN NEW;
    END IF;

    INSERT INTO partners.menu_change_log (change_description, menu_item_id)
    VALUES (v_change_description, NEW.menu_item_id);

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_menu_version_control
AFTER UPDATE OF price, is_available ON partners.menu_item
FOR EACH ROW
EXECUTE FUNCTION partners.fn_menu_version_control();

-- -------------------------------------------------------------
-- Trigger 2: Hygiene Alert
-- On INSERT into public.hygiene_inspection, if the cleanliness
-- score is below 6.0, deactivate the station.
-- Demonstrates: branching and DML UPDATE.
-- -------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_hygiene_alert ON public.hygiene_inspection;
DROP FUNCTION IF EXISTS public.fn_hygiene_alert();

CREATE OR REPLACE FUNCTION public.fn_hygiene_alert()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.cleanliness_score IS NULL THEN
        RAISE NOTICE 'Inspection % has no cleanliness score; no station update performed.', NEW.inspection_id;
    ELSIF NEW.cleanliness_score < 6.0 THEN
        UPDATE public.kitchen_station
        SET is_active = FALSE
        WHERE station_id = NEW.station_id;
    ELSE
        RAISE NOTICE 'Inspection % passed the threshold for station %.', NEW.inspection_id, NEW.station_id;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_hygiene_alert
AFTER INSERT ON public.hygiene_inspection
FOR EACH ROW
EXECUTE FUNCTION public.fn_hygiene_alert();