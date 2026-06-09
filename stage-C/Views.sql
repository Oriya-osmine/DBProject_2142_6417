
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
JOIN partners.menu_item mi ON smil.menu_item_id = mi.menu_item_id; -- Menu item from partners schema_order_routing_to_kitchen;



DROP VIEW IF EXISTS mappings.view_partner_recipe_routing;

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