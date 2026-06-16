-- ====================================================================
-- STAGE C: VIEWS AND QUERIES
-- ====================================================================

-- ==========================================
-- VIEW 1: Local Kitchen Perspective
-- ==========================================
-- View showing menu item responsibilities per kitchen station
-- `view_station_responsibilities`: station name, description, item name, and availability
CREATE VIEW mappings.view_station_responsibilities AS
SELECT 
    ks.station_name,         
    ks.description,          
    mi.item_name,          
    mi.is_available        
FROM public.kitchen_station ks
JOIN mappings.station_menu_item_link smil ON ks.station_id = smil.local_station_id -- Link between station and menu item
JOIN partners.menu_item mi ON smil.menu_item_id = mi.menu_item_id; -- Menu item from partners schema


-- ==========================================
-- VIEW 2: Partner/External Perspective
-- ==========================================
-- View from the Partner's perspective:
-- Shows menu items, categories, recipe instructions, and the local kitchen station assigned to prep them.
CREATE VIEW mappings.view_partner_recipe_routing AS
SELECT 
    mc.category_name,
    mi.item_name,
    mi.price,
    r.instructions AS recipe_instructions,
    ks.station_name AS prepared_at_station
FROM partners.menu_item mi
JOIN partners.menu_category mc ON mi.category_id = mc.category_id -- Joining Partner's category table
LEFT JOIN partners.recipe r ON mi.menu_item_id = r.menu_item_id -- Left join in case some items don't have recipes yet
JOIN mappings.station_menu_item_link smil ON mi.menu_item_id = smil.menu_item_id -- The Integration!
JOIN public.kitchen_station ks ON smil.local_station_id = ks.station_id; -- Your local kitchen station


-- ====================================================================
-- STEP 8: REQUIRED QUERIES ON THE VIEWS
-- ====================================================================

-- ---------------------------------------------------------
-- Queries for View 1 (mappings.view_station_responsibilities)
-- ---------------------------------------------------------

-- Query 1: Workload distribution. 
-- Meaning: Counts how many menu items are assigned to each station to identify potential bottlenecks.
SELECT 
    station_name, 
    COUNT(item_name) AS total_items_assigned
FROM mappings.view_station_responsibilities
GROUP BY station_name
ORDER BY total_items_assigned DESC;

-- Query 2: Active menu check for a specific station.
-- Meaning: Allows a specific station (e.g., 'Grill Station') to quickly print a checklist of what active items they need to be ready to cook today.
SELECT 
    item_name, 
    is_available 
FROM mappings.view_station_responsibilities 
WHERE station_name = 'Grill Station' 
  AND is_available = TRUE;


-- ---------------------------------------------------------
-- Queries for View 2 (mappings.view_partner_recipe_routing)
-- ---------------------------------------------------------

-- Query 3: Missing Information Audit.
-- Meaning: Helps the partner identify which of their menu items are missing recipe instructions so they can provide them to the local kitchen.
SELECT 
    item_name, 
    prepared_at_station
FROM mappings.view_partner_recipe_routing
WHERE recipe_instructions IS NULL;

-- Query 4: Premium Item Routing.
-- Meaning: The partner wants to know exactly where their most expensive, high-tier menu items (costing more than $20) are being prepared.
SELECT 
    item_name, 
    category_name, 
    price, 
    prepared_at_station 
FROM mappings.view_partner_recipe_routing
WHERE price > 20.00
ORDER BY price DESC;