import customtkinter as ctk
import os
from collections import Counter
from PIL import Image
from styles import * # Pastikan BG_MAIN, ACCENT, TEXT_WHITE, dll ada di sini

class GenreAnalyzePage(ctk.CTkFrame):
    def __init__(self, master, app):
        # 1. Frame Dasar
        super().__init__(master, fg_color=BG_MAIN, corner_radius=0)
        self.app = app

        # 2. Kamus Deskripsi Genre (Full English)
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

        # Proses Data dari Database Lokal
        self.analyzed_data = self.process_genre_logic()

        # Bangun UI
        self._build_ui()

    def process_genre_logic(self):
        all_genres = []
        movie_list = getattr(self.app, "movie_list", [])
        
        for movie in movie_list:
            raw_genre = movie.get("genre", "Unknown")
            if raw_genre and raw_genre not in ["Unknown", "N/A"]:
                # Memecah string genre seperti "Action, Drama" menjadi list
                genres = [g.strip() for g in raw_genre.split(',')]
                all_genres.extend(genres)
                
        counts = Counter(all_genres)
        return sorted(counts.items(), key=lambda x: x[1], reverse=True)

    def get_genre_description(self, genre_name):
        # Mengambil dari kamus GENRE_DESCRIPTIONS, jika tidak ada pakai default English
        return self.GENRE_DESCRIPTIONS.get(
            genre_name, 
            f"Discover our top recommendations for the {genre_name} genre based on your collection."
        )

    def _build_ui(self):
        # Navigasi (Sticky at top)
        self._build_nav()
        
        # Body Scrollable
        self.body = ctk.CTkScrollableFrame(self, fg_color=BG_MAIN, scrollbar_button_color="#444", scrollbar_button_hover_color=ACCENT)
        self.body.pack(fill="both", expand=True, side="top")

        # Komponen-komponen halaman
        self.create_hero_section()
        self.create_genre_graphics()
        self.create_top_recommendations()
        self.create_orange_banner()
        self.create_footer()

    def _build_nav(self):
        nav = ctk.CTkFrame(self, fg_color="#111111", corner_radius=0, height=60)
        nav.pack(fill="x", side="top")
        nav.pack_propagate(False)

        # Search Bar
        search_frame = ctk.CTkFrame(nav, fg_color="transparent")
        search_frame.pack(side="right", padx=20, pady=10)
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search Local...", width=150, height=32, fg_color="#222", border_color="#444")
        self.search_entry.pack(side="left", padx=5)
        ctk.CTkButton(search_frame, text="🔍", width=40, height=32, fg_color=ACCENT, 
                    command=lambda: self.app.handle_local_search(self.search_entry.get())).pack(side="left")

        # Navigation Tabs
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
        
        deco_frame = ctk.CTkFrame(self.body, fg_color="transparent")
        deco_frame.pack(pady=10)
        for color in ["#2d5a27", "#333333", "#c4a484", "#555555"]:
            ctk.CTkFrame(deco_frame, width=120, height=90, fg_color=color, corner_radius=8).pack(side="left", padx=15)

        desc_frame = ctk.CTkFrame(self.body, fg_color="transparent")
        desc_frame.pack(fill="x", padx=150, pady=40)
        ctk.CTkLabel(desc_frame, text="OVERVIEW", font=("Trebuchet MS", 12, "bold"), text_color=TEXT_GRAY).pack(side="left", anchor="n")
        
        overview_text = ("Genre Analysis helps you understand your cinematic preferences by examining the\n"
                         "distribution of genres in your collection. It highlights which genres appear most\n"
                         "frequently, providing insights through an easy-to-read graphical interface.")
        ctk.CTkLabel(desc_frame, text=overview_text, font=("Trebuchet MS", 13), text_color=TEXT_WHITE, justify="left").pack(side="left", padx=40)

    def create_genre_graphics(self):
        ctk.CTkLabel(self.body, text="Genre Distribution", font=("Georgia", 35, "italic"), text_color=TEXT_WHITE).pack(pady=(20, 20))
        
        graph_box = ctk.CTkFrame(self.body, fg_color="transparent")
        graph_box.pack(pady=10)

        top_10 = self.analyzed_data[:10]
        if not top_10: 
            ctk.CTkLabel(graph_box, text="No movie data available.", text_color=TEXT_GRAY).pack()
            return
            
        max_val = top_10[0][1]

        for genre, count in top_10:
            row = ctk.CTkFrame(graph_box, fg_color="transparent")
            row.pack(fill="x", pady=4)
            
            ctk.CTkLabel(row, text=f"{genre} ({count})", width=140, anchor="e", font=("Trebuchet MS", 12, "bold"), text_color=TEXT_WHITE).pack(side="left", padx=10)
            
            bar_w = int((count / max_val) * 400)
            if bar_w < 5: bar_w = 5
            ctk.CTkFrame(row, width=bar_w, height=20, fg_color=ACCENT, corner_radius=2).pack(side="left")

    def create_top_recommendations(self):
        top_3 = self.analyzed_data[:3]
        movie_list = getattr(self.app, "movie_list", [])
        
        for index, (name, count) in enumerate(top_3):
            cat_frame = ctk.CTkFrame(self.body, fg_color="transparent")
            cat_frame.pack(fill="x", padx=150, pady=40)
            
            ctk.CTkLabel(cat_frame, text=name, font=("Helvetica", 32, "bold"), text_color=TEXT_WHITE).pack(anchor="w")
            ctk.CTkLabel(cat_frame, text=self.get_genre_description(name), font=("Trebuchet MS", 13), text_color=TEXT_GRAY, wraplength=650, justify="left").pack(anchor="w", pady=(10, 15))
            ctk.CTkLabel(cat_frame, text=f"Featured {name} Titles", font=("Trebuchet MS", 12, "bold"), text_color=TEXT_WHITE).pack(anchor="w", pady=(0, 15))
            
            p_frame = ctk.CTkFrame(cat_frame, fg_color="transparent")
            p_frame.pack(anchor="w")
            
            # Filter film yang mengandung genre ini
            matching_movies = [m for m in movie_list if name in [g.strip() for g in m.get("genre", "").split(",")]]
            
            for m_data in matching_movies[:4]: # Tampilkan sampai 4 film
                poster_path = m_data.get("poster_local", "")
                
                if poster_path and os.path.exists(poster_path):
                    try:
                        img = ctk.CTkImage(Image.open(poster_path), size=(130, 190))
                        btn = ctk.CTkLabel(p_frame, text="", image=img, cursor="hand2")
                        btn.pack(side="left", padx=(0, 20))
                        btn.bind("<Button-1>", lambda e, d=m_data: self.app.show_page("moviedetail", data=d))
                    except: pass
                else:
                    p = ctk.CTkFrame(p_frame, width=130, height=190, fg_color="#333", corner_radius=4)
                    p.pack(side="left", padx=(0, 20))
                    p.pack_propagate(False)
                    ctk.CTkLabel(p, text=m_data.get("title", "No Title"), font=("Trebuchet MS", 11), text_color=TEXT_WHITE, wraplength=110).place(relx=0.5, rely=0.5, anchor="center")

            if index < len(top_3) - 1:
                ctk.CTkFrame(self.body, height=1, fg_color="#333333").pack(fill="x", padx=150, pady=20)

    def create_orange_banner(self):
        banner = ctk.CTkFrame(self.body, fg_color="#FF8C00", corner_radius=0, height=180)
        banner.pack(fill="x", padx=0, pady=20)
        banner.pack_propagate(False)

        content = ctk.CTkFrame(banner, fg_color="transparent")
        content.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(content, text="Ready for a movie marathon?", font=("Georgia", 32, "italic"), text_color="#111111").pack()
        ctk.CTkLabel(content, text="Review your watchlist and plan your next cinematic journey.", font=("Trebuchet MS", 14), text_color="#222222").pack(pady=(5, 20))
        ctk.CTkButton(content, text="Open Watchlist", fg_color="#111111", hover_color="#333333", text_color=TEXT_WHITE, font=("Trebuchet MS", 12, "bold"), width=160, height=40, corner_radius=0, command=lambda: self.app.show_page("watchlist")).pack()

    def create_footer(self):
        footer = ctk.CTkFrame(self.body, fg_color="#0A0A0A", corner_radius=0, height=150)
        footer.pack(fill="x", pady=(20, 0))
        footer.pack_propagate(False)

        ctk.CTkLabel(footer, text="Cinephile", font=("Helvetica", 50, "bold"), text_color=TEXT_WHITE).place(relx=0.05, rely=0.5, anchor="w")
        ctk.CTkLabel(footer, text="©2026 Cinephile Archive\nCurating cinematic excellence for your personal collection.", font=("Trebuchet MS", 11), text_color=TEXT_GRAY, justify="right").place(relx=0.95, rely=0.5, anchor="e")