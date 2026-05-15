import os
import json
import customtkinter as ctk
import math
from PIL import Image
import random

class MovieDetailPage(ctk.CTkFrame):
    def __init__(self, master, app, movie_data=None):
        super().__init__(master, fg_color="#141414", corner_radius=0)
        self.app = app
        self.movie = movie_data if movie_data else {}
        
        # Ambil data user agar tidak Guest
        self.username = "Guest"
        try:
            if os.path.exists("session.json"):
                with open("session.json", "r") as f:
                    data = json.load(f)
                    self.username = data.get("username", data.get("active_user", "Guest"))
        except:
            pass

        self._build_ui()

    def _generate_dynamic_chart(self, rating_str):
        try:
            rating = float(rating_str)
        except:
            rating = 5.0

        distribution = {}
        for score in range(1, 11):
            distance = abs(score - rating)
            weight = math.exp(-(distance ** 2) / 2.0) 
            noise = random.uniform(0.8, 1.2)
            distribution[score] = weight * noise     

        total_weight = sum(distribution.values())
        for score in distribution:
            distribution[score] = distribution[score] / total_weight
        return distribution

    def _add_to_watchlist(self, status):
        """Menyimpan film ke watchlist yang dinamis berdasarkan user login"""
        watchlist_file = f"watchlist_{self.username}.json"
        
        if os.path.exists(watchlist_file):
            with open(watchlist_file, "r", encoding="utf-8") as f:
                try:
                    watchlist = json.load(f)
                except:
                    watchlist = []
        else:
            watchlist = []

        movie_exists = False
        for m in watchlist:
            if m.get("title") == self.movie.get("title"):
                m["status"] = status 
                movie_exists = True
                break
        
        if not movie_exists:
            new_entry = self.movie.copy()
            new_entry["status"] = status
            watchlist.append(new_entry)

        with open(watchlist_file, "w", encoding="utf-8") as f:
            json.dump(watchlist, f, indent=4)
        
        self.add_btn.configure(text=f"✓ Added as {status}", fg_color="#28a745", hover_color="#218838")

    def _build_nav(self):
        """Membangun Navbar dengan Menu di TENGAH Presisi"""
        nav = ctk.CTkFrame(self, fg_color="#111111", height=60, corner_radius=0)
        nav.pack(fill="x", side="top")
        nav.pack_propagate(False)

        # Logo / Brand (Kiri)
        ctk.CTkLabel(nav, text="CINEPHILE", font=("Trebuchet MS", 20, "bold"), text_color="#E53935").pack(side="left", padx=30)

        # --- CONTAINER TENGAH ---
        pill = ctk.CTkFrame(nav, fg_color="#1E1E1E", height=34, corner_radius=17)
        pill.place(relx=0.5, rely=0.5, anchor="center") # INI YANG BIKIN KE TENGAH

        nav_items = [
            ("Home", "dashboard", 70),
            ("Genre Analysis", "genreanalyze", 110),
            ("Movie Table", "movietable", 92),
            ("Watchlist", "watchlist", 80)
        ]

        for text, page, w in nav_items:
            btn = ctk.CTkButton(pill, text=text, width=w, height=28, fg_color="transparent", 
                                text_color="#AAAAAA", font=("Trebuchet MS", 11, "bold"), 
                                corner_radius=16, hover_color="#3A3A3A",
                                command=lambda p=page: self.app.show_page(p))
            btn.pack(side="left", padx=2, pady=3)

        # User Profile (Kanan)
        user_frame = ctk.CTkFrame(nav, fg_color="transparent")
        user_frame.pack(side="right", padx=30)
        ctk.CTkLabel(user_frame, text=self.username, font=("Trebuchet MS", 12, "bold"), text_color="#FFFFFF").pack(side="right")
        ctk.CTkLabel(user_frame, text="👤", font=("Arial", 16)).pack(side="right", padx=10)

    def _build_ui(self):
        # Render Navbar
        self._build_nav()

        # Konten Utama dengan Scroll
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="#141414", corner_radius=0)
        self.scroll.pack(fill="both", expand=True)

        # 1. HEADER & TITLE (DI TENGAH)
        title = self.movie.get("title", "Unknown Title")
        year = self.movie.get("year", "N/A")
        title_text = f"{title} ({year})" if year != "N/A" else title
        ctk.CTkLabel(self.scroll, text=title_text, font=("Georgia", 44, "italic", "bold"), 
                     text_color="white", wraplength=900, anchor="center").pack(pady=(40, 10), anchor="center")

        # 2. MAIN POSTER (DI TENGAH)
        poster_path = self.movie.get("poster_local", "")
        if poster_path and os.path.exists(poster_path):
            try:
                img = Image.open(poster_path)
                poster_img = ctk.CTkImage(light_image=img, dark_image=img, size=(300, 450))
                ctk.CTkLabel(self.scroll, text="", image=poster_img).pack(pady=20, anchor="center")
            except: pass

        content_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        content_frame.pack(fill="x", padx=50)

        # 3. SYNOPSIS
        synopsis_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        synopsis_frame.pack(fill="x", pady=20)
        ctk.CTkLabel(synopsis_frame, text="Synopsis", font=("Helvetica", 18, "bold"), 
                     text_color="#FF8C00", width=120, anchor="nw").pack(side="left")
        
        synopsis_text = self.movie.get("synopsis", self.movie.get("description", "No synopsis available."))
        ctk.CTkLabel(synopsis_frame, text=synopsis_text, font=("Helvetica", 15), 
                     text_color="#DDDDDD", wraplength=750, justify="left").pack(side="left", fill="both", expand=True)

        ctk.CTkFrame(content_frame, fg_color="#333", height=1).pack(fill="x", pady=20)

        # 4. GENRE & RATING
        mid_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        mid_frame.pack(fill="x", pady=10)

        left_mid = ctk.CTkFrame(mid_frame, fg_color="transparent")
        left_mid.pack(side="left", fill="y")

        genre_row = ctk.CTkFrame(left_mid, fg_color="transparent")
        genre_row.pack(anchor="w")
        raw_genre = self.movie.get("genre", "General")
        genres = [g.strip() for g in raw_genre.split(",")] if isinstance(raw_genre, str) else ["Action"]
        for g in genres[:3]:
            ctk.CTkButton(genre_row, text=g, fg_color="#990000", text_color="white", width=80,
                          hover=False, corner_radius=20, height=30).pack(side="left", padx=(0, 10))

        rating_val = self.movie.get("rating", "N/A")
        ctk.CTkLabel(left_mid, text=f"★ {rating_val}/10", font=("Helvetica", 24, "bold"), 
                     text_color="#FF3333").pack(anchor="w", pady=(10, 0))

        # Platforms
        right_mid = ctk.CTkFrame(mid_frame, fg_color="transparent")
        right_mid.pack(side="right", fill="y", anchor="e")
        ctk.CTkLabel(right_mid, text="Where To Watch:", font=("Helvetica", 14, "bold"), text_color="white").pack(anchor="e")
        
        plat_row = ctk.CTkFrame(right_mid, fg_color="transparent")
        plat_row.pack(anchor="e", pady=5)
        
        platform_str = self.movie.get("platform_string", "")
        platforms = [p.strip() for p in platform_str.split(",")] if platform_str else []
        if platforms:
            for p in platforms[:4]:
                ctk.CTkButton(plat_row, text=p, fg_color="#222", text_color="white", hover=False, 
                              corner_radius=20, height=30).pack(side="left", padx=2)
        else:
            ctk.CTkLabel(plat_row, text="Not Available Online", text_color="gray").pack(side="right")

        # 5. CHART & WATCHLIST
        split_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        split_frame.pack(fill="x", pady=(40, 20), anchor="w")

        chart_frame = ctk.CTkFrame(split_frame, fg_color="transparent")
        chart_frame.pack(side="left", anchor="nw")
        ctk.CTkLabel(chart_frame, text=f"Ratings Distribution", font=("Helvetica", 24, "bold"), text_color="white").pack(anchor="w", pady=(0,20))

        ratings_data = self._generate_dynamic_chart(rating_val)
        for score in sorted(ratings_data.keys(), reverse=True):
            value = ratings_data[score]
            row = ctk.CTkFrame(chart_frame, fg_color="transparent")
            row.pack(fill="x", pady=5)
            ctk.CTkLabel(row, text=str(score), font=("Helvetica", 14), text_color="white", width=30).pack(side="left")
            fill_width = max(5, int(value * 450)) 
            ctk.CTkFrame(row, fg_color="#C00000", height=24, width=fill_width, corner_radius=5).pack(side="left", padx=10)

        wl_frame = ctk.CTkFrame(split_frame, fg_color="#1E1E1E", corner_radius=15)
        wl_frame.pack(side="left", fill="both", expand=True, padx=(80, 0), anchor="nw")
        
        wl_inner = ctk.CTkFrame(wl_frame, fg_color="transparent")
        wl_inner.pack(padx=30, pady=30, fill="both", expand=True)

        ctk.CTkLabel(wl_inner, text="Manage Watchlist", font=("Helvetica", 24, "bold"), text_color="white").pack(anchor="w", pady=(0, 20))
        self.status_var = ctk.StringVar(value="Plan to Watch")
        self.status_menu = ctk.CTkOptionMenu(wl_inner, values=["Watched", "Watching", "Plan to Watch"],
                                            variable=self.status_var, fg_color="#333", button_color="#444", 
                                            width=250, height=40)
        self.status_menu.pack(anchor="w", pady=(0, 20))

        self.add_btn = ctk.CTkButton(wl_inner, text="+ Update Watchlist", fg_color="#FF8C00", text_color="black", 
                                     font=("Helvetica", 15, "bold"), height=45, width=250,
                                     command=lambda: self._add_to_watchlist(self.status_var.get()))
        self.add_btn.pack(anchor="w")

        # 6. MORE STORIES
        more_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        more_frame.pack(fill="x", pady=(70, 40))
        ctk.CTkLabel(more_frame, text="More Stories", font=("Helvetica", 20, "bold"), text_color="white", width=150, anchor="nw").pack(side="left")
        
        posters_container = ctk.CTkFrame(more_frame, fg_color="transparent")
        posters_container.pack(side="left", fill="both", expand=True)

        all_movies = getattr(self.app, "movie_list", [])
        other_movies = [m for m in all_movies if m.get("title") != title]
        if other_movies:
            sample_movies = random.sample(other_movies, min(len(other_movies), 4))
            for m_data in sample_movies:
                m_path = m_data.get("poster_local", "")
                if m_path and os.path.exists(m_path):
                    try:
                        m_img = ctk.CTkImage(Image.open(m_path), size=(140, 200))
                        btn = ctk.CTkLabel(posters_container, text="", image=m_img, cursor="hand2")
                        btn.pack(side="left", padx=(0, 20))
                        btn.bind("<Button-1>", lambda e, d=m_data: self.app.show_page("moviedetail", data=d))
                    except: pass

        # 7. BANNER FOOTER
        banner = ctk.CTkFrame(self.scroll, fg_color="#FF8C00", corner_radius=0, height=120)
        banner.pack(fill="x", pady=(50, 0))
        banner.pack_propagate(False)
        ctk.CTkLabel(banner, text="Ready to track more movies?", font=("Georgia", 24, "italic"), text_color="black").pack(pady=(20, 5))
        ctk.CTkButton(banner, text="Back to Dashboard", fg_color="#1A1A1A", 
                      command=lambda: self.app.show_page("dashboard")).pack()