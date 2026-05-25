import customtkinter as ctk
import os
from collections import Counter
from PIL import Image
from styles import *
import json
from PIL import Image, ImageOps, ImageDraw

class GenreAnalyzePage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=BG_MAIN, corner_radius=0)
        self.app = app
        self._load_user_data() 
        self.drop_box = ctk.CTkFrame(self, fg_color="#1E1E1E", border_color="#444", border_width=1, corner_radius=10, width=280)
        # -------------------------------

        # Deskripsi genre untuk section rekomendasi
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

    def _load_user_data(self):
        self.username = "Guest"
        self.user_data = {}
        try:
            if os.path.exists("session.json"):
                with open("session.json", "r") as f:
                    self.username = json.load(f).get("active_user", "Guest")
            if os.path.exists("users.json"):
                with open("users.json", "r") as f:
                    self.user_data = json.load(f).get(self.username, {})
        except Exception:
            pass

    def _get_round_avatar(self, image_path, size=(40, 40)):
        try:
            mask = Image.new('L', size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + size, fill=255)
            img = Image.open(image_path).convert("RGBA")
            img = ImageOps.fit(img, size, centering=(0.5, 0.5))
            img.putalpha(mask)
            return ctk.CTkImage(img, size=size)
        except Exception:
            return None

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
        return sorted(yearly_top.keys()), yearly_top

    def get_genre_description(self, genre_name):
        return self.GENRE_DESCRIPTIONS.get(genre_name, f"Discover our top recommendations for the {genre_name} genre.")

    def _build_ui(self):
        self._build_nav()
        self.body = ctk.CTkScrollableFrame(self, fg_color=BG_MAIN, scrollbar_button_color="#444", scrollbar_button_hover_color=ACCENT)
        self.body.pack(fill="both", expand=True)

        self.create_hero_section()

        # ── KONTAINER UTAMA 2 KOLOM ──
        main_content = ctk.CTkFrame(self.body, fg_color="transparent")
        main_content.pack(fill="x", padx=100, pady=40)

        # KOLOM KIRI: Dikunci di atas (anchor="n")
        self.left_col = ctk.CTkFrame(main_content, fg_color="transparent")
        self.left_col.pack(side="left", fill="x", expand=True, padx=(0, 40), anchor="n")

        # KOLOM KANAN: Dikunci di atas (anchor="n")
        self.right_col = ctk.CTkFrame(main_content, fg_color="transparent")
        self.right_col.pack(side="right", fill="x", expand=True, padx=(40, 0), anchor="n")

        # Konten Sisi Kiri
        self.create_genre_graphics(parent=self.left_col)
        self.create_top_recommendations(parent=self.left_col)

        # Konten Sisi Kanan
        self.create_overview_section(parent=self.right_col)
        self.create_trend_section(parent=self.right_col)

        # Bagian Bawah
        self.create_orange_banner()
        self.create_footer()

    def _build_nav(self):
        self.nav = ctk.CTkFrame(self, fg_color="#111111", corner_radius=0, height=75, border_width=0)
        self.nav.pack(fill="x", side="top")
        self.nav.pack_propagate(False)

        left_frame = ctk.CTkFrame(self.nav, fg_color="transparent")
        left_frame.pack(side="left", padx=(20, 0))

        avatar_path = self.user_data.get("avatar_path", "")
        if avatar_path and os.path.exists(avatar_path):
            img_round = self._get_round_avatar(avatar_path)
            self.p_img = ctk.CTkLabel(left_frame, image=img_round, text="", cursor="hand2")
        else:
            self.p_img = ctk.CTkLabel(left_frame, text="👤", font=("Arial", 24), text_color="white", cursor="hand2")
        self.p_img.pack(side="left")

        self.p_name = ctk.CTkLabel(left_frame, text=f"  {self.username}", font=("Trebuchet MS", 15, "bold"), text_color="white", cursor="hand2")
        self.p_name.pack(side="left")

        def go_to_profile(e=None):
            self.app.show_page("profile")

        self.p_img.bind("<Button-1>", go_to_profile)
        self.p_name.bind("<Button-1>", go_to_profile)

        right_frame = ctk.CTkFrame(self.nav, fg_color="transparent")
        right_frame.pack(side="right", padx=(0, 20))

        self.entry_s = ctk.CTkEntry(
            right_frame, placeholder_text="🔍  Search movie...", width=210, height=38,
            fg_color="#222222", border_color="#333333", corner_radius=20, font=("Trebuchet MS", 12), text_color="white", border_width=1
        )
        self.entry_s.pack(side="left", padx=(0, 8))
        self.entry_s.bind("<KeyRelease>", self._on_search_typing)

        self.btn_s = ctk.CTkButton(
            right_frame, text="Search", width=80, height=38, fg_color=ACCENT, hover_color="#7A1C1C", corner_radius=20,
            font=("Trebuchet MS", 12, "bold"), text_color="white",
            command=lambda: self.app.handle_local_search(self.entry_s.get()) if hasattr(self.app, "handle_local_search") else None
        )
        self.btn_s.pack(side="left")

        menu_items = [
            ("Home",          "dashboard"),  
            ("Genre Analyze", None),         
            ("Movie Table",   "movietable"),
            ("Watchlist",     "watchlist"),
        ]
        
        pill = ctk.CTkFrame(self.nav, fg_color="#2E2E2E", bg_color="#111111", corner_radius=25, height=46, border_width=0)
        pill.place(relx=0.5, rely=0.5, anchor="center")
        pill.pack_propagate(True) 

        for i, (txt, pg) in enumerate(menu_items):
            is_active = (txt == "Genre Analyze")  
            p_left = 15 if i == 0 else 5
            p_right = 15 if i == len(menu_items) - 1 else 5
            
            btn = ctk.CTkButton(
                pill, text=txt, width=110, height=32,
                fg_color=ACCENT if is_active else "transparent",
                hover_color="#444444" if not is_active else "#902a2a",
                bg_color="transparent", corner_radius=20,
                font=("Trebuchet MS", 12, "bold"), text_color="white",
                command=lambda p=pg: self.app.show_page(p) if p else None
            )
            btn.pack(side="left", padx=(p_left, p_right), pady=7)

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
        ctk.CTkLabel(parent, text="Genre Distribution", font=("Georgia", 40, "italic"), text_color=TEXT_WHITE).pack(anchor="w", pady=(0, 20))
        graph_box = ctk.CTkFrame(parent, fg_color="transparent")
        graph_box.pack(anchor="w", fill="x")
        top_10 = self.analyzed_data[:10]
        if not top_10: return
        max_val = top_10[0][1]
        
        for genre, count in top_10:
            row = ctk.CTkFrame(graph_box, fg_color="transparent", cursor="hand2")
            row.pack(fill="x", pady=6)
            lbl = ctk.CTkLabel(row, text=f"{genre} ({count})", width=130, anchor="e", font=("Trebuchet MS", 13, "bold"), text_color=TEXT_WHITE, cursor="hand2")
            lbl.pack(side="left", padx=(0, 15))
            bar_w = max(5, int((count / max_val) * 380))
            bar = ctk.CTkFrame(row, width=bar_w, height=22, fg_color=ACCENT, corner_radius=2, cursor="hand2")
            bar.pack(side="left")
            row.bind("<Button-1>", lambda e, g=genre: self.app.handle_local_search(g))

    def create_overview_section(self, parent):
        ctk.CTkLabel(parent, text="OVERVIEW", font=("Trebuchet MS", 12, "bold"), text_color=TEXT_GRAY).pack(anchor="w", pady=(5, 5))
        overview_text = ("Analyze your movie collection's DNA.\nThis section provides insights into your\nmost watched genres and trends.")
        ctk.CTkLabel(parent, text=overview_text, font=("Trebuchet MS", 14), text_color=TEXT_WHITE, justify="left").pack(anchor="w")

    def create_trend_section(self, parent):
        self.all_years, self.yearly_top = self.process_yearly_data()
        self.trend_container = ctk.CTkFrame(parent, fg_color="transparent")
        self.trend_container.pack(fill="x", pady=(50, 0))
        
        ctk.CTkLabel(self.trend_container, text="Yearly Trends", font=("Georgia", 35, "italic"), text_color=TEXT_WHITE).pack(anchor="w", pady=(0, 10))
        
        filter_frame = ctk.CTkFrame(self.trend_container, fg_color="transparent")
        filter_frame.pack(anchor="w", pady=(0, 25))

        if not self.all_years:
            ctk.CTkLabel(self.trend_container, text="No yearly data found.", text_color=TEXT_GRAY).pack(anchor="w")
            return

        sorted_years = sorted(self.all_years)
        
        cb_style = {
            "width": 100, 
            "fg_color": "#2B2B2B", 
            "button_color": "#333", 
            "border_color": "#444", 
            "corner_radius": 6
        }
        
        self.start_combo = ctk.CTkComboBox(filter_frame, values=sorted_years, **cb_style)
        self.start_combo.set(sorted_years[0])
        self.start_combo.pack(side="left")
        try: self.start_combo._dropdown_menu.config(maxheight=10) 
        except: pass

        ctk.CTkLabel(filter_frame, text=" - ", text_color=TEXT_WHITE, font=("Arial", 16)).pack(side="left", padx=8)

        self.end_combo = ctk.CTkComboBox(filter_frame, values=sorted_years, **cb_style)
        self.end_combo.set(sorted_years[-1])
        self.end_combo.pack(side="left")
        try: self.end_combo._dropdown_menu.config(maxheight=10)
        except: pass

        btn_filter = ctk.CTkButton(filter_frame, text="Filter", width=70, height=32, fg_color="transparent", 
                                  border_width=1, border_color=ACCENT, text_color=TEXT_WHITE, 
                                  hover_color="#441111", font=("Trebuchet MS", 12, "bold"),
                                  command=self.update_trends_display)
        btn_filter.pack(side="left", padx=(15, 0))

        self.graph_display = ctk.CTkFrame(self.trend_container, fg_color="transparent")
        self.graph_display.pack(fill="x", anchor="w")

        self.update_trends_display()

    def update_trends_display(self):
        for w in self.graph_display.winfo_children(): w.destroy()

        try:
            s_year, e_year = int(self.start_combo.get()), int(self.end_combo.get())
            if s_year > e_year: s_year, e_year = e_year, s_year
        except: return

        valid_years = sorted([y for y in self.all_years if s_year <= int(y) <= e_year], reverse=True)

        # ── TEKS PERINGATAN JIKA MELEBIHI 28 TAHUN ──
        if len(valid_years) > 32:
            warning_lbl = ctk.CTkLabel(
                self.graph_display, 
                text="⚠️ Range exceeds 32 years! Only showing the 32 most recent years.", 
                font=("Trebuchet MS", 12, "bold"), 
                text_color="#FF8C00", 
                anchor="w"
            )
            warning_lbl.pack(fill="x", pady=(0, 12), anchor="w")
            valid_years = valid_years[:28]

        if not valid_years: return

        max_c = max([self.yearly_top[y][1] for y in valid_years])

        for year in valid_years:
            genre, count = self.yearly_top[year]
            
            row = ctk.CTkFrame(self.graph_display, fg_color="transparent")
            row.pack(fill="x", pady=5, anchor="w")

            ctk.CTkLabel(row, text=str(year), width=50, anchor="w", font=("Trebuchet MS", 13, "bold"), text_color=TEXT_WHITE).pack(side="left")

            bar_width = max(8, int((count / max_c) * 160))
            ctk.CTkFrame(row, width=bar_width, height=16, fg_color=ACCENT, corner_radius=0).pack(side="left", padx=(5, 12))

            ctk.CTkLabel(row, text=f"{genre} ({count})", font=("Trebuchet MS", 12), text_color=TEXT_GRAY).pack(side="left")

    def create_top_recommendations(self, parent):
        top_3 = self.analyzed_data[:3]
        movie_list = getattr(self.app, "movie_list", [])
        
        recom_container = ctk.CTkFrame(parent, fg_color="transparent")
        recom_container.pack(fill="x", pady=(50, 0), anchor="w")

        for name, count in top_3:
            cat_frame = ctk.CTkFrame(recom_container, fg_color="transparent")
            cat_frame.pack(fill="x", pady=(0, 45), anchor="w") # Jarak antar kategori kembali ke 45
            
            # Ukuran font Judul Genre kembali ke 36
            ctk.CTkLabel(cat_frame, text=name, font=("Helvetica", 36, "bold"), text_color=TEXT_WHITE).pack(anchor="w")
            
            # Ukuran font Deskripsi kembali ke 14, wraplength ke 600, dan pady ke (10, 20)
            ctk.CTkLabel(cat_frame, text=self.get_genre_description(name), font=("Trebuchet MS", 14), text_color=TEXT_GRAY, wraplength=600, justify="left").pack(anchor="w", pady=(10, 20))
            
            p_frame = ctk.CTkFrame(cat_frame, fg_color="transparent")
            p_frame.pack(anchor="w")
            matches = [m for m in movie_list if name in [g.strip() for g in m.get("genre", "").split(",")]]
            
            # Menampilkan 5 film dengan ukuran poster semula (120 x 175)
            for m_data in matches[:5]: 
                path = m_data.get("poster_local", "")
                if path and os.path.exists(path):
                    img = ctk.CTkImage(Image.open(path), size=(120, 175))
                    btn = ctk.CTkLabel(p_frame, text="", image=img, cursor="hand2")
                    btn.pack(side="left", padx=(0, 18))
                    btn.bind("<Button-1>", lambda e, d=m_data: self.app.show_page("moviedetail", data=d))
    def create_orange_banner(self):
        banner = ctk.CTkFrame(self.body, fg_color="#FF8C00", height=160)
        banner.pack(fill="x", pady=20)
        banner.pack_propagate(False)
        c = ctk.CTkFrame(banner, fg_color="transparent")
        c.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(c, text="Ready for a movie marathon?", font=("Georgia", 30, "italic"), text_color="#111").pack()
        ctk.CTkButton(c, text="Open Watchlist", fg_color="#111", corner_radius=4, font=("Trebuchet MS", 13, "bold"), command=lambda: self.app.show_page("watchlist")).pack(pady=18)

    def create_footer(self):
        footer = ctk.CTkFrame(self.body, fg_color="#0A0A0A", corner_radius=0, height=180)
        footer.pack(fill="x", pady=(20, 0))
        footer.pack_propagate(False)
        ctk.CTkLabel(footer, text="Cinephile", font=("Helvetica", 55, "bold"), text_color=TEXT_WHITE).place(relx=0.05, rely=0.5, anchor="w")
        ctk.CTkLabel(footer, text="©2026 Cinephile Archive\nCurating cinematic excellence for your personal collection.", font=("Trebuchet MS", 12), text_color=TEXT_GRAY, justify="right").place(relx=0.95, rely=0.5, anchor="e")

    def _on_search_typing(self, event):
        query = self.entry_s.get().lower().strip()
        if not query:
            self.drop_box.place_forget()
            return
        all_movies = getattr(self.app, "movie_list", [])
        matches = [m for m in all_movies if query in m.get("title", "").lower()][:5]
        
        for w in self.drop_box.winfo_children():
            w.destroy()
            
        if matches:
            self.drop_box.place(relx=1.0, x=-330, y=75)
            self.drop_box.lift()
            for m in matches:
                item_f = ctk.CTkFrame(self.drop_box, fg_color="transparent", cursor="hand2")
                item_f.pack(fill="x", padx=5, pady=2)
                p_path = m.get("poster_local", "")
                if p_path and os.path.exists(p_path):
                    try:
                        img_s = ctk.CTkImage(Image.open(p_path), size=(30, 45))
                        ctk.CTkLabel(item_f, image=img_s, text="").pack(side="left", padx=5)
                    except Exception:
                        pass
                ctk.CTkLabel(
                    item_f, text=m.get("title", "Unknown"),
                    font=("Trebuchet MS", 12), text_color="white", anchor="w"
                ).pack(side="left", fill="x")
                item_f.bind("<Button-1>", lambda e, item=m: self._go_to_detail(item))
        else:
            self.drop_box.place_forget()

    def _go_to_detail(self, movie):
        self.drop_box.place_forget()
        self.entry_s.delete(0, 'end')
        self.app.show_page("moviedetail", data=movie)