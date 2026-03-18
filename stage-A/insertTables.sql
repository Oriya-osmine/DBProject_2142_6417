/*
 * Insert Tables SQL Script
 * ========================
 * This script demonstrates three different data insertion methods:
 * 1. CSV Import using COPY command
 * 2. Mockaroo-generated INSERT statements
 * 3. Python-generated INSERT statements
 */

-- =====================================================
-- METHOD 1: CSV IMPORT (From DATA folder)
-- =====================================================
-- Inserts data from CSV files using PostgreSQL COPY command


COPY kitchen_station(station_name, description, is_active)
FROM '/data/output/kitchen_station.csv' DELIMITER ',' CSV HEADER;

-- =====================================================
-- METHOD 2: MOCKAROO-GENERATED (From mockarooFiles folder)
-- =====================================================
-- Chef data generated using Mockaroo service
-- Located at: /data/mockaroo/chef.sql

\i /data/mockaroo/chef.sql

-- =====================================================
-- METHOD 3: PYTHON-GENERATED (From DATA folder)
-- =====================================================
-- Data generated using Python scripts for large-scale data insertion
-- Located at: /data/output/

-- Insert kitchen orders (510+ records)
\i /data/output/kitchen_order_data.sql

-- Insert preparation tasks (20,000+ records)
\i /data/output/preparation_task_data.sql

-- Insert food prep logs (20,000+ records)
\i /data/output/food_prep_log_data.sql

-- Insert hygiene inspections (510+ records)
\i /data/output/hygiene_inspection_data.sql

-- =====================================================
-- Data Summary
-- =====================================================
-- kitchen_station:      ~14 records (from CSV)
-- chef:                 ~60 records (from Mockaroo)
-- kitchen_order:        ~510 records (from Python)
-- preparation_task:     ~20,010 records (from Python)
-- food_prep_log:        ~20,010 records (from Python)
-- hygiene_inspection:   ~510 records (from Python)
-- TOTAL:                ~51,104 records