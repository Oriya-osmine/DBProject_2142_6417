import customtkinter as ctk
from tkinter import ttk, messagebox
import psycopg2
from decimal import Decimal

# Global Database Connection Parameters
DB_CONFIG = {
    "dbname": "your_db_name",
    "user": "your_user",
    "password": "your_password",
    "host": "localhost"
}

def get_db_connection():
    conn_params = DB_CONFIG.copy()
    conn_params["connect_timeout"] = 3
    return psycopg2.connect(**conn_params)

def format_value(val):
    if isinstance(val, (float, Decimal)):
        return f"{val:.6f}"
    if val is None:
        return ""
    return str(val)

def fetch_fk_mapping(query):
    mapping = {}
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query)
        for row in cur.fetchall():
            mapping[str(row[0])] = row[1]
        cur.close()
        conn.close()
    except Exception:
        pass
    return mapping

class GenericDataTable(ctk.CTkFrame):
    def __init__(self, master, columns=None, **kwargs):
        super().__init__(master, **kwargs)
        
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2a2d2e", foreground="white", rowheight=25, fieldbackground="#2a2d2e", borderwidth=0)
        style.map('Treeview', background=[('selected', '#1f538d')])
        style.configure("Treeview.Heading", background="#1f538d", foreground="white", relief="flat")

        self.tree = ttk.Treeview(self, show='headings', height=10)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        if columns:
            self.set_columns(columns)

    def set_columns(self, columns):
        self.tree.config(columns=columns)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")

    def populate_data(self, query, params=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(query, params)
            rows = cur.fetchall()
            for row in rows:
                formatted_row = [format_value(val) for val in row]
                self.tree.insert("", "end", values=formatted_row)
            cur.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Query Error", str(e))