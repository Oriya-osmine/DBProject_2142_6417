import customtkinter as ctk
from tkinter import messagebox
import shared

class BaseCrudTab(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
    
    def exec_dml(self, query, params, success_msg, refresh_func):
        try:
            conn = shared.get_db_connection()
            cur = conn.cursor()
            cur.execute(query, params)
            conn.commit()
            cur.close()
            conn.close()
            messagebox.showinfo("Success", success_msg)
            refresh_func()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def confirm_delete(self):
        return messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this record? This action cannot be undone.")

class CrudFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        top_bar = ctk.CTkFrame(self, height=50, fg_color="transparent")
        top_bar.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(top_bar, text="Database Management (CRUD)", font=ctk.CTkFont(size=20, weight="bold")).pack(side="left", padx=10)

        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.tab_chefs = self.tabs.add("Chefs")
        self.tab_stations = self.tabs.add("Kitchen Stations")
        self.tab_orders = self.tabs.add("Kitchen Orders")
        self.tab_menu = self.tabs.add("Menu Items")
        self.tab_tasks = self.tabs.add("Preparation Tasks")
        self.tab_hygiene = self.tabs.add("Hygiene Inspections")
        self.tab_logs = self.tabs.add("Food Prep Logs")
        
        self.setup_chefs_crud()
        self.setup_stations_crud()
        self.setup_orders_crud()
        self.setup_menu_crud()
        self.setup_tasks_crud()
        self.setup_hygiene_crud()
        self.setup_logs_crud()

    def refresh_all_tabs(self):
        self.load_chefs()
        self.load_stations()
        self.load_orders()
        self.load_menu()
        self.load_tasks()
        self.load_hygiene()
        self.load_logs()

    # --- CHEFS CRUD ---
    def setup_chefs_crud(self):
        self.chef_tab_logic = BaseCrudTab(self.tab_chefs)
        cols = ("Chef ID", "First Name", "Last Name", "Specialty", "Station Name", "On Shift?")
        self.chefs_table = shared.GenericDataTable(self.tab_chefs, columns=cols)
        self.chefs_table.pack(pady=10, fill="x")
        
        form_frame = ctk.CTkFrame(self.tab_chefs)
        form_frame.pack(pady=10, fill="x")

        self.chef_id_entry = ctk.CTkEntry(form_frame, placeholder_text="Chef ID (Update/Del)")
        self.chef_id_entry.grid(row=0, column=0, padx=10, pady=10)
        ctk.CTkButton(form_frame, text="Load Data", command=self.fetch_chef).grid(row=0, column=1, padx=10, pady=10)

        self.c_fname = ctk.CTkEntry(form_frame, placeholder_text="First Name")
        self.c_fname.grid(row=1, column=0, padx=10, pady=10)
        self.c_lname = ctk.CTkEntry(form_frame, placeholder_text="Last Name")
        self.c_lname.grid(row=1, column=1, padx=10, pady=10)
        self.c_spec = ctk.CTkEntry(form_frame, placeholder_text="Specialization")
        self.c_spec.grid(row=1, column=2, padx=10, pady=10)
        
        self.station_map = {}
        self.c_station_cb = ctk.CTkComboBox(form_frame, values=["None"])
        self.c_station_cb.set("None")
        self.c_station_cb.grid(row=1, column=3, padx=10, pady=10)

        btn_frame = ctk.CTkFrame(self.tab_chefs, fg_color="transparent")
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Insert", fg_color="green", command=self.insert_chef).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Update", fg_color="#b8860b", command=self.update_chef).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Delete", fg_color="red", command=self.delete_chef).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Refresh", command=self.load_chefs).pack(side="left", padx=5)

    def load_chefs(self):
        try:
            self.station_map = shared.fetch_fk_mapping("SELECT station_name, station_id FROM public.kitchen_station")
            self.c_station_cb.configure(values=["None"] + list(self.station_map.keys()))
        except: pass

        query = """
            SELECT c.chef_id, c.first_name, c.last_name, c.specialization, 
                   COALESCE(ks.station_name, 'None'), c.is_on_shift
            FROM public.chef c
            LEFT JOIN public.kitchen_station ks ON c.current_station_id = ks.station_id
            ORDER BY c.chef_id;
        """
        self.chefs_table.populate_data(query)

    def fetch_chef(self):
        chef_id = self.chef_id_entry.get()
        if not chef_id: return
        try:
            conn = shared.get_db_connection(); cur = conn.cursor()
            cur.execute("""
                SELECT c.first_name, c.last_name, c.specialization, ks.station_name 
                FROM public.chef c LEFT JOIN public.kitchen_station ks ON c.current_station_id = ks.station_id 
                WHERE c.chef_id = %s
            """, (chef_id,))
            row = cur.fetchone()
            if row:
                self.c_fname.delete(0, 'end'); self.c_fname.insert(0, row[0])
                self.c_lname.delete(0, 'end'); self.c_lname.insert(0, row[1])
                self.c_spec.delete(0, 'end'); self.c_spec.insert(0, shared.format_value(row[2]))
                self.c_station_cb.set(row[3] if row[3] else "None")
            else: messagebox.showerror("Error", "Chef not found")
        except Exception as e: messagebox.showerror("Error", str(e))

    def insert_chef(self):
        if not self.c_fname.get() or not self.c_lname.get():
            messagebox.showwarning("Validation Error", "First and Last name are required.")
            return
        st_id = self.station_map.get(self.c_station_cb.get())
        q = "INSERT INTO public.chef (first_name, last_name, specialization, current_station_id, hire_date) VALUES (%s, %s, %s, %s, CURRENT_DATE)"
        self.chef_tab_logic.exec_dml(q, (self.c_fname.get(), self.c_lname.get(), self.c_spec.get(), st_id), "Inserted successfully", self.load_chefs)

    def update_chef(self):
        st_id = self.station_map.get(self.c_station_cb.get())
        q = "UPDATE public.chef SET first_name=%s, last_name=%s, specialization=%s, current_station_id=%s WHERE chef_id=%s"
        self.chef_tab_logic.exec_dml(q, (self.c_fname.get(), self.c_lname.get(), self.c_spec.get(), st_id, self.chef_id_entry.get()), "Updated successfully", self.load_chefs)

    def delete_chef(self):
        if self.chef_tab_logic.confirm_delete():
            self.chef_tab_logic.exec_dml("DELETE FROM public.chef WHERE chef_id=%s", (self.chef_id_entry.get(),), "Deleted successfully", self.load_chefs)

    # --- STATIONS CRUD ---
    def setup_stations_crud(self):
        self.st_tab_logic = BaseCrudTab(self.tab_stations)
        self.stations_table = shared.GenericDataTable(self.tab_stations, columns=("Station ID", "Station Name", "Description", "Active"))
        self.stations_table.pack(pady=10, fill="x")
        
        f = ctk.CTkFrame(self.tab_stations)
        f.pack(pady=10, fill="x")
        self.st_id_entry = ctk.CTkEntry(f, placeholder_text="Station ID")
        self.st_id_entry.grid(row=0, column=0, padx=10, pady=10)
        ctk.CTkButton(f, text="Load Data", command=self.fetch_station).grid(row=0, column=1, padx=10, pady=10)

        self.st_name = ctk.CTkEntry(f, placeholder_text="Station Name")
        self.st_name.grid(row=1, column=0, padx=10, pady=10)
        self.st_desc = ctk.CTkEntry(f, placeholder_text="Description", width=300)
        self.st_desc.grid(row=1, column=1, columnspan=2, padx=10, pady=10)

        bf = ctk.CTkFrame(self.tab_stations, fg_color="transparent")
        bf.pack(pady=10)
        ctk.CTkButton(bf, text="Insert", fg_color="green", command=self.insert_station).pack(side="left", padx=5)
        ctk.CTkButton(bf, text="Update", fg_color="#b8860b", command=self.update_station).pack(side="left", padx=5)
        ctk.CTkButton(bf, text="Delete", fg_color="red", command=self.delete_station).pack(side="left", padx=5)
        ctk.CTkButton(bf, text="Refresh", command=self.load_stations).pack(side="left", padx=5)

    def fetch_station(self):
        st_id = self.st_id_entry.get()
        if not st_id: return
        try:
            conn = shared.get_db_connection(); cur = conn.cursor()
            cur.execute("SELECT station_name, description FROM public.kitchen_station WHERE station_id = %s", (st_id,))
            row = cur.fetchone()
            if row:
                self.st_name.delete(0, 'end'); self.st_name.insert(0, row[0])
                self.st_desc.delete(0, 'end'); self.st_desc.insert(0, shared.format_value(row[1]))
            else: messagebox.showerror("Error", "Station not found")
        except Exception as e: messagebox.showerror("Error", str(e))

    def load_stations(self):
        self.stations_table.populate_data("SELECT station_id, station_name, description, is_active FROM public.kitchen_station ORDER BY station_id")

    def insert_station(self):
        if not self.st_name.get():
            messagebox.showwarning("Validation Error", "Station Name is required.")
            return
        self.st_tab_logic.exec_dml("INSERT INTO public.kitchen_station (station_name, description) VALUES (%s, %s)", (self.st_name.get(), self.st_desc.get()), "Inserted", self.load_stations)

    def update_station(self):
        self.st_tab_logic.exec_dml("UPDATE public.kitchen_station SET station_name=%s, description=%s WHERE station_id=%s", (self.st_name.get(), self.st_desc.get(), self.st_id_entry.get()), "Updated", self.load_stations)

    def delete_station(self):
        if self.st_tab_logic.confirm_delete():
            self.st_tab_logic.exec_dml("DELETE FROM public.kitchen_station WHERE station_id=%s", (self.st_id_entry.get(),), "Deleted", self.load_stations)

    # --- KITCHEN ORDERS CRUD ---
    def setup_orders_crud(self):
        self.ko_tab_logic = BaseCrudTab(self.tab_orders)
        self.ko_table = shared.GenericDataTable(self.tab_orders, columns=("Kitchen Order ID", "Ext. Order ID", "Status", "Station Name"))
        self.ko_table.pack(pady=10, fill="x")
        
        f = ctk.CTkFrame(self.tab_orders)
        f.pack(pady=10, fill="x")
        
        self.ko_id_entry = ctk.CTkEntry(f, placeholder_text="Kitchen Order ID")
        self.ko_id_entry.grid(row=0, column=0, padx=10, pady=10)
        ctk.CTkButton(f, text="Load Data", command=self.fetch_order).grid(row=0, column=1, padx=10, pady=10)

        self.ko_ext_id = ctk.CTkEntry(f, placeholder_text="External Order ID")
        self.ko_ext_id.grid(row=1, column=0, padx=10, pady=10)
        
        self.ko_status_cb = ctk.CTkComboBox(f, values=['Pending', 'In-Prep', 'Ready', 'Served', 'Cancelled'])
        self.ko_status_cb.grid(row=1, column=1, padx=10, pady=10)
        
        self.ko_station_cb = ctk.CTkComboBox(f, values=["None"])
        self.ko_station_cb.set("None")
        self.ko_station_cb.grid(row=1, column=2, padx=10, pady=10)

        bf = ctk.CTkFrame(self.tab_orders, fg_color="transparent")
        bf.pack(pady=10)
        ctk.CTkButton(bf, text="Insert", fg_color="green", command=self.insert_order).pack(side="left", padx=5)
        ctk.CTkButton(bf, text="Update", fg_color="#b8860b", command=self.update_order).pack(side="left", padx=5)
        ctk.CTkButton(bf, text="Delete", fg_color="red", command=self.delete_order).pack(side="left", padx=5)
        ctk.CTkButton(bf, text="Refresh", command=self.load_orders).pack(side="left", padx=5)

    def fetch_order(self):
        ko_id = self.ko_id_entry.get()
        if not ko_id: return
        try:
            conn = shared.get_db_connection(); cur = conn.cursor()
            cur.execute("""
                SELECT ko.order_id, ko.status, ks.station_name 
                FROM public.kitchen_order ko LEFT JOIN public.kitchen_station ks ON ko.station_id = ks.station_id
                WHERE ko.kitchen_order_id = %s
            """, (ko_id,))
            row = cur.fetchone()
            if row:
                self.ko_ext_id.delete(0, 'end'); self.ko_ext_id.insert(0, str(row[0]))
                self.ko_status_cb.set(row[1])
                self.ko_station_cb.set(row[2] if row[2] else "None")
        except Exception as e: messagebox.showerror("Error", str(e))

    def load_orders(self):
        try:
            self.ko_station_map = shared.fetch_fk_mapping("SELECT station_name, station_id FROM public.kitchen_station")
            self.ko_station_cb.configure(values=["None"] + list(self.ko_station_map.keys()))
        except: pass
        query = """
            SELECT ko.kitchen_order_id, ko.order_id, ko.status, COALESCE(ks.station_name, 'None')
            FROM public.kitchen_order ko LEFT JOIN public.kitchen_station ks ON ko.station_id = ks.station_id
            ORDER BY ko.kitchen_order_id DESC LIMIT 100;
        """
        self.ko_table.populate_data(query)

    def insert_order(self):
        st_id = self.ko_station_map.get(self.ko_station_cb.get())
        if not self.ko_ext_id.get(): return messagebox.showwarning("Validation Error", "Ext Order ID needed.")
        self.ko_tab_logic.exec_dml("INSERT INTO public.kitchen_order (order_id, status, station_id) VALUES (%s, %s, %s)", (self.ko_ext_id.get(), self.ko_status_cb.get(), st_id), "Inserted", self.load_orders)

    def update_order(self):
        st_id = self.ko_station_map.get(self.ko_station_cb.get())
        self.ko_tab_logic.exec_dml("UPDATE public.kitchen_order SET order_id=%s, status=%s, station_id=%s WHERE kitchen_order_id=%s", (self.ko_ext_id.get(), self.ko_status_cb.get(), st_id, self.ko_id_entry.get()), "Updated", self.load_orders)

    def delete_order(self):
        if self.ko_tab_logic.confirm_delete():
            self.ko_tab_logic.exec_dml("DELETE FROM public.kitchen_order WHERE kitchen_order_id=%s", (self.ko_id_entry.get(),), "Deleted", self.load_orders)

    # --- MENU ITEMS CRUD ---
    def setup_menu_crud(self):
        self.menu_logic = BaseCrudTab(self.tab_menu)
        self.menu_table = shared.GenericDataTable(self.tab_menu, columns=("Menu ID", "Item Name", "Price", "Available"))
        self.menu_table.pack(pady=10, fill="x")
        
        f = ctk.CTkFrame(self.tab_menu)
        f.pack(pady=10, fill="x")
        
        self.mi_id_entry = ctk.CTkEntry(f, placeholder_text="Menu Item ID")
        self.mi_id_entry.grid(row=0, column=0, padx=10, pady=10)
        ctk.CTkButton(f, text="Load Data", command=self.fetch_menu).grid(row=0, column=1, padx=10, pady=10)

        self.mi_name = ctk.CTkEntry(f, placeholder_text="Item Name")
        self.mi_name.grid(row=1, column=0, padx=10, pady=10)
        self.mi_price = ctk.CTkEntry(f, placeholder_text="Price")
        self.mi_price.grid(row=1, column=1, padx=10, pady=10)
        self.mi_avail = ctk.CTkComboBox(f, values=["True", "False"])
        self.mi_avail.grid(row=1, column=2, padx=10, pady=10)

        bf = ctk.CTkFrame(self.tab_menu, fg_color="transparent")
        bf.pack(pady=10)
        ctk.CTkButton(bf, text="Insert", fg_color="green", command=self.insert_menu).pack(side="left", padx=5)
        ctk.CTkButton(bf, text="Update", fg_color="#b8860b", command=self.update_menu).pack(side="left", padx=5)
        ctk.CTkButton(bf, text="Delete", fg_color="red", command=self.delete_menu).pack(side="left", padx=5)
        ctk.CTkButton(bf, text="Refresh", command=self.load_menu).pack(side="left", padx=5)

    def fetch_menu(self):
        m_id = self.mi_id_entry.get()
        if not m_id: return
        try:
            conn = shared.get_db_connection(); cur = conn.cursor()
            cur.execute("SELECT item_name, price, is_available FROM partners.menu_item WHERE menu_item_id = %s", (m_id,))
            row = cur.fetchone()
            if row:
                self.mi_name.delete(0, 'end'); self.mi_name.insert(0, row[0])
                self.mi_price.delete(0, 'end'); self.mi_price.insert(0, shared.format_value(row[1]))
                self.mi_avail.set(str(row[2]))
        except Exception as e: messagebox.showerror("Error", str(e))

    def load_menu(self):
        self.menu_table.populate_data("SELECT menu_item_id, item_name, price, is_available FROM partners.menu_item ORDER BY menu_item_id LIMIT 100")

    def insert_menu(self):
        self.menu_logic.exec_dml("INSERT INTO partners.menu_item (item_name, price, is_available, category_id) VALUES (%s, %s, %s, 1)", (self.mi_name.get(), self.mi_price.get(), self.mi_avail.get() == "True"), "Inserted", self.load_menu)

    def update_menu(self):
        self.menu_logic.exec_dml("UPDATE partners.menu_item SET item_name=%s, price=%s, is_available=%s WHERE menu_item_id=%s", (self.mi_name.get(), self.mi_price.get(), self.mi_avail.get() == "True", self.mi_id_entry.get()), "Updated", self.load_menu)

    def delete_menu(self):
        if self.menu_logic.confirm_delete():
            self.menu_logic.exec_dml("DELETE FROM partners.menu_item WHERE menu_item_id=%s", (self.mi_id_entry.get(),), "Deleted", self.load_menu)

    # --- PREPARATION TASKS CRUD ---
    def setup_tasks_crud(self):
        self.task_logic = BaseCrudTab(self.tab_tasks)
        self.task_table = shared.GenericDataTable(self.tab_tasks, columns=("Task ID", "Order ID", "Chef Name", "Description", "Status", "Priority"))
        self.task_table.pack(pady=10, fill="x")
        
        f = ctk.CTkFrame(self.tab_tasks)
        f.pack(pady=10, fill="x")
        
        self.tk_id_entry = ctk.CTkEntry(f, placeholder_text="Task ID")
        self.tk_id_entry.grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkButton(f, text="Load Data", command=self.fetch_task).grid(row=0, column=1, padx=5, pady=5)

        self.tk_order_id = ctk.CTkEntry(f, placeholder_text="Kitchen Order ID")
        self.tk_order_id.grid(row=1, column=0, padx=5, pady=5)
        
        self.tk_desc = ctk.CTkEntry(f, placeholder_text="Task Description", width=200)
        self.tk_desc.grid(row=1, column=1, padx=5, pady=5)
        
        self.tk_status_cb = ctk.CTkComboBox(f, values=['Pending', 'In-Prep', 'Ready', 'Completed'])
        self.tk_status_cb.grid(row=1, column=2, padx=5, pady=5)
        
        self.tk_priority = ctk.CTkEntry(f, placeholder_text="Priority (1-5)")
        self.tk_priority.grid(row=1, column=3, padx=5, pady=5)

        self.tk_chef_map = {}
        self.tk_chef_cb = ctk.CTkComboBox(f, values=["None"])
        self.tk_chef_cb.set("None")
        self.tk_chef_cb.grid(row=1, column=4, padx=5, pady=5)

        bf = ctk.CTkFrame(self.tab_tasks, fg_color="transparent")
        bf.pack(pady=10)
        ctk.CTkButton(bf, text="Insert", fg_color="green", command=self.insert_task).pack(side="left", padx=5)
        ctk.CTkButton(bf, text="Update", fg_color="#b8860b", command=self.update_task).pack(side="left", padx=5)
        ctk.CTkButton(bf, text="Delete", fg_color="red", command=self.delete_task).pack(side="left", padx=5)
        ctk.CTkButton(bf, text="Refresh", command=self.load_tasks).pack(side="left", padx=5)

    def fetch_task(self):
        t_id = self.tk_id_entry.get()
        if not t_id: return
        try:
            conn = shared.get_db_connection(); cur = conn.cursor()
            cur.execute("""
                SELECT pt.kitchen_order_id, pt.task_description, pt.status, pt.priority_level, c.first_name || ' ' || c.last_name 
                FROM public.preparation_task pt LEFT JOIN public.chef c ON pt.chef_id = c.chef_id
                WHERE pt.task_id = %s
            """, (t_id,))
            row = cur.fetchone()
            if row:
                self.tk_order_id.delete(0, 'end'); self.tk_order_id.insert(0, str(row[0]))
                self.tk_desc.delete(0, 'end'); self.tk_desc.insert(0, row[1])
                self.tk_status_cb.set(row[2])
                self.tk_priority.delete(0, 'end'); self.tk_priority.insert(0, str(row[3]))
                self.tk_chef_cb.set(row[4] if row[4] else "None")
        except Exception as e: messagebox.showerror("Error", str(e))

    def load_tasks(self):
        try:
            self.tk_chef_map = shared.fetch_fk_mapping("SELECT first_name || ' ' || last_name, chef_id FROM public.chef")
            self.tk_chef_cb.configure(values=["None"] + list(self.tk_chef_map.keys()))
        except: pass
        query = """
            SELECT pt.task_id, pt.kitchen_order_id, COALESCE(c.first_name || ' ' || c.last_name, 'Unassigned'), pt.task_description, pt.status, pt.priority_level
            FROM public.preparation_task pt LEFT JOIN public.chef c ON pt.chef_id = c.chef_id
            ORDER BY pt.task_id DESC LIMIT 100;
        """
        self.task_table.populate_data(query)

    def insert_task(self):
        c_id = self.tk_chef_map.get(self.tk_chef_cb.get())
        self.task_logic.exec_dml("INSERT INTO public.preparation_task (kitchen_order_id, chef_id, task_description, status, priority_level) VALUES (%s, %s, %s, %s, %s)", 
                                 (self.tk_order_id.get(), c_id, self.tk_desc.get(), self.tk_status_cb.get(), self.tk_priority.get()), "Inserted", self.load_tasks)

    def update_task(self):
        c_id = self.tk_chef_map.get(self.tk_chef_cb.get())
        self.task_logic.exec_dml("UPDATE public.preparation_task SET kitchen_order_id=%s, chef_id=%s, task_description=%s, status=%s, priority_level=%s WHERE task_id=%s", 
                                 (self.tk_order_id.get(), c_id, self.tk_desc.get(), self.tk_status_cb.get(), self.tk_priority.get(), self.tk_id_entry.get()), "Updated", self.load_tasks)

    def delete_task(self):
        if self.task_logic.confirm_delete():
            self.task_logic.exec_dml("DELETE FROM public.preparation_task WHERE task_id=%s", (self.tk_id_entry.get(),), "Deleted", self.load_tasks)

    # --- HYGIENE INSPECTIONS CRUD ---
    def setup_hygiene_crud(self):
        self.hygiene_logic = BaseCrudTab(self.tab_hygiene)
        self.hyg_table = shared.GenericDataTable(self.tab_hygiene, columns=("ID", "Station", "Inspector", "Date", "Score", "Status"))
        self.hyg_table.pack(pady=10, fill="x")
        
        f = ctk.CTkFrame(self.tab_hygiene)
        f.pack(pady=10, fill="x")
        
        self.hyg_id_entry = ctk.CTkEntry(f, placeholder_text="Inspection ID")
        self.hyg_id_entry.grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkButton(f, text="Load Data", command=self.fetch_hygiene).grid(row=0, column=1, padx=5, pady=5)

        self.hyg_score = ctk.CTkEntry(f, placeholder_text="Score (1.0-10.0)")
        self.hyg_score.grid(row=1, column=0, padx=5, pady=5)
        
        self.hyg_status_cb = ctk.CTkComboBox(f, values=['Perfect condition', 'Passed inspection', 'Needs improvement'])
        self.hyg_status_cb.grid(row=1, column=1, padx=5, pady=5)
        
        self.hyg_st_map = {}
        self.hyg_c_map = {}

        self.hyg_station_cb = ctk.CTkComboBox(f, values=["None"])
        self.hyg_station_cb.grid(row=1, column=2, padx=5, pady=5)
        
        self.hyg_inspector_cb = ctk.CTkComboBox(f, values=["None"])
        self.hyg_inspector_cb.grid(row=1, column=3, padx=5, pady=5)

        bf = ctk.CTkFrame(self.tab_hygiene, fg_color="transparent")
        bf.pack(pady=10)
        ctk.CTkButton(bf, text="Insert", fg_color="green", command=self.insert_hygiene).pack(side="left", padx=5)
        ctk.CTkButton(bf, text="Update", fg_color="#b8860b", command=self.update_hygiene).pack(side="left", padx=5)
        ctk.CTkButton(bf, text="Delete", fg_color="red", command=self.delete_hygiene).pack(side="left", padx=5)
        ctk.CTkButton(bf, text="Refresh", command=self.load_hygiene).pack(side="left", padx=5)

    def fetch_hygiene(self):
        h_id = self.hyg_id_entry.get()
        if not h_id: return
        try:
            conn = shared.get_db_connection(); cur = conn.cursor()
            cur.execute("""
                SELECT h.cleanliness_score, h.status, ks.station_name, c.first_name || ' ' || c.last_name
                FROM public.hygiene_inspection h 
                JOIN public.kitchen_station ks ON h.station_id = ks.station_id
                JOIN public.chef c ON h.inspector_id = c.chef_id
                WHERE h.inspection_id = %s
            """, (h_id,))
            row = cur.fetchone()
            if row:
                self.hyg_score.delete(0, 'end'); self.hyg_score.insert(0, str(row[0]))
                self.hyg_status_cb.set(row[1])
                self.hyg_station_cb.set(row[2])
                self.hyg_inspector_cb.set(row[3])
        except Exception as e: messagebox.showerror("Error", str(e))

    def load_hygiene(self):
        try:
            self.hyg_st_map = shared.fetch_fk_mapping("SELECT station_name, station_id FROM public.kitchen_station")
            self.hyg_c_map = shared.fetch_fk_mapping("SELECT first_name || ' ' || last_name, chef_id FROM public.chef")
            self.hyg_station_cb.configure(values=list(self.hyg_st_map.keys()))
            self.hyg_inspector_cb.configure(values=list(self.hyg_c_map.keys()))
        except: pass

        query = """
            SELECT h.inspection_id, ks.station_name, c.first_name || ' ' || c.last_name, h.inspection_date, h.cleanliness_score, h.status
            FROM public.hygiene_inspection h 
            JOIN public.kitchen_station ks ON h.station_id = ks.station_id
            JOIN public.chef c ON h.inspector_id = c.chef_id
            ORDER BY h.inspection_id DESC LIMIT 50;
        """
        self.hyg_table.populate_data(query)

    def insert_hygiene(self):
        self.hygiene_logic.exec_dml("INSERT INTO public.hygiene_inspection (station_id, inspector_id, cleanliness_score, status) VALUES (%s, %s, %s, %s)", 
                                 (self.hyg_st_map.get(self.hyg_station_cb.get()), self.hyg_c_map.get(self.hyg_inspector_cb.get()), self.hyg_score.get(), self.hyg_status_cb.get()), "Inserted", self.load_hygiene)

    def update_hygiene(self):
        self.hygiene_logic.exec_dml("UPDATE public.hygiene_inspection SET station_id=%s, inspector_id=%s, cleanliness_score=%s, status=%s WHERE inspection_id=%s", 
                                 (self.hyg_st_map.get(self.hyg_station_cb.get()), self.hyg_c_map.get(self.hyg_inspector_cb.get()), self.hyg_score.get(), self.hyg_status_cb.get(), self.hyg_id_entry.get()), "Updated", self.load_hygiene)

    def delete_hygiene(self):
        if self.hygiene_logic.confirm_delete():
            self.hygiene_logic.exec_dml("DELETE FROM public.hygiene_inspection WHERE inspection_id=%s", (self.hyg_id_entry.get(),), "Deleted", self.load_hygiene)

    # --- FOOD PREP LOGS CRUD ---
    def setup_logs_crud(self):
        self.log_logic = BaseCrudTab(self.tab_logs)
        self.log_table = shared.GenericDataTable(self.tab_logs, columns=("Log ID", "Chef", "Menu Item", "Prep Time (min)", "Date"))
        self.log_table.pack(pady=10, fill="x")
        
        f = ctk.CTkFrame(self.tab_logs)
        f.pack(pady=10, fill="x")
        
        self.lg_id_entry = ctk.CTkEntry(f, placeholder_text="Log ID")
        self.lg_id_entry.grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkButton(f, text="Load Data", command=self.fetch_log).grid(row=0, column=1, padx=5, pady=5)

        self.lg_time = ctk.CTkEntry(f, placeholder_text="Prep Time (mins)")
        self.lg_time.grid(row=1, column=0, padx=5, pady=5)
        
        self.lg_notes = ctk.CTkEntry(f, placeholder_text="Notes", width=200)
        self.lg_notes.grid(row=1, column=1, padx=5, pady=5)

        self.lg_c_map = {}
        self.lg_m_map = {}

        self.lg_chef_cb = ctk.CTkComboBox(f, values=["None"])
        self.lg_chef_cb.grid(row=1, column=2, padx=5, pady=5)
        
        self.lg_menu_cb = ctk.CTkComboBox(f, values=["None"])
        self.lg_menu_cb.grid(row=1, column=3, padx=5, pady=5)

        bf = ctk.CTkFrame(self.tab_logs, fg_color="transparent")
        bf.pack(pady=10)
        ctk.CTkButton(bf, text="Insert", fg_color="green", command=self.insert_log).pack(side="left", padx=5)
        ctk.CTkButton(bf, text="Update", fg_color="#b8860b", command=self.update_log).pack(side="left", padx=5)
        ctk.CTkButton(bf, text="Delete", fg_color="red", command=self.delete_log).pack(side="left", padx=5)
        ctk.CTkButton(bf, text="Refresh", command=self.load_logs).pack(side="left", padx=5)

    def fetch_log(self):
        l_id = self.lg_id_entry.get()
        if not l_id: return
        try:
            conn = shared.get_db_connection(); cur = conn.cursor()
            cur.execute("""
                SELECT l.preparation_time, l.notes, c.first_name || ' ' || c.last_name, m.item_name
                FROM public.food_prep_log l
                JOIN public.chef c ON l.chef_id = c.chef_id
                JOIN partners.menu_item m ON l.menu_item_id = m.menu_item_id
                WHERE l.log_id = %s
            """, (l_id,))
            row = cur.fetchone()
            if row:
                self.lg_time.delete(0, 'end'); self.lg_time.insert(0, str(row[0]))
                self.lg_notes.delete(0, 'end'); self.lg_notes.insert(0, row[1] if row[1] else "")
                self.lg_chef_cb.set(row[2])
                self.lg_menu_cb.set(row[3])
        except Exception as e: messagebox.showerror("Error", str(e))

    def load_logs(self):
        try:
            self.lg_c_map = shared.fetch_fk_mapping("SELECT first_name || ' ' || last_name, chef_id FROM public.chef")
            self.lg_m_map = shared.fetch_fk_mapping("SELECT item_name, menu_item_id FROM partners.menu_item")
            self.lg_chef_cb.configure(values=list(self.lg_c_map.keys()))
            self.lg_menu_cb.configure(values=list(self.lg_m_map.keys()))
        except: pass

        query = """
            SELECT l.log_id, c.first_name || ' ' || c.last_name, m.item_name, l.preparation_time, l.prep_date
            FROM public.food_prep_log l
            JOIN public.chef c ON l.chef_id = c.chef_id
            JOIN partners.menu_item m ON l.menu_item_id = m.menu_item_id
            ORDER BY l.log_id DESC LIMIT 50;
        """
        self.log_table.populate_data(query)

    def insert_log(self):
        self.log_logic.exec_dml("INSERT INTO public.food_prep_log (chef_id, menu_item_id, preparation_time, notes) VALUES (%s, %s, %s, %s)", 
                                 (self.lg_c_map.get(self.lg_chef_cb.get()), self.lg_m_map.get(self.lg_menu_cb.get()), self.lg_time.get(), self.lg_notes.get()), "Inserted", self.load_logs)

    def update_log(self):
        self.log_logic.exec_dml("UPDATE public.food_prep_log SET chef_id=%s, menu_item_id=%s, preparation_time=%s, notes=%s WHERE log_id=%s", 
                                 (self.lg_c_map.get(self.lg_chef_cb.get()), self.lg_m_map.get(self.lg_menu_cb.get()), self.lg_time.get(), self.lg_notes.get(), self.lg_id_entry.get()), "Updated", self.load_logs)

    def delete_log(self):
        if self.log_logic.confirm_delete():
            self.log_logic.exec_dml("DELETE FROM public.food_prep_log WHERE log_id=%s", (self.lg_id_entry.get(),), "Deleted", self.load_logs)