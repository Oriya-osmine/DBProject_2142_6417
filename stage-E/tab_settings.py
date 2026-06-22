import customtkinter as ctk
from tkinter import messagebox
import psycopg2
import shared

class SettingsFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        title_label = ctk.CTkLabel(self, text="Database Connection Settings", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=(30, 20))
        
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(pady=20, padx=50, fill="x")
        
        ctk.CTkLabel(form_frame, text="Database Name:").grid(row=0, column=0, padx=20, pady=15, sticky="w")
        self.db_name_entry = ctk.CTkEntry(form_frame, width=250)
        self.db_name_entry.insert(0, shared.DB_CONFIG["dbname"])
        self.db_name_entry.grid(row=0, column=1, padx=20, pady=15)
        
        ctk.CTkLabel(form_frame, text="Username:").grid(row=1, column=0, padx=20, pady=15, sticky="w")
        self.user_entry = ctk.CTkEntry(form_frame, width=250)
        self.user_entry.insert(0, shared.DB_CONFIG["user"])
        self.user_entry.grid(row=1, column=1, padx=20, pady=15)
        
        ctk.CTkLabel(form_frame, text="Password:").grid(row=2, column=0, padx=20, pady=15, sticky="w")
        self.pwd_entry = ctk.CTkEntry(form_frame, width=250, show="*")
        self.pwd_entry.insert(0, shared.DB_CONFIG["password"])
        self.pwd_entry.grid(row=2, column=1, padx=20, pady=15)
        
        ctk.CTkLabel(form_frame, text="Host:").grid(row=3, column=0, padx=20, pady=15, sticky="w")
        self.host_entry = ctk.CTkEntry(form_frame, width=250)
        self.host_entry.insert(0, shared.DB_CONFIG["host"])
        self.host_entry.grid(row=3, column=1, padx=20, pady=15)
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(btn_frame, text="Test Connection", fg_color="#b8860b", command=self.test_connection).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Save Settings", fg_color="green", command=self.save_settings).pack(side="left", padx=10)

    def test_connection(self):
        temp_config = {
            "dbname": self.db_name_entry.get(),
            "user": self.user_entry.get(),
            "password": self.pwd_entry.get(),
            "host": self.host_entry.get(),
            "connect_timeout": 3
        }
        try:
            conn = psycopg2.connect(**temp_config)
            conn.close()
            messagebox.showinfo("Success", "Connection to database successful!")
        except Exception as e:
            messagebox.showerror("Connection Failed", f"Could not connect:\n{e}")

    def save_settings(self):
        shared.DB_CONFIG["dbname"] = self.db_name_entry.get()
        shared.DB_CONFIG["user"] = self.user_entry.get()
        shared.DB_CONFIG["password"] = self.pwd_entry.get()
        shared.DB_CONFIG["host"] = self.host_entry.get()
        messagebox.showinfo("Saved", "Database configuration updated successfully.")