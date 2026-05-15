import os
import json
import customtkinter as ctk
import math
from PIL import Image, ImageFilter, ImageEnhance
import random


class MovieDetailPage(ctk.CTkFrame):
    def __init__(self, master, app, movie_data=None):
        super().__init__(master, fg_color="#141414", corner_radius=0)
        self.app = app
        self.movie = movie_data if movie_data else {}
        self.star_buttons = []
        self.selected_stars = 0
        self._more_movies = None  # FIX: cache sample movies

        # FIX: init image cache on app level
        if not hasattr(self.app, '_img_cache'):
            self.app._img_cache = {}

        self.username = "Guest"
        try:
            if os.path.exists("session.json"):
                with open("session.json", "r") as f:
                    data = json.load(f)
                    self.username = data.get("username", data.get("active_user", "Guest"))
        except:
            pass

        self._build_ui()

    # FIX: helper untuk load image dengan cache
    def _load_image(self, path, size):
        key = (path, size)
        if key not in self.app._img_cache:
            img = Image.open(path)
            self.app._img_cache[key] = ctk.CTkImage(
                light_image=img, dark_image=img, size=size
            )
        return self.app._img_cache[key]

    def _generate_dynamic_chart(self, rating_str, votes_str="0"):
        try:
            rating = float(rating_str)
        except:
            rating = 5.0

        # FIX: parse total votes dari scraper
        try:
            total_votes = int(str(votes_str).replace(",", "").replace(".", "").replace(" ", ""))
        except:
            total_votes = 0

        distribution = {}
        for score in range(1, 11):
            distance = abs(score - rating)
            weight = math.exp(-(distance ** 2) / 2.0)
            noise = random.uniform(0.8, 1.2)
            distribution[score] = weight * noise

        total_weight = sum(distribution.values())
        for score in distribution:
            distribution[score] = distribution[score] / total_weight

        return distribution, total_votes

    def _load_existing_review(self):
        watchlist_file = f"watchlist_{self.username}.json"
        if os.path.exists(watchlist_file):
            try:
                with open(watchlist_file, "r", encoding="utf-8") as f:
                    watchlist = json.load(f)
                for m in watchlist:
                    if m.get("title") == self.movie.get("title"):
                        return m.get("user_rating", 0), m.get("user_review", "")
            except:
                pass
        return 0, ""

    def _on_status_change(self, value):
        if value == "Plan to Watch":
            self.selected_stars = 0
            for i, btn in enumerate(self.star_buttons):
                btn.configure(state="disabled", text="☆", text_color="#2A2A2A")
        else:
            for btn in self.star_buttons:
                btn.configure(state="normal", text_color="#555555")
            for i, btn in enumerate(self.star_buttons):
                if i < self.selected_stars:
                    btn.configure(text="★", text_color="#FF8C00")
                else:
                    btn.configure(text="☆", text_color="#555555")

    def _set_stars(self, count):
        if self.status_var.get() == "Plan to Watch":
            return
        self.selected_stars = count
        for i, btn in enumerate(self.star_buttons):
            if i < count:
                btn.configure(text="★", text_color="#FF8C00")
            else:
                btn.configure(text="☆", text_color="#555555")

    def _go_to_genre(self, genre):
        self.app.search_query_pending = genre
        self.app.show_page("movietable")

    def _add_to_watchlist(self, status):
        watchlist_file = f"watchlist_{self.username}.json"

        if os.path.exists(watchlist_file):
            with open(watchlist_file, "r", encoding="utf-8") as f:
                try:
                    watchlist = json.load(f)
                except:
                    watchlist = []
        else:
            watchlist = []

        user_rating = self.selected_stars
        user_review = self.review_entry.get("1.0", "end").strip()

        movie_exists = False
        for m in watchlist:
            if m.get("title") == self.movie.get("title"):
                m["status"] = status
                if user_rating > 0:
                    m["user_rating"] = user_rating
                if user_review:
                    m["user_review"] = user_review
                movie_exists = True
                break

        if not movie_exists:
            new_entry = self.movie.copy()
            new_entry["status"] = status
            if user_rating > 0:
                new_entry["user_rating"] = user_rating
            if user_review:
                new_entry["user_review"] = user_review
            watchlist.append(new_entry)

        with open(watchlist_file, "w", encoding="utf-8") as f:
            json.dump(watchlist, f, indent=4)

        self.add_btn.configure(text=f"✓ Saved as {status}", fg_color="#28a745", hover_color="#218838")

    def _build_nav(self):
        nav = ctk.CTkFrame(self, fg_color="#111111", height=60, corner_radius=0)
        nav.pack(fill="x", side="top")
        nav.pack_propagate(False)

        ctk.CTkLabel(nav, text="CINEPHILE", font=("Trebuchet MS", 20, "bold"),
                     text_color="#E53935").pack(side="left", padx=30)

        user_frame = ctk.CTkFrame(nav, fg_color="transparent")
        user_frame.pack(side="right", padx=30)
        ctk.CTkLabel(user_frame, text=self.username, font=("Trebuchet MS", 12, "bold"),
                     text_color="#FFFFFF").pack(side="right")
        ctk.CTkLabel(user_frame, text="👤", font=("Arial", 16)).pack(side="right", padx=10)

        center_frame = ctk.CTkFrame(nav, fg_color="transparent")
        center_frame.pack(side="left", fill="both", expand=True)

        pill = ctk.CTkFrame(center_frame, fg_color="#1E1E1E", height=40, corner_radius=20)
        pill.place(relx=0.5, rely=0.5, anchor="center")

        nav_items = [
            ("Home",           "dashboard",    70),
            ("Genre Analysis", "genreanalyze", 110),
            ("Movie Table",    "movietable",   92),
            ("Watchlist",      "watchlist",    80),
        ]

        for i, (text, page, w) in enumerate(nav_items):
            padx_left  = 6 if i == 0 else 2
            padx_right = 6 if i == len(nav_items) - 1 else 2
            btn = ctk.CTkButton(
                pill, text=text, width=w, height=32,
                fg_color="transparent", text_color="#AAAAAA",
                font=("Trebuchet MS", 11, "bold"),
                corner_radius=20, hover_color="#3A3A3A",
                command=lambda p=page: self.app.show_page(p)
            )
            btn.pack(side="left", padx=(padx_left, padx_right), pady=4)

    def _build_ui(self):
        self._build_nav()

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="#141414", corner_radius=0)
        self.scroll.pack(fill="both", expand=True)

        # ── DATA FILM ─────────────────────────────────────────────
        title         = self.movie.get("title", "Unknown Title")
        year          = self.movie.get("year", "N/A")
        rating_val    = self.movie.get("rating", "N/A")
        votes_val     = self.movie.get("votes", "0")   # FIX: ambil votes dari data film
        poster_path   = self.movie.get("poster_local", "")
        raw_genre     = self.movie.get("genre", "General")
        genres        = [g.strip() for g in raw_genre.split(",")] if isinstance(raw_genre, str) else ["Action"]
        synopsis_full = self.movie.get("synopsis", self.movie.get("description", "No synopsis available."))

        # ── 1. HERO SECTION ───────────────────────────────────────
        hero = ctk.CTkFrame(self.scroll, fg_color="#1c1c1c", corner_radius=0, height=340)
        hero.pack(fill="x")
        hero.pack_propagate(False)

        if poster_path and os.path.exists(poster_path):
            try:
                # FIX: resize ke ukuran lebih kecil sebelum blur → jauh lebih cepat
                target_w, target_h = 800, 227
                bg_img = Image.open(poster_path).convert("RGB")

                ratio  = max(target_w / bg_img.width, target_h / bg_img.height)
                new_w  = int(bg_img.width * ratio)
                new_h  = int(bg_img.height * ratio)
                bg_img = bg_img.resize((new_w, new_h), Image.LANCZOS)

                left   = (new_w - target_w) // 2
                top    = (new_h - target_h) // 2
                bg_img = bg_img.crop((left, top, left + target_w, top + target_h))

                bg_img = bg_img.filter(ImageFilter.GaussianBlur(radius=12))
                bg_img = ImageEnhance.Brightness(bg_img).enhance(0.25)

                # FIX: tetap display di ukuran 1200x340, tapi proses di 800x227
                self._hero_bg = ctk.CTkImage(light_image=bg_img, dark_image=bg_img,
                                             size=(1200, 340))
                bg_label = ctk.CTkLabel(hero, text="", image=self._hero_bg)
                bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            except Exception as e:
                print("Hero BG error:", e)

        hero_content = ctk.CTkFrame(hero, fg_color="transparent")
        hero_content.place(relx=0.05, rely=0.5, anchor="w")

        if poster_path and os.path.exists(poster_path):
            try:
                # FIX: pakai cache untuk poster thumb
                self._poster_thumb = self._load_image(poster_path, size=(160, 240))
                ctk.CTkLabel(hero_content, text="", image=self._poster_thumb).pack(side="left")
            except:
                pass

        info_frame = ctk.CTkFrame(hero_content, fg_color="transparent")
        info_frame.pack(side="left", padx=30, anchor="w")

        title_text = f"{title} ({year})" if year != "N/A" else title
        font_size = 28 if len(title_text) > 40 else 34
        ctk.CTkLabel(info_frame, text=title_text,
                     font=("Palatino Linotype", font_size, "italic"),
                     text_color="white", wraplength=750, anchor="w",
                     justify="left").pack(anchor="w")

        genre_row = ctk.CTkFrame(info_frame, fg_color="transparent")
        genre_row.pack(anchor="w", pady=(8, 0))
        for g in genres[:3]:
            ctk.CTkButton(genre_row, text=g, fg_color="#990000", text_color="white",
                          width=80, hover_color="#c0392b", corner_radius=20, height=28,
                          command=lambda genre=g: self._go_to_genre(genre)
                          ).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(info_frame, text=f"★ {rating_val}/10",
                     font=("Helvetica", 22, "bold"),
                     text_color="#FF3333").pack(anchor="w", pady=(10, 0))

        # ── KONTEN BAWAH ──────────────────────────────────────────
        content_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        content_frame.pack(fill="x", padx=50)

        # 2. SYNOPSIS FULL
        synopsis_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        synopsis_frame.pack(fill="x", pady=20)
        ctk.CTkLabel(synopsis_frame, text="Synopsis", font=("Helvetica", 18, "bold"),
                     text_color="#FF8C00", width=120, anchor="nw").pack(side="left")
        ctk.CTkLabel(synopsis_frame, text=synopsis_full, font=("Helvetica", 15),
                     text_color="#DDDDDD", wraplength=750, justify="left").pack(side="left", fill="both", expand=True)

        ctk.CTkFrame(content_frame, fg_color="#333", height=1).pack(fill="x", pady=20)

        # 3. WHERE TO WATCH
        wtw_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        wtw_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(wtw_frame, text="Where To Watch:", font=("Helvetica", 14, "bold"),
                     text_color="white").pack(side="left")

        plat_row = ctk.CTkFrame(wtw_frame, fg_color="transparent")
        plat_row.pack(side="left", padx=15)
        platform_str = self.movie.get("platform_string", "")
        platforms = [p.strip() for p in platform_str.split(",")] if platform_str else []
        if platforms:
            for p in platforms[:4]:
                ctk.CTkButton(plat_row, text=p, fg_color="#222", text_color="white",
                              hover=False, corner_radius=20, height=30).pack(side="left", padx=2)
        else:
            ctk.CTkLabel(plat_row, text="Not Available Online", text_color="gray").pack(side="left")

        # 4. CHART & WATCHLIST + REVIEW
        split_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        split_frame.pack(fill="x", pady=(40, 20), anchor="w")

        chart_frame = ctk.CTkFrame(split_frame, fg_color="transparent")
        chart_frame.pack(side="left", anchor="nw")
        ctk.CTkLabel(chart_frame, text="Ratings Distribution",
                     font=("Helvetica", 24, "bold"), text_color="white").pack(anchor="w", pady=(0, 20))

        # FIX: pass votes_val ke generate chart, terima total_votes juga
        ratings_data, total_votes = self._generate_dynamic_chart(rating_val, votes_val)

        for score in sorted(ratings_data.keys(), reverse=True):
            value = ratings_data[score]
            row = ctk.CTkFrame(chart_frame, fg_color="transparent")
            row.pack(fill="x", pady=5)
            ctk.CTkLabel(row, text=str(score), font=("Helvetica", 14),
                         text_color="white", width=30).pack(side="left")
            fill_width = max(5, int(value * 450))
            # FIX: corner_radius 5 → 2 (lebih ringan di render)
            ctk.CTkFrame(row, fg_color="#C00000", height=24,
                         width=fill_width, corner_radius=2).pack(side="left", padx=10)

        # FIX: tampilkan total orang yang sudah rating di bawah chart
        votes_display = f"{total_votes:,}" if total_votes > 0 else "N/A"
        if votes_display:
            ctk.CTkLabel(
                chart_frame,
                text=f"👥  {votes_display} ratings",
                font=("Helvetica", 18),
                text_color="#AAAAAA"
            ).pack(anchor="w", pady=(14, 0))

        wl_frame = ctk.CTkFrame(split_frame, fg_color="#1E1E1E", corner_radius=15)
        wl_frame.pack(side="left", fill="both", expand=True, padx=(80, 0), anchor="nw")

        wl_inner = ctk.CTkFrame(wl_frame, fg_color="transparent")
        wl_inner.pack(padx=30, pady=30, fill="both", expand=True)

        ctk.CTkLabel(wl_inner, text="Manage Watchlist",
                     font=("Helvetica", 24, "bold"), text_color="white").pack(anchor="w", pady=(0, 15))

        self.status_var = ctk.StringVar(value="Plan to Watch")
        self.status_menu = ctk.CTkOptionMenu(
            wl_inner, values=["Watched", "Watching", "Plan to Watch"],
            variable=self.status_var, fg_color="#333", button_color="#444",
            width=250, height=40,
            command=self._on_status_change
        )
        self.status_menu.pack(anchor="w", pady=(0, 20))

        ctk.CTkFrame(wl_inner, fg_color="#333", height=1).pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(wl_inner, text="My Review",
                     font=("Helvetica", 16, "bold"), text_color="#FF8C00").pack(anchor="w", pady=(0, 10))

        star_label_frame = ctk.CTkFrame(wl_inner, fg_color="transparent")
        star_label_frame.pack(anchor="w", pady=(0, 8))
        ctk.CTkLabel(star_label_frame, text="Rating:",
                     font=("Helvetica", 13), text_color="#AAAAAA").pack(side="left", padx=(0, 10))

        star_frame = ctk.CTkFrame(star_label_frame, fg_color="transparent")
        star_frame.pack(side="left")

        self.star_buttons = []
        for i in range(1, 11):
            btn = ctk.CTkButton(
                star_frame, text="☆", width=26, height=28,
                fg_color="transparent", hover_color="#2A2A2A",
                font=("Arial", 17), text_color="#555555",
                command=lambda n=i: self._set_stars(n)
            )
            btn.pack(side="left", padx=1)
            self.star_buttons.append(btn)

        existing_rating, existing_review = self._load_existing_review()
        if existing_rating > 0:
            self._set_stars(existing_rating)

        self._on_status_change(self.status_var.get())

        ctk.CTkLabel(wl_inner, text="Notes / Review:",
                     font=("Helvetica", 13), text_color="#AAAAAA").pack(anchor="w", pady=(5, 5))
        self.review_entry = ctk.CTkTextbox(
            wl_inner, width=250, height=90,
            fg_color="#2A2A2A", text_color="#FFFFFF",
            font=("Helvetica", 13), corner_radius=8
        )
        self.review_entry.pack(anchor="w", pady=(0, 15))

        if existing_review:
            self.review_entry.insert("1.0", existing_review)

        self.add_btn = ctk.CTkButton(
            wl_inner, text="+ Update Watchlist", fg_color="#FF8C00", text_color="black",
            font=("Helvetica", 15, "bold"), height=45, width=250,
            command=lambda: self._add_to_watchlist(self.status_var.get())
        )
        self.add_btn.pack(anchor="w")

        # 5. MORE STORIES
        more_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        more_frame.pack(fill="x", pady=(70, 40))
        ctk.CTkLabel(more_frame, text="More Stories",
                     font=("Helvetica", 20, "bold"), text_color="white",
                     width=150, anchor="nw").pack(side="left")

        posters_container = ctk.CTkFrame(more_frame, fg_color="transparent")
        posters_container.pack(side="left", fill="both", expand=True)

        all_movies = getattr(self.app, "movie_list", [])
        other_movies = [m for m in all_movies if m.get("title") != title]

        # FIX: sample sekali saja, disimpan di self._more_movies biar ga random ulang
        if other_movies:
            if self._more_movies is None:
                self._more_movies = random.sample(other_movies, min(len(other_movies), 4))
            for m_data in self._more_movies:
                m_path = m_data.get("poster_local", "")
                if m_path and os.path.exists(m_path):
                    try:
                        # FIX: pakai cache untuk thumbnail "More Stories"
                        m_img = self._load_image(m_path, size=(140, 200))
                        btn = ctk.CTkLabel(posters_container, text="", image=m_img, cursor="hand2")
                        btn.pack(side="left", padx=(0, 20))
                        btn.bind("<Button-1>", lambda e, d=m_data: self.app.show_page("moviedetail", data=d))
                    except:
                        pass

        # 6. BANNER FOOTER
        # FIX: tombol diubah ke Watchlist, karena Dashboard sudah ada di navbar atas
        banner = ctk.CTkFrame(self.scroll, fg_color="#FF8C00", corner_radius=0, height=120)
        banner.pack(fill="x", pady=(50, 0))
        banner.pack_propagate(False)
        ctk.CTkLabel(banner, text="Ready to track more movies?",
                     font=("Georgia", 24, "italic"), text_color="black").pack(pady=(20, 5))
        ctk.CTkButton(banner, text="Go to Watchlist", fg_color="#1A1A1A",
                      text_color="white", font=("Trebuchet MS", 13, "bold"),
                      command=lambda: self.app.show_page("watchlist")).pack()
