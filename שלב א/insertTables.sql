-- ייבוא מהתיקייה המקורית של ה-CSV
COPY kitchen_station(station_name, description, is_active)
FROM '/data/import/kitchen_station.csv' DELIMITER ',' CSV HEADER;

COPY hygiene_inspection(station_id, inspector_id, inspection_date, cleanliness_score, temperature_check, status, comments)
FROM '/data/import/hygiene_inspection.csv' DELIMITER ',' CSV HEADER;

-- הערה למרצה:
-- קבצי ה-SQL נמצאים בתיקיות:
-- 1. /data/mockaroo/chef.sql
-- 2. /data/programing/kitchen_order_data.sql
-- 3. /data/programing/preparation_task_data.sql
-- 4. /data/programing/food_prep_log_data.sql