import random

def generate_tasks(num_records=20010):
    """
    Generate preparation_task records.
    Creates SQL INSERT statements for the preparation_task table.
    Generates 20,000+ records as per project requirements.
    """
    output_file = "../DATA/preparation_task_data.sql"
    descriptions = ['Chop onions', 'Grill patties', 'Prep salad', 'Boil pasta', 'Clean fryer', 
                    'Slice tomatoes', 'Dice bell peppers', 'Season meat', 'Heat oil', 'Assemble platter',
                    'Blanch vegetables', 'Marinate chicken', 'Check temperature', 'Plate garnish']
    statuses = ['Pending', 'In-Prep', 'Ready', 'Completed']

    print(f"Generating {num_records} preparation tasks...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"-- {num_records} INSERTs for preparation_task table\n")
        f.write("-- Generated automatically using Python script\n\n")
        for _ in range(num_records):
            order_id = random.randint(1, 510)
            chef_id = random.randint(1, 50)
            desc = random.choice(descriptions)
            status = random.choice(statuses)
            priority = random.randint(1, 5)
            
            sql = f"INSERT INTO preparation_task (kitchen_order_id, chef_id, task_description, status, priority_level) VALUES ({order_id}, {chef_id}, '{desc}', '{status}', {priority});\n"
            f.write(sql)
    print(f"Created '{output_file}'")

if __name__ == "__main__":
    generate_tasks()

if __name__ == "__main__":
    generate_tasks()