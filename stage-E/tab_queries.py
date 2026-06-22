import customtkinter as ctk
import shared

class QueriesFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        top_bar = ctk.CTkFrame(self, height=50, fg_color="transparent")
        top_bar.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(top_bar, text="Reports & SQL Queries (Stage B)", font=ctk.CTkFont(size=20, weight="bold")).pack(side="left", padx=10)
        
        # Table for displaying results
        self.result_table = shared.GenericDataTable(self)
        self.result_table.pack(pady=10, fill="both", expand=True, padx=20)
        
        # Frame for Query Buttons (Grid layout for 8 buttons)
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10, padx=20, fill="x")
        
        btn_width = 400
        
        # Row 0
        ctk.CTkButton(btn_frame, text="1. Stations Workload Distribution", width=btn_width, command=self.run_query_1).grid(row=0, column=0, padx=10, pady=5)
        ctk.CTkButton(btn_frame, text="2. Chefs with High Priority Tasks", width=btn_width, command=self.run_query_2).grid(row=0, column=1, padx=10, pady=5)
        
        # Row 1
        ctk.CTkButton(btn_frame, text="3. Order Preparation Duration", width=btn_width, command=self.run_query_3).grid(row=1, column=0, padx=10, pady=5)
        ctk.CTkButton(btn_frame, text="4. Monthly Station Workload Trends", width=btn_width, command=self.run_query_4).grid(row=1, column=1, padx=10, pady=5)

        # Row 2
        ctk.CTkButton(btn_frame, text="5. Hygiene Scores by Station/Month", width=btn_width, command=self.run_query_5).grid(row=2, column=0, padx=10, pady=5)
        ctk.CTkButton(btn_frame, text="6. Chef Productivity Analysis", width=btn_width, command=self.run_query_6).grid(row=2, column=1, padx=10, pady=5)

        # Row 3
        ctk.CTkButton(btn_frame, text="7. Active Tasks by Priority", width=btn_width, command=self.run_query_7).grid(row=3, column=0, padx=10, pady=5)
        ctk.CTkButton(btn_frame, text="8. Temperature Anomalies Alert", width=btn_width, command=self.run_query_8).grid(row=3, column=1, padx=10, pady=5)

    def run_query_1(self):
        query = """
            SELECT 
                ks.station_id, ks.station_name,
                COUNT(ko.kitchen_order_id) as total_orders,
                SUM(CASE WHEN ko.status = 'Pending' THEN 1 ELSE 0 END) as pending_orders,
                SUM(CASE WHEN ko.status = 'In-Prep' THEN 1 ELSE 0 END) as in_prep_orders,
                SUM(CASE WHEN ko.status = 'Ready' THEN 1 ELSE 0 END) as ready_orders,
                SUM(CASE WHEN ko.status = 'Served' THEN 1 ELSE 0 END) as served_orders,
                SUM(CASE WHEN ko.status = 'Cancelled' THEN 1 ELSE 0 END) as cancelled_orders
            FROM public.kitchen_station ks
            LEFT JOIN public.kitchen_order ko ON ks.station_id = ko.station_id
            GROUP BY ks.station_id, ks.station_name
            ORDER BY pending_orders DESC, in_prep_orders DESC;
        """
        self.result_table.set_columns(("Station ID", "Station Name", "Total Orders", "Pending", "In-Prep", "Ready", "Served", "Cancelled"))
        self.result_table.populate_data(query)

    def run_query_2(self):
        query = """
            SELECT 
                c.chef_id,
                CONCAT(c.first_name, ' ', c.last_name) as chef_name,
                c.specialization,
                COUNT(pt.task_id) as high_priority_tasks
            FROM public.chef c
            LEFT JOIN public.preparation_task pt ON c.chef_id = pt.chef_id 
                AND pt.priority_level >= 4 
                AND pt.status IN ('Pending', 'In-Prep')
            WHERE EXISTS (
                SELECT 1 FROM public.preparation_task
                WHERE chef_id = c.chef_id AND priority_level >= 4 AND status IN ('Pending', 'In-Prep')
            )
            GROUP BY c.chef_id, c.first_name, c.last_name, c.specialization
            ORDER BY high_priority_tasks DESC;
        """
        self.result_table.set_columns(("Chef ID", "Chef Name", "Specialization", "High Priority Tasks"))
        self.result_table.populate_data(query)

    def run_query_3(self):
        query = """
            SELECT 
                ko.kitchen_order_id, ko.order_id, ks.station_name,
                ko.start_time, ko.finish_time,
                CAST(DATE_TRUNC('day', ko.start_time) AS DATE) as order_date,
                ROUND(EXTRACT(EPOCH FROM (ko.finish_time - ko.start_time)) / 60.0, 2) as preparation_minutes,
                CASE 
                    WHEN ROUND(EXTRACT(EPOCH FROM (ko.finish_time - ko.start_time)) / 60.0, 2) > 60 THEN 'Slow (>60 min)'
                    WHEN ROUND(EXTRACT(EPOCH FROM (ko.finish_time - ko.start_time)) / 60.0, 2) > 30 THEN 'Medium (30-60 min)'
                    ELSE 'Fast (<30 min)'
                END as duration_category
            FROM public.kitchen_order ko
            JOIN public.kitchen_station ks ON ko.station_id = ks.station_id
            WHERE ko.finish_time IS NOT NULL AND ko.status IN ('Ready', 'Served')
            ORDER BY preparation_minutes DESC;
        """
        self.result_table.set_columns(("Kitchen Order ID", "Order ID", "Station Name", "Start Time", "Finish Time", "Order Date", "Prep (Mins)", "Category"))
        self.result_table.populate_data(query)

    def run_query_4(self):
        query = """
            SELECT 
                ks.station_id, ks.station_name,
                DATE_TRUNC('month', ko.start_time)::DATE as month_start,
                COUNT(DISTINCT ko.kitchen_order_id) as total_orders,
                SUM(CASE WHEN ko.status = 'Served' THEN 1 ELSE 0 END) as completed_orders,
                ROUND(AVG(EXTRACT(EPOCH FROM (ko.finish_time - ko.start_time)) / 60.0), 2) as avg_prep_time_minutes
            FROM public.kitchen_order ko
            JOIN public.kitchen_station ks ON ko.station_id = ks.station_id
            WHERE ko.finish_time IS NOT NULL
            GROUP BY ks.station_id, ks.station_name, DATE_TRUNC('month', ko.start_time)
            ORDER BY month_start DESC, ks.station_id;
        """
        self.result_table.set_columns(("Station ID", "Station Name", "Month Start", "Total Orders", "Completed", "Avg Prep Time (Min)"))
        self.result_table.populate_data(query)

    def run_query_5(self):
        query = """
            SELECT 
                ks.station_id, ks.station_name,
                EXTRACT(YEAR FROM hi.inspection_date) as inspection_year,
                EXTRACT(MONTH FROM hi.inspection_date) as inspection_month,
                COUNT(hi.inspection_id) as total_inspections,
                ROUND(AVG(hi.cleanliness_score), 2) as avg_score,
                MIN(hi.cleanliness_score) as min_score,
                MAX(hi.cleanliness_score) as max_score
            FROM public.hygiene_inspection hi
            JOIN public.kitchen_station ks ON hi.station_id = ks.station_id
            WHERE hi.inspection_date IS NOT NULL
            GROUP BY ks.station_id, ks.station_name, EXTRACT(YEAR FROM hi.inspection_date), EXTRACT(MONTH FROM hi.inspection_date)
            ORDER BY inspection_year DESC, inspection_month DESC, ks.station_id;
        """
        self.result_table.set_columns(("Station ID", "Station Name", "Year", "Month", "Total Inspections", "Avg Score", "Min Score", "Max Score"))
        self.result_table.populate_data(query)

    def run_query_6(self):
        query = """
            SELECT 
                c.chef_id, CONCAT(c.first_name, ' ', c.last_name) as chef_name, c.specialization,
                EXTRACT(YEAR FROM fpl.prep_date) as work_year,
                EXTRACT(MONTH FROM fpl.prep_date) as work_month,
                COUNT(fpl.log_id) as total_items_prepped,
                ROUND(AVG(fpl.preparation_time), 2) as avg_prep_time_minutes,
                MIN(fpl.preparation_time) as fastest_prep,
                MAX(fpl.preparation_time) as slowest_prep
            FROM public.food_prep_log fpl
            JOIN public.chef c ON fpl.chef_id = c.chef_id
            WHERE fpl.prep_date IS NOT NULL
            GROUP BY c.chef_id, c.first_name, c.last_name, c.specialization, EXTRACT(YEAR FROM fpl.prep_date), EXTRACT(MONTH FROM fpl.prep_date)
            HAVING COUNT(fpl.log_id) > 5
            ORDER BY work_year DESC, work_month DESC, avg_prep_time_minutes ASC;
        """
        self.result_table.set_columns(("Chef ID", "Chef Name", "Specialty", "Year", "Month", "Total Items Prepped", "Avg Prep Time", "Fastest", "Slowest"))
        self.result_table.populate_data(query)

    def run_query_7(self):
        query = """
            SELECT 
                ks.station_name, pt.task_id,
                CONCAT(c.first_name, ' ', c.last_name) as chef_name,
                pt.task_description, pt.priority_level, pt.status,
                ko.kitchen_order_id,
                ROUND(EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - ko.start_time)) / 60.0, 2) as minutes_elapsed
            FROM public.preparation_task pt
            JOIN public.kitchen_order ko ON pt.kitchen_order_id = ko.kitchen_order_id
            JOIN public.kitchen_station ks ON ko.station_id = ks.station_id
            JOIN public.chef c ON pt.chef_id = c.chef_id
            WHERE pt.status IN ('Pending', 'In-Prep') AND pt.priority_level >= 3
            ORDER BY pt.priority_level DESC, ko.start_time ASC;
        """
        self.result_table.set_columns(("Station Name", "Task ID", "Chef Name", "Description", "Priority", "Status", "Order ID", "Mins Elapsed"))
        self.result_table.populate_data(query)

    def run_query_8(self):
        query = """
            SELECT 
                hi.inspection_id, ks.station_name,
                hi.inspection_date, hi.temperature_check,
                CONCAT(c.first_name, ' ', c.last_name) as inspector_name,
                hi.comments,
                CASE 
                    WHEN hi.temperature_check < 5 THEN 'Fridge OK'
                    WHEN hi.temperature_check BETWEEN 5 AND 15 THEN 'Fridge WARM - Risk'
                    WHEN hi.temperature_check > 15 THEN 'Fridge HOT - Critical'
                    WHEN hi.temperature_check < -15 THEN 'Freezer OK'
                    ELSE 'Normal Range'
                END as temperature_alert
            FROM public.hygiene_inspection hi
            JOIN public.kitchen_station ks ON hi.station_id = ks.station_id
            JOIN public.chef c ON hi.inspector_id = c.chef_id
            WHERE hi.temperature_check IS NOT NULL
            ORDER BY 
                CASE 
                    WHEN hi.temperature_check > 15 THEN 1
                    WHEN hi.temperature_check BETWEEN 5 AND 15 THEN 2
                    ELSE 3
                END,
                hi.inspection_date DESC;
        """
        self.result_table.set_columns(("Inspection ID", "Station Name", "Date", "Temp", "Inspector", "Comments", "Temp Alert"))
        self.result_table.populate_data(query)