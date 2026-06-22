import customtkinter as ctk
import shared

class QueriesFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        top_bar = ctk.CTkFrame(self, height=50, fg_color="transparent")
        top_bar.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(top_bar, text="Reports & SQL Queries (Stage B)", font=ctk.CTkFont(size=20, weight="bold")).pack(side="left", padx=10)
        
        self.result_table = shared.GenericDataTable(self)
        self.result_table.pack(pady=20, fill="both", expand=True, padx=20)
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        q1_btn = ctk.CTkButton(btn_frame, text="Execute Query 1: Stations Workload", width=250, command=self.run_query_1)
        q1_btn.pack(side="left", padx=10)
        
        q2_btn = ctk.CTkButton(btn_frame, text="Execute Query 2: Inactive Stations", width=250, command=self.run_query_2)
        q2_btn.pack(side="left", padx=10)

    def run_query_1(self):
        query = """
            SELECT ks.station_name, COUNT(ko.kitchen_order_id) as total_orders,
                   SUM(CASE WHEN ko.status = 'Pending' THEN 1 ELSE 0 END) as pending_orders
            FROM public.kitchen_station ks
            LEFT JOIN public.kitchen_order ko ON ks.station_id = ko.station_id
            GROUP BY ks.station_name
            ORDER BY total_orders DESC;
        """
        self.result_table.set_columns(("Station Name", "Total Orders", "Pending Orders"))
        self.result_table.populate_data(query)

    def run_query_2(self):
        query = """
            SELECT ks.station_name, ks.description
            FROM public.kitchen_station ks
            WHERE ks.is_active = TRUE 
            AND NOT EXISTS (
                SELECT 1 FROM public.kitchen_order ko 
                WHERE ko.station_id = ks.station_id
            );
        """
        self.result_table.set_columns(("Station Name", "Description"))
        self.result_table.populate_data(query)