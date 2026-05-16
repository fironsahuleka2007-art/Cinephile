import customtkinter as ctk
import json
import os
import threading

from loginPage import AuthPages
from movieTable import MovietablePage
from dashboardCinephile import DashboardPage
from profilePage import ProfilePage
from genreAnalyze import GenreAnalyzePage
from movieDetail import MovieDetailPage
from watchlist import WatchlistPage
from scraper import MovieScraper
from styles import *

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Cinephile App")
        self.geometry("1100x850")
        self.configure(fg_color=BG_MAIN)
        
        self.db_path = "data_film.json"
        self.scraper = MovieScraper()
        self.current_page_instance = None
        
        # Status awal hak akses user saat pertama kali app dibuka
        self.is_admin = False 
        
        # Kunci username di core app utama (default 'guest')
        self.username = "guest" 

        self._load_local_data()

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        self.auth = AuthPages(self.container, self)
        
        active_user = None
        if os.path.exists("session.json"):
            try:
                with open("session.json", "r", encoding="utf-8") as f:
                    active_user = json.load(f).get("active_user")
            except: pass

        if active_user:
            # Jika ada session tersimpan, set langsung username aktifnya
            self.username = active_user 
            self.show_page("dashboard")
        else:
            self.show_page("login")

    def _load_local_data(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    self.movie_list = json.load(f)
            except: self.movie_list = []
        
        if not self.movie_list:
            threading.Thread(target=self._initialize_data, daemon=True).start()

    def _initialize_data(self):
        hasil = self.scraper.scrape_top_movies()
        if hasil:
            self.movie_list = hasil
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(self.movie_list, f, indent=4)
            print("✅ Database Ready!")

    def show_page(self, page_name, data=None):
        for widget in self.container.winfo_children():
            widget.destroy()

        if page_name == "login":
            self.geometry("1100x850")
            self.auth.render_login()
        elif page_name == "register":
            self.auth.render_register()
        elif page_name == "dashboard":
            self.geometry("1100x850")
            self.current_page_instance = DashboardPage(self.container, self)
        elif page_name == "profile":
            self.geometry("1100x850")
            self.current_page_instance = ProfilePage(self.container, self)
        elif page_name == "movietable":
            self.current_page_instance = MovietablePage(self.container, self)
        elif page_name == "genreanalyze":
            self.current_page_instance = GenreAnalyzePage(self.container, self)
        elif page_name == "moviedetail":
            self.current_page_instance = MovieDetailPage(self.container, self, movie_data=data)
        elif page_name == "watchlist":
            # FIX UTAMA: Kembalikan ke format original agar tidak crash positional argument!
            # Halaman WatchlistPage di dalam filenya nanti tinggal baca 'self.app.username'
            self.current_page_instance = WatchlistPage(self.container, self)

        if self.current_page_instance and hasattr(self.current_page_instance, "pack"):
            self.current_page_instance.pack(fill="both", expand=True)

    def show_toast(self, message, target=None):
        print(f"Toas Notification: {message}")
        if target:
            self.show_page(target)

    def show_welcome_transition(self, username):
        # Kunci username yang sukses login ke Core Application
        self.username = username 
        
        for widget in self.container.winfo_children():
            widget.destroy()
            
        welcome_frame = ctk.CTkFrame(self.container, fg_color=BG_MAIN)
        welcome_frame.place(relwidth=1, relheight=1)
        
        self.welcome_lbl = ctk.CTkLabel(welcome_frame, text=f"Welcome back,\n{username}", font=("Arial Black", 46, "bold"), text_color="white", justify="center")
        self.welcome_lbl.place(relx=0.5, rely=0.55, anchor="center") 
        
        self.text_y = 0.55
        self._animate_text_up()
        
        self.after(2000, lambda: self._slide_up_dashboard(welcome_frame))

    def _animate_text_up(self):
        if hasattr(self, 'welcome_lbl') and self.welcome_lbl.winfo_exists():
            if self.text_y > 0.48:
                self.text_y -= 0.001
                self.welcome_lbl.place(rely=self.text_y)
                self.after(16, self._animate_text_up)

    def _slide_up_dashboard(self, welcome_frame):
        self.current_page_instance = DashboardPage(self.container, self)
        self.current_page_instance.place(relwidth=1, relheight=1, rely=1.0, relx=0)
        self.slide_y = 1.0
        self._animate_slide(welcome_frame)

    def _animate_slide(self, welcome_frame):
        if self.slide_y > 0.005: 
            self.slide_y += (0.0 - self.slide_y) * 0.08 
            self.current_page_instance.place(rely=self.slide_y)
            self.after(16, lambda: self._animate_slide(welcome_frame))
        else:
            self.current_page_instance.place(rely=0)
            welcome_frame.destroy()
            self.current_page_instance.place_forget()
            self.current_page_instance.pack(fill="both", expand=True)

    def handle_local_search(self, query):
        if not query: return
        query = query.lower().strip()
        self.search_query_pending = query 
        self.show_page("movietable")

    def logout_user(self):
        if os.path.exists("session.json"):
            try: os.remove("session.json")
            except: pass
        self.username = "guest"
        self.show_page("login")

    def on_closing(self):
        try: self.scraper.close()
        except: pass
        self.destroy()

if __name__ == "__main__":
    app = MainApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()