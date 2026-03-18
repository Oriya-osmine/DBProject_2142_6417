-- =====================================================
-- Data Verification - View all data
-- =====================================================

SELECT 'kitchen_station' as table_name, COUNT(*) as record_count FROM kitchen_station
UNION ALL
SELECT 'chef', COUNT(*) FROM chef
UNION ALL
SELECT 'kitchen_order', COUNT(*) FROM kitchen_order
UNION ALL
SELECT 'preparation_task', COUNT(*) FROM preparation_task
UNION ALL
SELECT 'food_prep_log', COUNT(*) FROM food_prep_log
UNION ALL
SELECT 'hygiene_inspection', COUNT(*) FROM hygiene_inspection;

-- View sample data from each table
SELECT * FROM kitchen_station LIMIT 5;
SELECT * FROM chef LIMIT 5;
SELECT * FROM kitchen_order LIMIT 5;
SELECT * FROM preparation_task LIMIT 5;
SELECT * FROM food_prep_log LIMIT 5;
SELECT * FROM hygiene_inspection LIMIT 5;
