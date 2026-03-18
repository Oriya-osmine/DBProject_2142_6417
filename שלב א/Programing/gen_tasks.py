import random

def generate_tasks(num_records=20000):
    output_file = "preparation_task_data.sql"
    descriptions = ['Chop onions', 'Grill patties', 'Prep salad', 'Boil pasta', 'Clean fryer', 'Slice tomatoes']
    statuses = ['Pending', 'In-Prep', 'Ready']

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("-- 20,000 INSERTs for preparation_task\n")
        for _ in range(num_records):
            order_id = random.randint(1, 500)
            chef_id = random.randint(1, 50)
            desc = random.choice(descriptions)
            status = random.choice(statuses)
            priority = random.randint(1, 5)
            
            sql = f"INSERT INTO preparation_task (kitchen_order_id, chef_id, task_description, status, priority_level) VALUES ({order_id}, {chef_id}, '{desc}', '{status}', {priority});\n"
            f.write(sql)
    print(f"Created '{output_file}'")

if __name__ == "__main__":
    generate_tasks()