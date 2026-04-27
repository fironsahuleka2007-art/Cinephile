import customtkinter as ctk
import json
import os
import threading
from loginPage import AuthPages
from movieTable import MovietablePage
from dashboardCinephile import DashboardPage
from genreAnalyze import GenreAnalyzePage
from profilePage import ProfilePage
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
        
        # Inisialisasi Scraper
        self.scraper = MovieScraper()
        
        # Menyimpan instance halaman yang sedang aktif
        self.current_page_instance = None
        
        # Protokol saat aplikasi ditutup
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 1. BACA DATABASE JSON (Lokal)
        self.movie_list = []
        self.db_path = "data_film.json"
        if os.path.exists(self.db_path):
            with open(self.db_path, "r", encoding="utf-8") as f:
                try:
                    self.movie_list = json.load(f)
                except json.JSONDecodeError:
                    self.movie_list = []

        # 2. AUTO-SCRAPE JIKA DATABASE KOSONG
        if len(self.movie_list) == 0:
            print("⚠️ Database kosong. Memulai inisialisasi data dari IMDb...")
            threading.Thread(target=self._initialize_data, daemon=True).start()

        # 2. SETUP WADAH UTAMA (Container)
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        # 3. INISIALISASI AUTH
        self.auth = AuthPages(self.container, self)

        # 4. CEK SESI LOGIN
        active_user = self.auth.db.get_session()
        if active_user:
            self.show_page("dashboard")
        else:
            self.show_page("login")
    
    def _initialize_data(self):
        """Fungsi latar belakang untuk scraping data awal"""
        # Scrape 20 film terbaik (bisa diubah angkanya)
        hasil = self.scraper.scrape_top_movies()
        
        if hasil:
            self.movie_list = hasil
            # Simpan ke JSON
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(self.movie_list, f, indent=4)
            print("✅ Database berhasil diisi dengan data awal!")
            
            # Jika user sedang di dashboard atau movietable, refresh halamannya
            if hasattr(self, 'current_page_instance'):
                page_name = self.current_page_instance.__class__.__name__
                if page_name in ["DashboardPage", "MovietablePage"]:
                    self.after(0, lambda: self.show_page(page_name.replace("Page", "").lower()))

    def show_page(self, page_name, data=None):
        # 1. Kosongkan isi container sebelum memuat halaman baru
        for widget in self.container.winfo_children():
            widget.destroy()

        # 2. Muat halaman berdasarkan page_name
        if page_name == "login":
            self.auth.render_login()
            self.current_page_instance = self.auth
        elif page_name == "register":
            self.auth.render_register()
            self.current_page_instance = self.auth
        elif page_name == "dashboard":
            self.current_page_instance = DashboardPage(self.container, self)
            self.current_page_instance.pack(fill="both", expand=True)
        elif page_name == "movietable":
            self.current_page_instance = MovietablePage(self.container, self)
            self.current_page_instance.pack(fill="both", expand=True)
        elif page_name == "genreanalyze":
            self.current_page_instance = GenreAnalyzePage(self.container, self)
            self.current_page_instance.pack(fill="both", expand=True)
        elif page_name == "moviedetail":
            self.current_page_instance = MovieDetailPage(self.container, self, movie_data=data)
            self.current_page_instance.pack(fill="both", expand=True)
        elif page_name == "watchlist":
            self.current_page_instance = WatchlistPage(self.container, self)
            self.current_page_instance.pack(fill="both", expand=True)

    def handle_local_search(self, query):
        if not query.strip():
            return
            
        print(f"Mencari '{query}' di database lokal...")
        self.show_page("movietable")

        if hasattr(self, 'current_page_instance') and self.current_page_instance.__class__.__name__ == "MovietablePage":
            self.current_page_instance.filter_data(query)

        def run_scraping():
            print(f"🔍 Mencari data real untuk: '{query}'...")
            hasil = self.scraper.search_movie(query)
            
            if "error" in hasil:
                print(f"❌ Scraping Gagal: {hasil['error']}")
            else:
                print(f"✅ Data Ditemukan: {hasil['title']}")
                self.after(0, lambda: self.show_page("moviedetail", data=hasil))

        threading.Thread(target=run_scraping, daemon=True).start()

    def logout(self):
        self.auth.db.clear_session()
        self.show_page("login")
    
    def on_closing(self):
        print("Closing application and browser...")
        try:
            self.scraper.close()
        except:
            pass
        self.destroy()

    def show_toast(self, message, target=None):
        print(f"🔔 {message}")
        if target:
            self.show_page(target)

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue") # Atau tema oranye jika ada
    app = MainApp()
    app.mainloop()