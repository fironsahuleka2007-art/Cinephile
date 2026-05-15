import customtkinter as ctk
import json
import os
import threading

# Import langsung dari folder yang sama
from loginPage import AuthPages
from movieTable import MovietablePage
from dashboardCinephile import DashboardPage
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
        self.movie_list = []
        self.search_query_pending = None
        self.scraper = MovieScraper()
        self.current_page_instance = None

        self._load_local_data()

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        self.auth = AuthPages(self.container, self)
        
        # Cek Session (Login otomatis)
        active_user = None
        if os.path.exists("session.json"):
            try:
                with open("session.json", "r", encoding="utf-8") as f:
                    active_user = json.load(f).get("active_user")
            except: pass

        if active_user:
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

    def show_page(self, page_name, data=None):
        for widget in self.container.winfo_children():
            widget.destroy()

        if page_name == "login":
            self.auth.render_login()
        elif page_name == "register":
            self.auth.render_register()
        elif page_name == "dashboard":
            self.current_page_instance = DashboardPage(self.container, self)
        elif page_name == "movietable":
            self.current_page_instance = MovietablePage(self.container, self)
        elif page_name == "genreanalyze":
            self.current_page_instance = GenreAnalyzePage(self.container, self)
        elif page_name == "moviedetail":
            self.current_page_instance = MovieDetailPage(self.container, self, movie_data=data)
        elif page_name == "watchlist":
            self.current_page_instance = WatchlistPage(self.container, self)

        if self.current_page_instance and hasattr(self.current_page_instance, "pack"):
            self.current_page_instance.pack(fill="both", expand=True)

    # ========================================================
    # LOGIKA ANIMASI TRANSISI (WELCOME -> DASHBOARD)
    # ========================================================
    def show_welcome_transition(self, username):
        for widget in self.container.winfo_children():
            widget.destroy()
            
        welcome_frame = ctk.CTkFrame(self.container, fg_color=BG_MAIN)
        welcome_frame.place(relwidth=1, relheight=1)
        
        self.welcome_lbl = ctk.CTkLabel(welcome_frame, text=f"Welcome back,\n{username}", font=("Arial Black", 46, "bold"), text_color="white", justify="center")
        self.welcome_lbl.place(relx=0.5, rely=0.55, anchor="center") 
        
        self.text_y = 0.55
        self._animate_text_up()
        
        # Delay lebih lama (2000ms = 2 detik) biar teks terbaca baru slide
        self.after(2000, lambda: self._slide_up_dashboard(welcome_frame))

    def _animate_text_up(self):
        """Animasi teks melayang ke atas dengan sangat lambat & mulus"""
        if hasattr(self, 'welcome_lbl') and self.welcome_lbl.winfo_exists():
            if self.text_y > 0.48:
                self.text_y -= 0.001
                self.welcome_lbl.place(rely=self.text_y)
                self.after(16, self._animate_text_up) # 16ms = ~60fps

    def _slide_up_dashboard(self, welcome_frame):
        """Siapkan dashboard di bawah layar untuk di-slide up"""
        self.current_page_instance = DashboardPage(self.container, self)
        self.current_page_instance.place(relwidth=1, relheight=1, rely=1.0, relx=0)
        self.slide_y = 1.0
        self._animate_slide(welcome_frame)

    def _animate_slide(self, welcome_frame):
        """Menggeser dashboard ke atas menggunakan rumus Easing-Out agar sangat mulus"""
        if self.slide_y > 0.005: # Threshold biar gak bablas
            # Rumus Lerp (Linear Interpolation) biar makin ke atas makin ngerem
            self.slide_y += (0.0 - self.slide_y) * 0.08 
            self.current_page_instance.place(rely=self.slide_y)
            self.after(16, lambda: self._animate_slide(welcome_frame))
        else:
            # Selesai, kunci posisi di atas
            self.current_page_instance.place(rely=0)
            welcome_frame.destroy()
            self.current_page_instance.place_forget()
            self.current_page_instance.pack(fill="both", expand=True)

    def handle_local_search(self, query):
        if not query: return
        query = query.lower().strip()
        self.search_query_pending = query 
        self.show_page("movietable")

    def on_closing(self):
        try: self.scraper.close()
        except: pass
        self.destroy()

if __name__ == "__main__":
    app = MainApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()