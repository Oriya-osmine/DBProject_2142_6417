import gen_orders
import gen_logs
import gen_tasks

def run_all():
    print("--- Starting Full Data Generation ---")
    
    # 1. Generate 500 orders
    gen_orders.generate_orders(500)
    
    # 2. Generate 20,000 logs
    gen_logs.generate_logs(20000)
    
    # 3. Generate 20,000 tasks
    gen_tasks.generate_tasks(20000)
    
    print("--- All SQL files generated successfully ---")

if __name__ == "__main__":
    run_all()