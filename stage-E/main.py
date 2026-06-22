import customtkinter as ctk
from tkinter import messagebox
import shared

# Import Tabs
from tab_settings import SettingsFrame
from tab_crud import CrudFrame
from tab_queries import QueriesFrame
from tab_advanced import AdvancedFrame

# UI Configuration
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class KitchenManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Kitchen Management System")
        self.geometry("1200x800")
        
        # Sidebar Frame
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.pack_propagate(False)
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Kitchen Admin", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.pack(pady=(30, 30))

        # Navigation Buttons
        nav_btn_kwargs = {"width": 200, "height": 40, "anchor": "w"}
        ctk.CTkButton(self.sidebar_frame, text="⚙️ Database Settings", command=lambda: self.show_frame("Settings"), **nav_btn_kwargs).pack(pady=10)
        ctk.CTkButton(self.sidebar_frame, text="🗄️ Database Management", command=lambda: self.show_frame("CRUD"), **nav_btn_kwargs).pack(pady=10)
        ctk.CTkButton(self.sidebar_frame, text="📊 Reports & Queries", command=lambda: self.show_frame("Queries"), **nav_btn_kwargs).pack(pady=10)
        ctk.CTkButton(self.sidebar_frame, text="⚙️ Functions & Procedures", command=lambda: self.show_frame("Advanced"), **nav_btn_kwargs).pack(pady=10)
        
        ctk.CTkButton(self.sidebar_frame, text="🚪 Exit", command=self.quit, fg_color="#8b0000", hover_color="#5c0000", **nav_btn_kwargs).pack(side="bottom", pady=30)

        # Main Content Container
        self.main_container = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_container.pack(side="right", fill="both", expand=True)
        
        # Load Tabs
        self.frames = {}
        self.frames["Settings"] = SettingsFrame(self.main_container)
        self.frames["CRUD"] = CrudFrame(self.main_container)
        self.frames["Queries"] = QueriesFrame(self.main_container)
        self.frames["Advanced"] = AdvancedFrame(self.main_container)
        
        self.show_frame("Settings")

    def check_db_connection(self):
        try:
            conn = shared.get_db_connection()
            conn.close()
            return True
        except Exception:
            return False

    def show_frame(self, frame_name):
        # Guard: Ensure DB is connected before showing data screens
        if frame_name in ["CRUD", "Queries", "Advanced"]:
            if not self.check_db_connection():
                messagebox.showwarning("Connection Failed", "Could not connect to the database. Please verify and save your settings.")
                frame_name = "Settings"

        for frame in self.frames.values():
            frame.pack_forget()

        if frame_name == "CRUD":
            self.frames[frame_name].refresh_all_tabs()

        self.frames[frame_name].pack(fill="both", expand=True)

if __name__ == "__main__":
    app = KitchenManagerApp()
    app.mainloop()