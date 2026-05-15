import customtkinter as ctk
import os
from PIL import Image
from styles import *

BG_MAIN    = "#1A1A1A"
BG_LIGHT   = "#F4F4F4"
TEXT_WHITE = "#FFFFFF"
TEXT_GRAY  = "#AAAAAA"
ACCENT     = "#E53935"

class MovietablePage(ctk.CTkFrame):
    def __init__(self, master, app, genre_filter=None):
        super().__init__(master, fg_color=BG_MAIN, corner_radius=0)
        self.app = app
        self.current_page = 0
        self.items_per_page = 10
        self.sort_key = "default"   # default | title | year_asc | year_desc | rating_asc | rating_desc | genre

        self.all_movies = getattr(self.app, "movie_list", [])
        self.filtered_list = self.all_movies.copy()

        self._build_ui()

        # Filter by genre kalau dipanggil dari movieDetail
        if genre_filter:
            self.after(100, lambda: self.filter_data(genre_filter))
        else:
            # Cek titipan search query
            pending = getattr(self.app, "search_query_pending", None)
            if pending:
                self.app.search_query_pending = None
                self.after(100, lambda: self.filter_data(pending))

    def _build_nav(self):
        nav = ctk.CTkFrame(self, fg_color="#111111", corner_radius=0, height=60)
        nav.pack(fill="x", side="top")
        nav.pack_propagate(False)

        search_frame = ctk.CTkFrame(nav, fg_color="transparent")
        search_frame.pack(side="right", padx=20, pady=10)
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search Local...", width=150, height=32, fg_color="#222", border_color="#444")
        self.search_entry.pack(side="left", padx=5)
        ctk.CTkButton(search_frame, text="🔍", width=40, height=32, fg_color="#E53935",
                      command=lambda: self.filter_data(self.search_entry.get())).pack(side="left")

        pill_outer = ctk.CTkFrame(nav, fg_color="transparent")
        pill_outer.place(relx=0.5, rely=0.5, anchor="center")
        pill = ctk.CTkFrame(pill_outer, fg_color="#2E2E2E", corner_radius=20, height=34)
        pill.pack()

        ctk.CTkButton(pill, text="Home", width=70, height=28, fg_color="transparent", text_color="#AAAAAA", corner_radius=16, font=("Trebuchet MS", 11, "bold"), command=lambda: self.app.show_page("dashboard")).pack(side="left", padx=(3, 1), pady=3)
        ctk.CTkButton(pill, text="Genre Analysis", width=110, height=28, fg_color="transparent", text_color="#AAAAAA", corner_radius=16, font=("Trebuchet MS", 11, "bold"), command=lambda: self.app.show_page("genreanalyze")).pack(side="left", padx=1, pady=3)
        ctk.CTkButton(pill, text="Movie Table", width=92, height=28, fg_color="#E53935", text_color="#FFFFFF", corner_radius=16, font=("Trebuchet MS", 11, "bold")).pack(side="left", padx=(1, 3), pady=3)
        ctk.CTkButton(pill, text="Watchlist", width=80, height=28, fg_color="transparent", text_color="#AAAAAA", corner_radius=16, font=("Trebuchet MS", 11, "bold"), command=lambda: self.app.show_page("watchlist")).pack(side="left", padx=(1, 3), pady=3)

    def _apply_sort(self, data):
        """Sort data sesuai sort_key yang aktif"""
        if self.sort_key == "title":
            return sorted(data, key=lambda m: m.get("title", "").lower())
        elif self.sort_key == "year_desc":
            return sorted(data, key=lambda m: m.get("year", "0"), reverse=True)
        elif self.sort_key == "year_asc":
            return sorted(data, key=lambda m: m.get("year", "0"))
        elif self.sort_key == "rating_desc":
            return sorted(data, key=lambda m: float(m.get("rating", 0) or 0), reverse=True)
        elif self.sort_key == "rating_asc":
            return sorted(data, key=lambda m: float(m.get("rating", 0) or 0))
        elif self.sort_key == "genre":
            return sorted(data, key=lambda m: m.get("genre", "").lower())
        return data  # default: urutan asli

    def filter_data(self, query):
        if query is None:
            return
        query = query.lower().strip()
        self.current_page = 0

        all_data = getattr(self.app, "movie_list", [])
        self.all_movies = all_data

        if not query:
            filtered = all_data.copy()
        else:
            filtered = [
                m for m in all_data
                if query in str(m.get("title", "")).lower() or
                   query in str(m.get("genre", "")).lower()
            ]

        self.filtered_list = self._apply_sort(filtered)
        self.render_table()

    def _set_sort(self, key):
        self.sort_key = key
        self.current_page = 0
        # Re-apply sort ke filtered_list yang sekarang
        self.filtered_list = self._apply_sort(self.filtered_list)
        self.render_table()
        # Update warna tombol sort
        self._refresh_sort_buttons()

    def _refresh_sort_buttons(self):
        for key, btn in self._sort_buttons.items():
            if key == self.sort_key:
                btn.configure(fg_color=ACCENT, text_color=TEXT_WHITE)
            else:
                btn.configure(fg_color="#DDDDDD", text_color="#333333")

    def _build_ui(self):
        self._build_nav()

        # ── HEADER ─────────────────────────────────────────────────────────
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=(25, 5))
        ctk.CTkLabel(header_frame, text="All Movies", font=("Helvetica", 36, "bold"), text_color=TEXT_WHITE).pack()

        # ── SORT BAR ───────────────────────────────────────────────────────
        sort_frame = ctk.CTkFrame(self, fg_color="transparent")
        sort_frame.pack(pady=(0, 10))

        ctk.CTkLabel(sort_frame, text="Sort by:", font=("Trebuchet MS", 12), text_color=TEXT_GRAY).pack(side="left", padx=(0, 8))

        self._sort_buttons = {}
        sort_options = [
            ("Default",       "default"),
            ("A–Z Title",     "title"),
            ("Newest",        "year_desc"),
            ("Oldest",        "year_asc"),
            ("Rating ↓",      "rating_desc"),
            ("Rating ↑",      "rating_asc"),
            ("Genre A–Z",     "genre"),
        ]
        for label, key in sort_options:
            is_active = (key == self.sort_key)
            btn = ctk.CTkButton(
                sort_frame, text=label, width=85, height=28,
                fg_color=ACCENT if is_active else "#DDDDDD",
                text_color=TEXT_WHITE if is_active else "#333333",
                hover_color="#c0392b" if is_active else "#BBBBBB",
                font=("Trebuchet MS", 11, "bold"),
                corner_radius=14,
                command=lambda k=key: self._set_sort(k)
            )
            btn.pack(side="left", padx=3)
            self._sort_buttons[key] = btn

        # ── TABLE ──────────────────────────────────────────────────────────
        self.table_container = ctk.CTkFrame(self, fg_color=BG_LIGHT, corner_radius=15)
        self.table_container.pack(fill="both", expand=True, padx=40, pady=(0, 20))

        self.rows_frame = ctk.CTkScrollableFrame(self.table_container, fg_color="transparent")
        self.rows_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.pagination_frame = ctk.CTkFrame(self.table_container, fg_color="transparent")
        self.pagination_frame.pack(fill="x", pady=15)

        self.render_table()

    def render_table(self):
        for widget in self.rows_frame.winfo_children():
            widget.destroy()
        for widget in self.pagination_frame.winfo_children():
            widget.destroy()

        start = self.current_page * self.items_per_page
        end = start + self.items_per_page
        movies_to_show = self.filtered_list[start:end]
        total_pages = (len(self.filtered_list) + self.items_per_page - 1) // self.items_per_page

        if not movies_to_show:
            ctk.CTkLabel(self.rows_frame, text="No movies found.", font=("Trebuchet MS", 14), text_color="#888888").pack(pady=40)

        for movie in movies_to_show:
            card = ctk.CTkFrame(self.rows_frame, fg_color="#FFFFFF", corner_radius=10, height=90, cursor="hand2")
            card.pack(fill="x", padx=10, pady=6)
            card.pack_propagate(False)

            def go_to_detail(e, m=movie):
                self.app.show_page("moviedetail", data=m)

            # Poster
            poster_lbl = ctk.CTkLabel(card, text="🎬", fg_color="#E0E0E0", width=50, height=75, corner_radius=5)
            poster_lbl.pack(side="left", padx=10, pady=7)
            path = movie.get("poster_local", "")
            if path and os.path.exists(path):
                try:
                    img = ctk.CTkImage(Image.open(path), size=(50, 75))
                    poster_lbl.configure(image=img, text="")
                except:
                    pass

            # Info
            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            title_lbl = ctk.CTkLabel(info, text=movie.get("title", "Unknown"), font=("Trebuchet MS", 16, "bold"), text_color="#7A1C1C", anchor="w")
            title_lbl.pack(fill="x")
            subtitle_lbl = ctk.CTkLabel(info, text=f"{movie.get('year', 'N/A')} • {movie.get('genre', 'N/A')}", font=("Trebuchet MS", 12), text_color="#555555", anchor="w")
            subtitle_lbl.pack(fill="x")

            # Rating
            rt_frame = ctk.CTkFrame(card, fg_color="transparent")
            rt_frame.pack(side="right", padx=20)
            rat_val = ctk.CTkLabel(rt_frame, text=f"{movie.get('rating', 'N/A')}", font=("Helvetica", 18, "bold"), text_color="#8A4B1A")
            rat_val.pack()
            rat_text = ctk.CTkLabel(rt_frame, text="⭐ IMDb", font=("Trebuchet MS", 10), text_color="#AAAAAA")
            rat_text.pack()

            # Bind klik ke semua elemen
            for w in [card, poster_lbl, info, title_lbl, subtitle_lbl, rt_frame, rat_val, rat_text]:
                w.bind("<Button-1>", go_to_detail)

        # Pagination
        ctk.CTkButton(self.pagination_frame, text="◀ Prev", width=100, fg_color=ACCENT,
                      command=self.prev_page,
                      state="normal" if self.current_page > 0 else "disabled").pack(side="left", padx=40)
        ctk.CTkLabel(self.pagination_frame, text=f"Page {self.current_page + 1} of {max(1, total_pages)}", text_color="black").pack(side="left", expand=True)
        ctk.CTkButton(self.pagination_frame, text="Next ▶", width=100, fg_color=ACCENT,
                      command=self.next_page,
                      state="normal" if end < len(self.filtered_list) else "disabled").pack(side="right", padx=40)

    def prev_page(self):
        self.current_page -= 1
        self.render_table()

    def next_page(self):
        self.current_page += 1
        self.render_table()