import customtkinter as ctk
from tkinter import messagebox
import shared

class AdvancedFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        top_bar = ctk.CTkFrame(self, height=50, fg_color="transparent")
        top_bar.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(top_bar, text="Functions & Procedures (Stage D)", font=ctk.CTkFont(size=20, weight="bold")).pack(side="left", padx=10)

        # 1. Pack the actions frame at the BOTTOM first, without vertical expansion
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.pack(side="bottom", fill="x", padx=10, pady=20)

        # 2. Pack the table in the middle and tell it to EXPAND and fill all remaining space
        self.adv_table = shared.GenericDataTable(self)
        self.adv_table.pack(side="top", fill="both", expand=True, padx=20, pady=(0, 10))

        # --- VIEWS SECTION ---
        view_f = ctk.CTkFrame(actions_frame)
        view_f.pack(side="left", fill="both", expand=True, padx=10)
        ctk.CTkLabel(view_f, text="Views (Stage C)", font=("Arial", 16, "bold")).pack(pady=10)
        ctk.CTkButton(view_f, text="1. Station Responsibilities", command=self.load_view_stations).pack(pady=5)
        ctk.CTkButton(view_f, text="2. Partner Recipe Routing", command=self.load_view_partners).pack(pady=5)

        # --- FUNCTIONS SECTION ---
        func_f = ctk.CTkFrame(actions_frame)
        func_f.pack(side="left", fill="both", expand=True, padx=10)
        ctk.CTkLabel(func_f, text="Functions (Stage D)", font=("Arial", 16, "bold")).pack(pady=10)
        
        f1 = ctk.CTkFrame(func_f, fg_color="transparent")
        f1.pack(pady=5)
        self.wl_chef_id = ctk.CTkEntry(f1, placeholder_text="Chef ID", width=80)
        self.wl_chef_id.pack(side="left", padx=5)
        ctk.CTkButton(f1, text="Calculate Workload", command=self.run_func_workload, width=120).pack(side="left")

        f2 = ctk.CTkFrame(func_f, fg_color="transparent")
        f2.pack(pady=5)
        self.menu_station_id = ctk.CTkEntry(f2, placeholder_text="Station ID", width=80)
        self.menu_station_id.pack(side="left", padx=5)
        ctk.CTkButton(f2, text="Get Station Menu", command=self.run_func_station_menu, width=120).pack(side="left")

        # --- PROCEDURES SECTION ---
        proc_f = ctk.CTkFrame(actions_frame)
        proc_f.pack(side="left", fill="both", expand=True, padx=10)
        ctk.CTkLabel(proc_f, text="Procedures (Stage D)", font=("Arial", 16, "bold")).pack(pady=10)

        p1 = ctk.CTkFrame(proc_f, fg_color="transparent")
        p1.pack(pady=5)
        self.old_chef = ctk.CTkEntry(p1, placeholder_text="Old Chef ID", width=80)
        self.old_chef.pack(side="left", padx=2)
        self.new_chef = ctk.CTkEntry(p1, placeholder_text="New Chef ID", width=80)
        self.new_chef.pack(side="left", padx=2)
        ctk.CTkButton(p1, text="Transfer Tasks", command=self.run_proc_transfer, width=100).pack(side="left", padx=2)

        p2 = ctk.CTkFrame(proc_f, fg_color="transparent")
        p2.pack(pady=5)
        self.disp_order_id = ctk.CTkEntry(p2, placeholder_text="Order ID", width=80)
        self.disp_order_id.pack(side="left", padx=5)
        ctk.CTkButton(p2, text="Dispatch Order", command=self.run_proc_dispatch, width=120).pack(side="left")

    def check_exists(self, table, pk_column, value):
        """ Helper method to pre-validate IDs before calling DB Functions/Procedures """
        try:
            conn = shared.get_db_connection()
            cur = conn.cursor()
            cur.execute(f"SELECT EXISTS(SELECT 1 FROM public.{table} WHERE {pk_column} = %s)", (value,))
            exists = cur.fetchone()[0]
            cur.close()
            conn.close()
            return exists
        except Exception:
            return False

    def load_view_stations(self):
        self.adv_table.set_columns(("Station Name", "Description", "Item Name", "Is Available"))
        self.adv_table.populate_data("SELECT station_name, description, item_name, is_available FROM mappings.view_station_responsibilities LIMIT 50")

    def load_view_partners(self):
        self.adv_table.set_columns(("Category", "Item", "Price", "Instructions", "Prepared At"))
        self.adv_table.populate_data("SELECT category_name, item_name, price, recipe_instructions, prepared_at_station FROM mappings.view_partner_recipe_routing LIMIT 50")

    def run_func_workload(self):
        chef_id = self.wl_chef_id.get()
        if not chef_id: return
        
        # PRE-VALIDATION CHECK
        if not self.check_exists("chef", "chef_id", chef_id):
            messagebox.showwarning("Validation Error", f"Chef ID '{chef_id}' does not exist in the database.")
            return

        try:
            conn = shared.get_db_connection(); cur = conn.cursor()
            cur.execute("SELECT public.calculate_chef_workload(%s)", (chef_id,))
            res = cur.fetchone()[0]
            conn.close()
            messagebox.showinfo("Result", f"Total workload for Chef {chef_id} is: {res}")
        except Exception as e: messagebox.showerror("Error", str(e))

    def run_func_station_menu(self):
        station_id = self.menu_station_id.get()
        if not station_id: return

        # PRE-VALIDATION CHECK
        if not self.check_exists("kitchen_station", "station_id", station_id):
            messagebox.showwarning("Validation Error", f"Station ID '{station_id}' does not exist in the database.")
            return

        try:
            conn = shared.get_db_connection()
            conn.autocommit = False 
            cur = conn.cursor()
            
            cur.execute("SELECT public.get_active_station_menu(%s);", (station_id,))
            cursor_name = cur.fetchone()[0]
            
            cur.execute(f'FETCH ALL FROM "{cursor_name}";')
            rows = cur.fetchall()
            conn.commit()
            conn.close()

            self.adv_table.set_columns(("Station ID", "Station Name", "Menu Item ID", "Item Name", "Price", "Available"))
            for item in self.adv_table.tree.get_children(): self.adv_table.tree.delete(item)
            for row in rows:
                self.adv_table.tree.insert("", "end", values=[shared.format_value(v) for v in row])
        except Exception as e: messagebox.showerror("RefCursor Error", str(e))

    def run_proc_transfer(self):
        old_c = self.old_chef.get()
        new_c = self.new_chef.get()
        if not old_c or not new_c: return

        # PRE-VALIDATION CHECK
        if not self.check_exists("chef", "chef_id", old_c):
            messagebox.showwarning("Validation Error", f"Old Chef ID '{old_c}' does not exist.")
            return
        if not self.check_exists("chef", "chef_id", new_c):
            messagebox.showwarning("Validation Error", f"New Chef ID '{new_c}' does not exist.")
            return

        try:
            conn = shared.get_db_connection(); cur = conn.cursor()
            cur.execute("CALL public.transfer_chef_tasks(%s, %s)", (old_c, new_c))
            conn.commit(); conn.close()
            messagebox.showinfo("Success", "Tasks transferred successfully via Procedure.")
        except Exception as e: messagebox.showerror("Procedure Error", str(e))

    def run_proc_dispatch(self):
        o_id = self.disp_order_id.get()
        if not o_id: return

        # PRE-VALIDATION CHECK
        if not self.check_exists("kitchen_order", "kitchen_order_id", o_id):
            messagebox.showwarning("Validation Error", f"Order ID '{o_id}' does not exist.")
            return

        try:
            conn = shared.get_db_connection(); cur = conn.cursor()
            cur.execute("CALL public.dispatch_kitchen_order(%s)", (o_id,))
            conn.commit(); conn.close()
            messagebox.showinfo("Success", "Order dispatched successfully via Procedure.")
        except Exception as e: messagebox.showerror("Procedure Error", str(e))