import customtkinter as ctk
import json
import os
import threading
from loginPage import AuthPages
from movieTable import MovietablePage
from dashboardCinephile import DashboardPage
from genreAnalyze import GenreAnalyzePage
from movieDetail import MovieDetailPage
from watchlist import WatchlistPage
from scraper import MovieScraper

# Variabel Warna Global (Biar gak NameError lagi)
BG_MAIN    = "#1A1A1A"
BG_LIGHT   = "#F4F4F4"
TEXT_WHITE = "#FFFFFF"
TEXT_GRAY  = "#AAAAAA"
ACCENT     = "#E53935"

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Cinephile App")
        self.geometry("1100x850")
        self.configure(fg_color=BG_MAIN)
        
        # Variabel sistem
        self.search_query_pending = None
        self.movie_list = []
        self.db_path = "data_film.json"
        self.scraper = MovieScraper()
        self.current_page_instance = None

        # Load Data Lokal
        self._load_local_data()

        # UI Setup
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        # Init Auth
        self.auth = AuthPages(self.container, self)

        # Cek Sesi
        active_user = self.auth.db.get_session()
        if active_user:
            self.show_page("dashboard")
        else:
            self.show_page("login")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _load_local_data(self):
        if os.path.exists(self.db_path):
            with open(self.db_path, "r", encoding="utf-8") as f:
                try:
                    self.movie_list = json.load(f)
                except:
                    self.movie_list = []
        
        if not self.movie_list:
            print("⚠️ Database kosong. Scraping data awal...")
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
            self.auth.render_login()
            self.current_page_instance = self.auth
        elif page_name == "register":
            self.auth.render_register()
            self.current_page_instance = self.auth
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

        if hasattr(self.current_page_instance, "pack"):
            self.current_page_instance.pack(fill="both", expand=True)

    def show_toast(self, message, target=None):
        """Fungsi yang tadi error (Sekarang sudah ada)"""
        print(f"🔔 {message}")
        if target:
            self.show_page(target)

    def handle_local_search(self, query):
        if not query: return
        query = query.lower().strip()
        
        # Jika di MovieTable, langsung filter. Jika tidak, titip query.
        if self.current_page_instance.__class__.__name__ == "MovietablePage":
            self.current_page_instance.filter_data(query)
        else:
            self.search_query_pending = query
            self.show_page("movietable")

    def on_closing(self):
        try: self.scraper.close()
        except: pass
        self.destroy()

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()