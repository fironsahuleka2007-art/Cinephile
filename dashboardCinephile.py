import customtkinter as ctk
from PIL import Image
import os
import json
from collections import Counter
from styles import *

class DashboardPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=BG_MAIN, corner_radius=0)
        self.app = app
        self._load_user_data()
        self._build_ui()

    def _load_user_data(self):
        self.username = "Guest"
        try:
            if os.path.exists("session.json"):
                with open("session.json", "r") as f:
                    self.username = json.load(f).get("username", "Guest")
        except: pass

        self.stats = {"Watched": 0, "Watching": 0, "Plan to Watch": 0}
        wl_file = f"watchlist_{self.username}.json"
        if os.path.exists(wl_file):
            try:
                with open(wl_file, "r") as f:
                    data = json.load(f)
                    for m in data:
                        status = m.get("status")
                        if status in self.stats: self.stats[status] += 1
            except: pass

    def _get_insights(self):
        """Menghitung visualisasi statistik dari database film"""
        movies = getattr(self.app, "movie_list", [])
        if not movies:
            return {"top_year": "N/A", "top_genre": "N/A", "total": 0}

        # 1. Menghitung Peak Year (Tahun dengan film terbanyak)
        years = [m.get("year") for m in movies if m.get("year") and str(m.get("year")).isdigit()]
        top_year = Counter(years).most_common(1)[0][0] if years else "N/A"

        # 2. Menghitung Top Genre
        genres = []
        for m in movies:
            g_str = m.get("genre", "")
            if g_str and g_str not in ["Unknown", "N/A"]:
                genres.extend([g.strip() for g in g_str.split(",")])
        top_genre = Counter(genres).most_common(1)[0][0] if genres else "N/A"

        return {"top_year": top_year, "top_genre": top_genre, "total": len(movies)}

    def _build_ui(self):
        self._build_nav()
        self.body = ctk.CTkScrollableFrame(self, fg_color=BG_MAIN, scrollbar_button_color="#444", scrollbar_button_hover_color=ACCENT)
        self.body.pack(fill="both", expand=True, side="top")
        
        self._build_hero()
        self._build_insights_section() # FITUR BARU: Data Visualisasi
        self._build_movie_list()
        self._build_watchlist_banner()
        self._build_footer()

    def _build_nav(self):
        nav = ctk.CTkFrame(self, fg_color=BG_NAV, corner_radius=0, height=60)
        nav.pack(fill="x", side="top")
        nav.pack_propagate(False)

        self.profile_container = ctk.CTkFrame(nav, fg_color="transparent", cursor="hand2")
        self.profile_container.pack(side="left", padx=20, pady=10)
        
        initial = self.username[0].upper() if self.username else "G"
        self.avatar = ctk.CTkLabel(self.profile_container, text=initial, width=36, height=36, corner_radius=18, fg_color=ACCENT, text_color="white", font=("Trebuchet MS", 16, "bold"))
        self.avatar.pack(side="left")
        self.user_lbl = ctk.CTkLabel(self.profile_container, text=f"  {self.username} ▼", font=("Trebuchet MS", 14, "bold"), text_color=TEXT_WHITE)
        self.user_lbl.pack(side="left")

        search_frame = ctk.CTkFrame(nav, fg_color="transparent")
        search_frame.pack(side="right", padx=20, pady=10)
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search Local...", width=200, height=32, font=("Trebuchet MS", 12), fg_color="#222", border_color="#444")
        self.search_entry.pack(side="left", padx=5)
        ctk.CTkButton(search_frame, text="🔍", width=40, height=32, fg_color=ACCENT, command=lambda: self.app.handle_local_search(self.search_entry.get())).pack(side="left")

        pill_outer = ctk.CTkFrame(nav, fg_color="transparent")
        pill_outer.place(relx=0.5, rely=0.5, anchor="center")
        pill = ctk.CTkFrame(pill_outer, fg_color=BG_TAB, corner_radius=20, height=34)
        pill.pack()

        ctk.CTkButton(pill, text="Home", width=70, height=28, fg_color=ACCENT, text_color=TEXT_WHITE, corner_radius=16, font=FONT_BTN).pack(side="left", padx=(3, 1), pady=3)
        ctk.CTkButton(pill, text="Genre Analysis", width=120, height=28, fg_color="transparent", text_color=TEXT_GRAY, corner_radius=16, font=FONT_BTN, command=lambda: self.app.show_page("genreanalyze")).pack(side="left", padx=1, pady=3)
        ctk.CTkButton(pill, text="Movie Table", width=100, height=28, fg_color="transparent", text_color=TEXT_GRAY, corner_radius=16, font=FONT_BTN, command=lambda: self.app.show_page("movietable")).pack(side="left", padx=(1, 3), pady=3)
        ctk.CTkButton(pill, text="Watchlist", width=90, height=28, fg_color="transparent", text_color=TEXT_GRAY, corner_radius=16, font=FONT_BTN, command=lambda: self.app.show_page("watchlist")).pack(side="left", padx=(1, 3), pady=3)

        self.logout_btn = ctk.CTkButton(self.profile_container, text="Logout", width=60, height=24, fg_color="#333", hover_color="#c0392b", font=("Trebuchet MS", 10), command=self._handle_logout)
        self.logout_btn.pack(side="left", padx=15)

    def _handle_logout(self):
        if os.path.exists("session.json"): os.remove("session.json")
        self.app.show_page("login")

    def _build_hero(self):
        hero_frame = ctk.CTkFrame(self.body, fg_color="transparent")
        hero_frame.pack(fill="x", pady=(20, 10))
        hero_path = os.path.join("assets", "heroes", "hero1.jpeg")
        if os.path.exists(hero_path):
            try:
                # Dikecilin sizenya sedikit biar padet
                img = ctk.CTkImage(Image.open(hero_path), size=(1100, 260))
                ctk.CTkLabel(hero_frame, text="", image=img).pack()
            except: pass
        else:
            ctk.CTkLabel(hero_frame, text="Welcome to Cinephile", font=("Helvetica", 32, "bold"), text_color="white").pack(pady=50)

    def _build_insights_section(self):
        """Fitur untuk memaksimalkan visualisasi data (Saran Dosen/PM)"""
        insights = self._get_insights()
        
        insight_frame = ctk.CTkFrame(self.body, fg_color="transparent")
        insight_frame.pack(fill="x", padx=40, pady=15)
        
        ctk.CTkLabel(insight_frame, text="Database Insights", font=("Helvetica", 24, "bold"), text_color="white").pack(anchor="w", pady=(0, 10))
        
        cards_container = ctk.CTkFrame(insight_frame, fg_color="transparent")
        cards_container.pack(fill="x")
        
        # 4 Card Box agar penuh dan padat
        self._create_stat_card(cards_container, "Total Movies", str(insights["total"]), "🎬", "#2d5a27")
        self._create_stat_card(cards_container, "Peak Year", str(insights["top_year"]), "📅", "#8A4B1A")
        self._create_stat_card(cards_container, "Top Genre", str(insights["top_genre"]), "🔥", "#2A368F")
        wl_total = sum(self.stats.values())
        self._create_stat_card(cards_container, "Your Watchlist", f"{wl_total} Titles", "📌", "#c0392b")

    def _create_stat_card(self, parent, title, value, icon, color):
        card = ctk.CTkFrame(parent, fg_color=color, corner_radius=12, height=90)
        card.pack(side="left", fill="x", expand=True, padx=8)
        card.pack_propagate(False)
        
        ctk.CTkLabel(card, text=icon, font=("Arial", 36)).pack(side="left", padx=15)
        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", fill="y", pady=12)
        ctk.CTkLabel(info, text=title, font=("Trebuchet MS", 13), text_color="#DDDDDD", anchor="w").pack(fill="x")
        ctk.CTkLabel(info, text=value, font=("Arial Black", 20, "bold"), text_color="white", anchor="w").pack(fill="x")

    def _build_movie_list(self):
        title_frame = ctk.CTkFrame(self.body, fg_color="transparent")
        title_frame.pack(fill="x", padx=40, pady=(15, 10))
        ctk.CTkLabel(title_frame, text="Trending Now", font=("Helvetica", 24, "bold"), text_color="white").pack(side="left")

        scroll_h = ctk.CTkScrollableFrame(self.body, orientation="horizontal", height=290, fg_color="transparent")
        scroll_h.pack(fill="x", padx=30)
        
        movies = getattr(self.app, "movie_list", [])
        for m in movies[:10]:
            card = ctk.CTkFrame(scroll_h, fg_color="transparent", width=150, height=260)
            card.pack(side="left", padx=10)
            card.pack_propagate(False)

            def go_to_detail(e, md=m): self.app.show_page("moviedetail", data=md)
            
            poster_path = m.get("poster_local", "")
            if poster_path and os.path.exists(poster_path):
                try:
                    img = ctk.CTkImage(Image.open(poster_path), size=(145, 210))
                    lbl = ctk.CTkLabel(card, text="", image=img, cursor="hand2")
                    lbl.pack(); lbl.bind("<Button-1>", go_to_detail)
                except: pass
            
            lbl_t = ctk.CTkLabel(card, text=m.get("title", "Unknown"), font=("Trebuchet MS", 13, "bold"), text_color="white", anchor="w")
            lbl_t.pack(fill="x", pady=(5,0)); lbl_t.bind("<Button-1>", go_to_detail)

    def _build_watchlist_banner(self):
        wrapper = ctk.CTkFrame(self.body, fg_color=BG_MAIN)
        wrapper.pack(fill="x", padx=30, pady=20)
        banner = ctk.CTkFrame(wrapper, fg_color="#FF8C00", corner_radius=15, height=140) 
        banner.pack(fill="x")
        banner.pack_propagate(False)
        content = ctk.CTkFrame(banner, fg_color="transparent")
        content.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(content, text="Manage your watchlist today!", font=("Georgia", 26, "italic", "bold"), text_color="#111111").pack()
        ctk.CTkButton(content, text="Go to Watchlist", fg_color="#111111", text_color="white", font=FONT_BTN, width=180, height=35, command=lambda: self.app.show_page("watchlist")).pack(pady=10)

    def _build_footer(self):
        footer = ctk.CTkFrame(self.body, fg_color="#0A0A0A", corner_radius=0, height=130)
        footer.pack(fill="x", pady=(10, 0))
        footer.pack_propagate(False)
        ctk.CTkLabel(footer, text="Cinephile", font=("Helvetica", 46, "bold"), text_color=TEXT_WHITE).place(relx=0.05, rely=0.5, anchor="w")
        ctk.CTkLabel(footer, text="©2026 Cinephile Archive\nCurating cinematic excellence.", font=("Trebuchet MS", 12), text_color=TEXT_GRAY, justify="right").place(relx=0.95, rely=0.5, anchor="e")