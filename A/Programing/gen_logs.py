import random
from datetime import datetime, timedelta

def generate_logs(num_records=20010):
    """
    Generate food_prep_log records.
    Creates SQL INSERT statements for the food_prep_log table.
    Generates 20,000+ records as per project requirements.
    """
    output_file = "food_prep_log_data.sql"
    notes_pool = ['Perfectly cooked', 'Needs more salt', 'Standard prep', 'Extra crispy', 'Quick prep', 'Excellent quality', 'Good presentation', 'Checked and approved', '']

    def random_date():
        start = datetime(2025, 1, 1)
        end = datetime(2026, 3, 1)
        return start + timedelta(days=random.randrange((end - start).days))

    print(f"Generating {num_records} food prep logs...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"-- {num_records} INSERTs for food_prep_log table\n")
        f.write("-- Generated automatically using Python script\n")
        f.write("-- Covers period: January 1, 2025 - March 1, 2026\n\n")
        for _ in range(num_records):
            chef_id = random.randint(1, 50)
            menu_item_id = random.randint(1, 100)
            prep_time = random.randint(5, 120)
            p_date = random_date().strftime('%Y-%m-%d')
            note = random.choice(notes_pool)
            
            note_val = f"'{note}'" if note else "NULL"
            sql = f"INSERT INTO food_prep_log (chef_id, menu_item_id, preparation_time, prep_date, notes) VALUES ({chef_id}, {menu_item_id}, {prep_time}, '{p_date}', {note_val});\n"
            f.write(sql)
    print(f"Created '{output_file}'")

if __name__ == "__main__":
    generate_logs()

if __name__ == "__main__":
    generate_logs()