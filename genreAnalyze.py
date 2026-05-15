import customtkinter as ctk
import os
from collections import Counter
from PIL import Image
from styles import *

class GenreAnalyzePage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=BG_MAIN, corner_radius=0)
        self.app = app

        # Deskripsi genre
        self.GENRE_DESCRIPTIONS = {
            "Action": "Focuses on high-energy sequences, physical feats, and thrilling chases or battles.",
            "Adventure": "Features characters traveling to new worlds or embarking on epic journeys to complete a mission.",
            "Animation": "Utilizes hand-drawn or computer-generated imagery to bring imaginative stories and characters to life.",
            "Biography": "Tells the real-life story of a person, focusing on their experiences, achievements, and legacy.",
            "Comedy": "Intended to provoke laughter through humor, irony, or witty dialogue and situations.",
            "Crime": "Features criminal activities, investigations, law enforcement, and the pursuit of justice.",
            "Drama": "Explores the human condition, emotional conflict, and realistic character development.",
            "Family": "Designed to appeal to all ages, focusing on themes like friendship, family values, and growth.",
            "Fantasy": "Involves magical elements, mythical creatures, and extraordinary worlds beyond reality.",
            "History": "Recreates historical events, periods, or figures with attention to factual details and atmosphere.",
            "Horror": "Designed to evoke fear, suspense, and shock through supernatural or psychological elements.",
            "Music": "Focuses on the lives of musicians, the creative process, or utilizes music as a central narrative theme.",
            "Musical": "Features characters who burst into song and dance to express emotions or advance the plot.",
            "Mystery": "Centers on solving a puzzle, crime, or unexplained event through clues and investigation.",
            "Romance": "Focuses on love stories, emotional relationships, and the journey of finding a partner.",
            "Sci-Fi": "Explores futuristic concepts, advanced science, technology, space exploration, and extraterrestrial life.",
            "Thriller": "Emphasizes suspense, excitement, and high-stakes tension to keep viewers on the edge of their seats.",
            "War": "Focuses on armed conflict, the struggles of soldiers, and the impact of battle on society.",
            "Western": "Set in the American Old West, featuring cowboys, outlaws, and the struggle for law and order."
        }

        self.analyzed_data = self.process_genre_logic()
        self._anim_offset = 0  
        self._build_ui()

    def process_genre_logic(self):
        all_genres = []
        movie_list = getattr(self.app, "movie_list", [])
        for movie in movie_list:
            raw_genre = movie.get("genre", "Unknown")
            if raw_genre and raw_genre not in ["Unknown", "N/A"]:
                genres = [g.strip() for g in raw_genre.split(',')]
                all_genres.extend(genres)
        counts = Counter(all_genres)
        return sorted(counts.items(), key=lambda x: x[1], reverse=True)

    def process_yearly_data(self):
        year_data = {}
        movie_list = getattr(self.app, "movie_list", [])
        for movie in movie_list:
            year_str = str(movie.get("year", movie.get("Year", "")))
            year = "".join(filter(str.isdigit, year_str))[:4]
            if not year or len(year) != 4: continue
            raw_genre = movie.get("genre", "Unknown")
            if raw_genre and raw_genre not in ["Unknown", "N/A"]:
                genres = [g.strip() for g in raw_genre.split(',')]
                if year not in year_data: year_data[year] = []
                year_data[year].extend(genres)
        yearly_top = {}
        for y, g_list in year_data.items():
            if g_list:
                top_genre, count = Counter(g_list).most_common(1)[0]
                yearly_top[y] = (top_genre, count)
        return sorted(yearly_top.keys(), reverse=True), yearly_top

    def get_genre_description(self, genre_name):
        return self.GENRE_DESCRIPTIONS.get(genre_name, f"Discover our top recommendations for the {genre_name} genre.")

    def _build_ui(self):
        self._build_nav()
        self.body = ctk.CTkScrollableFrame(self, fg_color=BG_MAIN, scrollbar_button_color="#444", scrollbar_button_hover_color=ACCENT)
        self.body.pack(fill="both", expand=True)

        self.create_hero_section()

        # --- CONTAINER UTAMA (DIBAGI 2 KOLOM) ---
        main_content = ctk.CTkFrame(self.body, fg_color="transparent")
        main_content.pack(fill="x", padx=80, pady=40)

        # KOLOM KIRI (Distribusi + Penjelasan Genre)
        left_col = ctk.CTkFrame(main_content, fg_color="transparent")
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 40), anchor="n")

        # KOLOM KANAN (Overview + Yearly Trends)
        right_col = ctk.CTkFrame(main_content, fg_color="transparent", width=350)
        right_col.pack(side="left", fill="both", anchor="n")

        # Isi Kolom Kiri
        self.create_genre_graphics(left_col)
        self.create_top_recommendations(left_col) 

        # Isi Kolom Kanan
        self.create_overview_section(right_col)
        self.create_trend_section(right_col)
        # ---------------------------------------

        self.create_orange_banner()
        self.create_footer()

    def _build_nav(self):
        nav = ctk.CTkFrame(self, fg_color="#111111", corner_radius=0, height=60)
        nav.pack(fill="x", side="top")
        nav.pack_propagate(False)
        search_frame = ctk.CTkFrame(nav, fg_color="transparent")
        search_frame.pack(side="right", padx=20, pady=10)
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search...", width=150, height=32, fg_color="#222", border_color="#444")
        self.search_entry.pack(side="left", padx=5)
        ctk.CTkButton(search_frame, text="🔍", width=40, height=32, fg_color=ACCENT, command=lambda: self.app.handle_local_search(self.search_entry.get())).pack(side="left")
        pill_outer = ctk.CTkFrame(nav, fg_color="transparent")
        pill_outer.place(relx=0.5, rely=0.5, anchor="center")
        pill = ctk.CTkFrame(pill_outer, fg_color="#2E2E2E", corner_radius=20, height=34)
        pill.pack()
        ctk.CTkButton(pill, text="Home", width=70, height=28, fg_color="transparent", text_color=TEXT_GRAY, corner_radius=16, font=("Trebuchet MS", 11, "bold"), command=lambda: self.app.show_page("dashboard")).pack(side="left", padx=3)
        ctk.CTkButton(pill, text="Genre Analysis", width=110, height=28, fg_color=ACCENT, text_color=TEXT_WHITE, corner_radius=16, font=("Trebuchet MS", 11, "bold")).pack(side="left", padx=1)
        ctk.CTkButton(pill, text="Movie Table", width=92, height=28, fg_color="transparent", text_color=TEXT_GRAY, corner_radius=16, font=("Trebuchet MS", 11, "bold"), command=lambda: self.app.show_page("movietable")).pack(side="left", padx=1)
        ctk.CTkButton(pill, text="Watchlist", width=80, height=28, fg_color="transparent", text_color=TEXT_GRAY, corner_radius=16, font=("Trebuchet MS", 11, "bold"), command=lambda: self.app.show_page("watchlist")).pack(side="left", padx=3)

    def create_hero_section(self):
        ctk.CTkLabel(self.body, text="Genre Analyze", font=("Helvetica", 70, "bold"), text_color=TEXT_WHITE).pack(pady=(60, 20))
        movie_list = getattr(self.app, "movie_list", [])
        self._carousel_movies = [m for m in movie_list if m.get("poster_local") and os.path.exists(m.get("poster_local", ""))]
        outer = ctk.CTkFrame(self.body, fg_color="transparent", height=140)
        outer.pack(fill="x", pady=10)
        outer.pack_propagate(False)
        self._carousel_frame = ctk.CTkFrame(outer, fg_color="transparent", height=130)
        self._carousel_frame.place(x=0, y=5)
        self._carousel_images = []
        sample = self._carousel_movies[:12]
        if sample:
            for movie in sample * 2:
                try:
                    img = ctk.CTkImage(Image.open(movie.get("poster_local")), size=(85, 120))
                    self._carousel_images.append(img)
                    lbl = ctk.CTkLabel(self._carousel_frame, text="", image=img, cursor="hand2")
                    lbl.pack(side="left", padx=6)
                    lbl.bind("<Button-1>", lambda e, d=movie: self.app.show_page("moviedetail", data=d))
                except: pass
            self._carousel_item_w = 85 + 12
            self._carousel_half_w = self._carousel_item_w * len(sample)
            self._anim_offset = 0
            self._animate_carousel()

    def _animate_carousel(self):
        try:
            if not self._carousel_frame.winfo_exists(): return
            self._anim_offset -= 1
            if abs(self._anim_offset) >= self._carousel_half_w: self._anim_offset = 0
            self._carousel_frame.place(x=self._anim_offset, y=5)
            self.after(30, self._animate_carousel)
        except: pass

    def create_genre_graphics(self, parent):
        ctk.CTkLabel(parent, text="Genre Distribution", font=("Georgia", 35, "italic"), text_color=TEXT_WHITE).pack(anchor="w", pady=(0, 20))
        graph_box = ctk.CTkFrame(parent, fg_color="transparent")
        graph_box.pack(anchor="w", fill="x")
        top_10 = self.analyzed_data[:10]
        if not top_10: return
        max_val = top_10[0][1]
        
        for genre, count in top_10:
            row = ctk.CTkFrame(graph_box, fg_color="transparent", cursor="hand2")
            row.pack(fill="x", pady=4)
            
            # Teks Genre (Bisa diklik)
            lbl = ctk.CTkLabel(row, text=f"{genre} ({count})", width=120, anchor="e", font=("Trebuchet MS", 12, "bold"), text_color=TEXT_WHITE, cursor="hand2")
            lbl.pack(side="left", padx=(0, 10))
            
            # Batang Grafik (Bisa diklik)
            bar_w = max(5, int((count / max_val) * 350))
            bar = ctk.CTkFrame(row, width=bar_w, height=20, fg_color=ACCENT, corner_radius=2, cursor="hand2")
            bar.pack(side="left")

            # --- FUNGSI KLIK PINDAH & FILTER ---
            def go_to_table(event, target_genre=genre):
                # Memanggil routing & pencarian milik main.py
                self.app.handle_local_search(target_genre)

            # Menyambungkan event klik ke elemen UI
            row.bind("<Button-1>", go_to_table)
            lbl.bind("<Button-1>", go_to_table)
            bar.bind("<Button-1>", go_to_table)

    def create_overview_section(self, parent):
        ctk.CTkLabel(parent, text="OVERVIEW", font=("Trebuchet MS", 12, "bold"), text_color=TEXT_GRAY).pack(anchor="w", pady=(5, 5))
        overview_text = ("Analyze your movie collection's DNA.\nThis section provides insights into your\nmost watched genres and trends.")
        ctk.CTkLabel(parent, text=overview_text, font=("Trebuchet MS", 13), text_color=TEXT_WHITE, justify="left").pack(anchor="w")

    def create_trend_section(self, parent):
        self.all_years, self.yearly_top = self.process_yearly_data()
        self.trend_container = ctk.CTkFrame(parent, fg_color="transparent")
        self.trend_container.pack(fill="x", pady=(40, 0))
        ctk.CTkLabel(self.trend_container, text="Yearly Trends", font=("Georgia", 28, "italic"), text_color=TEXT_WHITE).pack(anchor="w", pady=(0, 5))
        
        filter_frame = ctk.CTkFrame(self.trend_container, fg_color="transparent")
        filter_frame.pack(anchor="w", pady=(0, 15))
        
        y_list = self.all_years if self.all_years else ["2024"]
        self.start_year_var = ctk.StringVar(value=y_list[min(4, len(y_list)-1)])
        self.end_year_var = ctk.StringVar(value=y_list[0])
        
        ctk.CTkOptionMenu(filter_frame, values=y_list, variable=self.start_year_var, width=80, fg_color="#333", button_color=ACCENT).pack(side="left", padx=2)
        ctk.CTkLabel(filter_frame, text="-", text_color=TEXT_WHITE).pack(side="left", padx=5)
        ctk.CTkOptionMenu(filter_frame, values=y_list, variable=self.end_year_var, width=80, fg_color="#333", button_color=ACCENT).pack(side="left", padx=2)
        ctk.CTkButton(filter_frame, text="Filter", width=60, fg_color="transparent", border_width=1, border_color=ACCENT, text_color=ACCENT, command=self.render_trend_graph).pack(side="left", padx=10)
        
        self.trend_graph_area = ctk.CTkFrame(self.trend_container, fg_color="transparent")
        self.trend_graph_area.pack(fill="x")
        self.render_trend_graph()

    def render_trend_graph(self):
        for w in self.trend_graph_area.winfo_children(): w.destroy()
        s, e = self.start_year_var.get(), self.end_year_var.get()
        if s > e: s, e = e, s
        f_years = [y for y in self.all_years if s <= y <= e]
        if not f_years: return
        max_c = max([self.yearly_top[y][1] for y in f_years] + [1])
        for year in f_years:
            genre, count = self.yearly_top[year]
            row = ctk.CTkFrame(self.trend_graph_area, fg_color="transparent")
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(row, text=year, width=40, font=("Trebuchet MS", 12, "bold"), text_color=TEXT_WHITE).pack(side="left")
            bar_w = max(5, int((count / max_c) * 180))
            ctk.CTkFrame(row, width=bar_w, height=16, fg_color=ACCENT, corner_radius=2).pack(side="left", padx=10)
            ctk.CTkLabel(row, text=f"{genre} ({count})", font=("Trebuchet MS", 11), text_color=TEXT_WHITE).pack(side="left")

    def create_top_recommendations(self, parent):
        ctk.CTkFrame(parent, height=1, fg_color="#333").pack(fill="x", pady=40)
        
        top_3 = self.analyzed_data[:3]
        movie_list = getattr(self.app, "movie_list", [])
        for name, count in top_3:
            cat_frame = ctk.CTkFrame(parent, fg_color="transparent")
            cat_frame.pack(fill="x", pady=(0, 40))
            ctk.CTkLabel(cat_frame, text=name, font=("Helvetica", 32, "bold"), text_color=TEXT_WHITE).pack(anchor="w")
            ctk.CTkLabel(cat_frame, text=self.get_genre_description(name), font=("Trebuchet MS", 13), text_color=TEXT_GRAY, wraplength=500, justify="left").pack(anchor="w", pady=(10, 15))
            
            p_frame = ctk.CTkFrame(cat_frame, fg_color="transparent")
            p_frame.pack(anchor="w")
            matches = [m for m in movie_list if name in [g.strip() for g in m.get("genre", "").split(",")]]
            for m_data in matches[:4]:
                path = m_data.get("poster_local", "")
                if path and os.path.exists(path):
                    img = ctk.CTkImage(Image.open(path), size=(110, 160))
                    btn = ctk.CTkLabel(p_frame, text="", image=img, cursor="hand2")
                    btn.pack(side="left", padx=(0, 15))
                    btn.bind("<Button-1>", lambda e, d=m_data: self.app.show_page("moviedetail", data=d))

    def create_orange_banner(self):
        banner = ctk.CTkFrame(self.body, fg_color="#FF8C00", height=160)
        banner.pack(fill="x", pady=20)
        banner.pack_propagate(False)
        c = ctk.CTkFrame(banner, fg_color="transparent")
        c.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(c, text="Ready for a movie marathon?", font=("Georgia", 28, "italic"), text_color="#111").pack()
        ctk.CTkButton(c, text="Open Watchlist", fg_color="#111", corner_radius=0, command=lambda: self.app.show_page("watchlist")).pack(pady=15)

    def create_footer(self):
        footer = ctk.CTkFrame(self.body, fg_color="#0A0A0A", height=120)
        footer.pack(fill="x")
        ctk.CTkLabel(footer, text="Cinephile", font=("Helvetica", 40, "bold"), text_color=TEXT_WHITE).place(relx=0.05, rely=0.5, anchor="w")