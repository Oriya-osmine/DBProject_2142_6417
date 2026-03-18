import random
from datetime import datetime, timedelta

def generate_orders(num_records=510):
    """
    Generate kitchen_order records.
    Creates SQL INSERT statements for the kitchen_order table.
    """
    output_file = "../DATA/kitchen_order_data.sql"
    statuses = ['Pending', 'In-Prep', 'Ready', 'Served', 'Cancelled']

    def random_start_time():
        start = datetime(2025, 1, 1, 12, 0, 0)
        end = datetime(2026, 3, 1, 23, 0, 0)
        time_between = end - start
        random_seconds = random.randrange(int(time_between.total_seconds()))
        return start + timedelta(seconds=random_seconds)

    print(f"Generating {num_records} kitchen orders...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"-- {num_records} INSERTs for kitchen_order table\n")
        f.write("-- Generated automatically using Python script\n\n")
        for _ in range(num_records):
            order_id = random.randint(1000, 9999)
            status = random.choice(statuses)
            start_time = random_start_time()
            station_id = random.randint(1, 14)

            if status in ['Pending', 'In-Prep']:
                finish_time_str = "NULL"
            else:
                prep_minutes = random.randint(10, 65)
                finish_time = start_time + timedelta(minutes=prep_minutes)
                finish_time_str = f"'{finish_time.strftime('%Y-%m-%d %H:%M:%S')}'"

            sql = f"INSERT INTO kitchen_order (order_id, status, start_time, finish_time, station_id) VALUES ({order_id}, '{status}', '{start_time.strftime('%Y-%m-%d %H:%M:%S')}', {finish_time_str}, {station_id});\n"
            f.write(sql)
    print(f"Created '{output_file}'")

if __name__ == "__main__":
    generate_orders()