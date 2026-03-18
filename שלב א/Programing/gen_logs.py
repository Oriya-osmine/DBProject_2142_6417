import random
from datetime import datetime, timedelta

def generate_logs(num_records=20000):
    output_file = "food_prep_log_data.sql"
    notes_pool = ['Perfectly cooked', 'Needs more salt', 'Standard prep', 'Extra crispy', 'Quick prep', '']

    def random_date():
        start = datetime(2025, 1, 1)
        end = datetime(2026, 3, 1)
        return start + timedelta(days=random.randrange((end - start).days))

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("-- 20,000 INSERTs for food_prep_log\n")
        for _ in range(num_records):
            chef_id = random.randint(1, 50)
            menu_item_id = random.randint(1, 100)
            prep_time = random.randint(5, 120)
            p_date = random_date().strftime('%Y-%m-%d')
            note = random.choice(notes_pool)
            
            sql = f"INSERT INTO food_prep_log (chef_id, menu_item_id, preparation_time, prep_date, notes) VALUES ({chef_id}, {menu_item_id}, {prep_time}, '{p_date}', '{note}');\n"
            f.write(sql)
    print(f"Created '{output_file}'")

if __name__ == "__main__":
    generate_logs()