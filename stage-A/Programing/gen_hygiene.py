"""
Generate 500+ hygiene inspection records for the hygiene_inspection table.
Creates CSV file and SQL insert statements.
"""
import random
from datetime import datetime, timedelta

def generate_hygiene_data(num_records=510):
    """Generate hygiene inspection data with CSV and SQL formats."""
    
    output_csv = "../DATA/hygiene_inspection.csv"
    output_sql = "../DATA/hygiene_inspection_data.sql"
    
    statuses = ['Perfect condition', 'All clean', 'Passed inspection', 
                'Needs improvement', 'Fridge slightly warm', 'Good']
    
    def random_date():
        """Generate random date between Jan 1, 2025 and March 1, 2026."""
        start = datetime(2025, 1, 1)
        end = datetime(2026, 3, 1)
        return start + timedelta(days=random.randrange((end - start).days))
    
    print("Generating hygiene inspection data...")
    
    # Generate CSV
    with open(output_csv, 'w', encoding='utf-8') as f:
        f.write("station_id,inspector_id,inspection_date,next_inspection_date,cleanliness_score,temperature_check,status,comments\n")
        
        for i in range(num_records):
            station_id = random.randint(1, 14)  # Valid station IDs
            inspector_id = random.randint(1, 50)  # Valid chef IDs
            inspection_date = random_date()
            next_inspection_date = inspection_date + timedelta(days=random.randint(7, 30))
            cleanliness_score = round(random.uniform(3.0, 5.9), 1)  # 1-10 scale, realistic distribution
            temperature_check = round(random.uniform(4.0, 25.0), 2)  # Celsius
            status = random.choice(statuses)
            comments = random.choice(['', 'OK', 'Watch fridge temp', 'Deep clean needed', 'Excellent'])
            
            f.write(f"{station_id},{inspector_id},{inspection_date.strftime('%Y-%m-%d')},{next_inspection_date.strftime('%Y-%m-%d')},{cleanliness_score},{temperature_check},{status},{comments}\n")
    
    print(f"Created '{output_csv}' with {num_records} records")
    
    # Generate SQL INSERT statements
    with open(output_sql, 'w', encoding='utf-8') as f:
        f.write(f"-- {num_records} INSERTs for hygiene_inspection table\n")
        f.write("-- Generated automatically using Python script\n\n")
        
        for i in range(num_records):
            station_id = random.randint(1, 14)
            inspector_id = random.randint(1, 50)
            inspection_date = random_date()
            next_inspection_date = inspection_date + timedelta(days=random.randint(7, 30))
            cleanliness_score = round(random.uniform(3.0, 5.9), 1)
            temperature_check = round(random.uniform(4.0, 25.0), 2)
            status = random.choice(statuses)
            comments = random.choice(['', 'OK', 'Watch fridge temp', 'Deep clean needed', 'Excellent'])
            
            comment_val = f"'{comments}'" if comments else "NULL"
            
            sql = f"INSERT INTO hygiene_inspection (station_id, inspector_id, inspection_date, next_inspection_date, cleanliness_score, temperature_check, status, comments) VALUES ({station_id}, {inspector_id}, '{inspection_date.strftime('%Y-%m-%d')}', '{next_inspection_date.strftime('%Y-%m-%d')}', {cleanliness_score}, {temperature_check}, '{status}', {comment_val});\n"
            f.write(sql)
    
    print(f"Created '{output_sql}' with {num_records} INSERT statements")

if __name__ == "__main__":
    generate_hygiene_data()
