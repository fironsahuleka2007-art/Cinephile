import customtkinter as ctk
from collections import Counter
from styles import * # Memakai warna dari styles.py biar seragam

class GenreAnalyzePage(ctk.CTkFrame):
    def __init__(self, master, app):
        # 1. Ubah jadi CTkFrame biasa (bukan Scrollable) biar Navigasi bisa nempel di atas
        super().__init__(master, fg_color=BG_MAIN, corner_radius=0)
        self.app = app

        # Data Simulasi
        self.raw_movie_data = [
            "Epic", "Epic, Drama", "Action, Epic", "Epic, Romance", "Epic, Fantasy",
            "Action", "Action, Sci-Fi", "Action, Comedy", "Action, Thriller",
            "Crime", "Crime, Drama", "Crime, Mystery",
            "Drama", "Drama, Romance", "Comedy", "Thriller", "Horror", "Sci-Fi", "Adventure", "Animation", "Mystery"
        ]
        
        # Proses Data
        self.analyzed_data = self.process_genre_logic()

        # Bangun UI (Navigasi + Body Scroll)
        self._build_ui()

    def _build_ui(self):
        # Panggil Navigasi dulu biar nempel di paling atas
        self._build_nav()
        
        # 2. Bikin Body yang bisa di-scroll persis kayak Dashboard
        self.body = ctk.CTkScrollableFrame(self, fg_color=BG_MAIN, scrollbar_button_color="#444", scrollbar_button_hover_color=ACCENT)
        self.body.pack(fill="both", expand=True, side="top")

        # Masukkan komponen UI dari temanmu ke dalam self.body
        self.create_hero_section()
        self.create_genre_graphics()
        self.create_top_recommendations()
        self.create_orange_banner()
        self.create_footer()

    # ── BAGIAN NAVIGASI (Disamakan dengan Dashboard) ──
    def _build_nav(self):
        nav = ctk.CTkFrame(self, fg_color=BG_NAV, corner_radius=0, height=44)
        nav.pack(fill="x", side="top")
        nav.pack_propagate(False)

        nav.columnconfigure(0, weight=1) 
        nav.columnconfigure(1, weight=0) 
        nav.columnconfigure(2, weight=1) 

        # Logo / Log Out di kiri
        logout_btn = ctk.CTkLabel(nav, text="◎ Log Out", cursor="hand2", font=("Trebuchet MS", 12, "bold"), text_color=ACCENT)
        logout_btn.grid(row=0, column=0, sticky="w", padx=(16, 0), pady=8)
        logout_btn.bind("<Button-1>", lambda e: self.app.logout())

        # Pill Tabs (Tengah)
        pill_outer = ctk.CTkFrame(nav, fg_color="transparent")
        pill_outer.grid(row=0, column=1, pady=7)
        pill = ctk.CTkFrame(pill_outer, fg_color=BG_TAB, corner_radius=20, height=30)
        pill.pack()

        # Tombol Home (ABU)
        btn_home = ctk.CTkButton(pill, text="Home", width=60, height=26, fg_color="transparent", hover_color="#3A3A3A", text_color=TEXT_GRAY, font=("Trebuchet MS", 10, "bold"), corner_radius=16)
        btn_home.pack(side="left", padx=(3, 1), pady=2)
        btn_home.configure(command=lambda: self.app.show_page("dashboard"))

        # Tombol Genre Analysis (MERAH KARENA SEDANG AKTIF)
        btn_genre = ctk.CTkButton(pill, text="Genre Analysis", width=110, height=26, fg_color=ACCENT, hover_color="#C62828", text_color=TEXT_WHITE, font=("Trebuchet MS", 10, "bold"), corner_radius=16)
        btn_genre.pack(side="left", padx=1, pady=2)

        # Tombol Movie Table (ABU)
        btn_table = ctk.CTkButton(pill, text="Movie Table", width=92, height=26, fg_color="transparent", hover_color="#3A3A3A", text_color=TEXT_GRAY, font=("Trebuchet MS", 10, "bold"), corner_radius=16)
        btn_table.pack(side="left", padx=(1, 3), pady=2)
        btn_table.configure(command=lambda: self.app.show_page("movietable"))

        ctk.CTkLabel(pill, text="🔍", font=("Trebuchet MS", 13), text_color=TEXT_GRAY).pack(side="left", padx=(4, 8))
        ctk.CTkLabel(nav, text="").grid(row=0, column=2)

    # --- LOGIKA ANALISIS ---
    def process_genre_logic(self):
        all_genres = []
        for row in self.raw_movie_data:
            if row and row != "Unknown":
                genres = row.split(', ')
                all_genres.extend(genres)
        counts = Counter(all_genres)
        return sorted(counts.items(), key=lambda x: x[1], reverse=True)

    def get_genre_description(self, genre_name):
        descriptions = {
            "Epic": "The epic genre features grand, sweeping stories, often set against significant historical, cultural, or mythical backdrops.",
            "Action": "The action genre features fast-paced, thrilling, and intense sequences of physical feats, combat, and excitement.",
            "Crime": "The crime genre features criminal activities, investigations, law enforcement, crimes, and the pursuit of justice.",
            "Drama": "Menggali sisi kemanusiaan, konflik emosional, dan perkembangan karakter yang realistis."
        }
        return descriptions.get(genre_name, f"Discover our top recommendations for the {genre_name} genre based on your collection.")

    # --- KOMPONEN UI ---
    def create_hero_section(self):
        # Menempelkan widget ke self.body, bukan self
        ctk.CTkLabel(self.body, text="Genre Analyze", font=("Helvetica", 70, "bold"), text_color=TEXT_WHITE).pack(pady=(60, 20))
        
        deco_frame = ctk.CTkFrame(self.body, fg_color="transparent")
        deco_frame.pack(pady=10)
        for color in ["#2d5a27", "#333333", "#c4a484", "#555555"]:
            ctk.CTkFrame(deco_frame, width=120, height=90, fg_color=color, corner_radius=8).pack(side="left", padx=15)

        desc_frame = ctk.CTkFrame(self.body, fg_color="transparent")
        desc_frame.pack(fill="x", padx=150, pady=40)
        ctk.CTkLabel(desc_frame, text="Why this exists", font=("Trebuchet MS", 12, "bold"), text_color=TEXT_GRAY).pack(side="left", anchor="n")
        text = "Genre Analyze helps you understand your movie preferences by examining the\ndistribution of genres in your collection. It highlights which genres appear most\nfrequently and which ones are less common, displayed through an easy-to-read chart."
        ctk.CTkLabel(desc_frame, text=text, font=("Trebuchet MS", 13), text_color=TEXT_WHITE, justify="left").pack(side="left", padx=40)

    def create_genre_graphics(self):
        ctk.CTkLabel(self.body, text="Genre Graphics", font=("Georgia", 35, "italic"), text_color=TEXT_WHITE).pack(pady=(20, 20))
        
        graph_box = ctk.CTkFrame(self.body, fg_color="transparent")
        graph_box.pack(pady=10)

        top_10 = self.analyzed_data[:10]
        if not top_10: return
        max_val = top_10[0][1]

        for genre, count in top_10:
            row = ctk.CTkFrame(graph_box, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=genre, width=100, anchor="e", font=("Trebuchet MS", 12, "bold"), text_color=TEXT_WHITE).pack(side="left", padx=10)
            
            bar_w = int((count / max_val) * 350)
            if bar_w < 5: bar_w = 5
            # Menggunakan ACCENT (Merah) dari styles.py
            ctk.CTkFrame(row, width=bar_w, height=18, fg_color=ACCENT, corner_radius=0).pack(side="left")

    def create_top_recommendations(self):
        top_3 = self.analyzed_data[:3]
        
        for index, (name, count) in enumerate(top_3):
            cat_frame = ctk.CTkFrame(self.body, fg_color="transparent")
            cat_frame.pack(fill="x", padx=150, pady=40)
            
            ctk.CTkLabel(cat_frame, text=name, font=("Helvetica", 32, "bold"), text_color=TEXT_WHITE).pack(anchor="w")
            ctk.CTkLabel(cat_frame, text=self.get_genre_description(name), font=("Trebuchet MS", 13), text_color=TEXT_GRAY, wraplength=650, justify="left").pack(anchor="w", pady=(10, 15))
            ctk.CTkLabel(cat_frame, text=f"{name} Movies", font=("Trebuchet MS", 12, "bold"), text_color=TEXT_WHITE).pack(anchor="w", pady=(0, 15))
            
            p_frame = ctk.CTkFrame(cat_frame, fg_color="transparent")
            p_frame.pack(anchor="w")
            for _ in range(3):
                p = ctk.CTkFrame(p_frame, width=130, height=190, fg_color=BG_TAB, corner_radius=4)
                p.pack(side="left", padx=(0, 20))
                p.pack_propagate(False)

            if index < len(top_3) - 1:
                ctk.CTkFrame(self.body, height=1, fg_color="#333333").pack(fill="x", padx=150, pady=10)

    def create_orange_banner(self):
        # Desain Banner Oranye disamakan 100% dengan Dashboard
        wrapper = ctk.CTkFrame(self.body, fg_color=BG_MAIN)
        wrapper.pack(fill="x", padx=20, pady=12)
        banner = ctk.CTkFrame(wrapper, fg_color="#FF8C00", corner_radius=0, height=200)
        banner.pack(fill="x")
        banner.pack_propagate(False)

        content = ctk.CTkFrame(banner, fg_color="transparent")
        content.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(content, text="Don't forget your watchlist!", font=("Georgia", 36, "italic"), text_color="#111111").pack(pady=(0,5))
        ctk.CTkLabel(content, text="Update it and discover what to watch next.", font=("Trebuchet MS", 14, "bold"), text_color="#222222").pack(pady=(0, 20))
        ctk.CTkButton(content, text="Go to Watchlist", fg_color="#111111", hover_color="#333333", text_color=TEXT_WHITE, font=("Trebuchet MS", 12, "bold"), width=160, height=40, corner_radius=0, command=lambda: self.app.show_page("watchlist")).pack()

    def create_footer(self):
        # Footer disamakan 100% dengan Dashboard
        footer = ctk.CTkFrame(self.body, fg_color="#0A0A0A", corner_radius=0, height=170)
        footer.pack(fill="x", pady=(20, 0))
        footer.pack_propagate(False)

        ctk.CTkLabel(footer, text="Cinephile", font=("Helvetica", 60, "bold"), text_color=TEXT_WHITE).place(relx=0.04, rely=0.5, anchor="w")
        ctk.CTkLabel(footer, text="©2026 Movie Archive\nWords, images, and signals from the edge", font=("Trebuchet MS", 10), text_color=TEXT_GRAY, justify="right").place(relx=0.96, rely=0.8, anchor="e")