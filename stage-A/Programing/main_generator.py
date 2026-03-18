"""
Main data generator script.
Generates SQL INSERT statements for all tables according to project requirements:
- At least 500 records per table
- At least 20,000 records in 2 tables (kitchen_order, preparation_task, food_prep_log)
"""

import gen_orders
import gen_logs
import gen_tasks
import gen_hygiene

def run_all():
    print("=== Starting Full Data Generation ===")
    
    # 1. Generate 500+ kitchen orders
    gen_orders.generate_orders(510)
    
    # 2. Generate 20,000+ food prep logs
    gen_logs.generate_logs(20010)
    
    # 3. Generate 20,000+ preparation tasks
    gen_tasks.generate_tasks(20010)
    
    # 4. Generate 510+ hygiene inspections
    gen_hygiene.generate_hygiene_data(510)
    
    print("\n=== All SQL files generated successfully ===")
    print("Generated files:")
    print("  - kitchen_order_data.sql (510 records)")
    print("  - food_prep_log_data.sql (20,010 records)")
    print("  - preparation_task_data.sql (20,010 records)")
    print("  - hygiene_inspection_data.sql (510 records)")
    print("  - hygiene_inspection.csv (510 records)")

if __name__ == "__main__":
    run_all()