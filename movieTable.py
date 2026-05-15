import customtkinter as ctk
import tkinter as tk
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
        self.items_per_page = 20
        self.sort_key = "default"

        self.all_movies = getattr(self.app, "movie_list", [])
        self.filtered_list = self.all_movies.copy()

        self._genre_selected = set()

        self._build_ui()

        if genre_filter:
            self.after(100, lambda: self._toggle_genre(genre_filter))
        else:
            pending = getattr(self.app, "search_query_pending", None)
            if pending:
                self.app.search_query_pending = None
                self.after(100, lambda: self._search(pending))

    # ── NAVBAR ────────────────────────────────────────────────────────────────
    def _build_nav(self):
        nav = ctk.CTkFrame(self, fg_color="#111111", corner_radius=0, height=60)
        nav.pack(fill="x", side="top")
        nav.pack_propagate(False)

        search_frame = ctk.CTkFrame(nav, fg_color="transparent")
        search_frame.pack(side="right", padx=20, pady=10)
        self.search_entry = ctk.CTkEntry(
            search_frame, placeholder_text="Search...",
            width=150, height=32, fg_color="#222", border_color="#444"
        )
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<Return>", lambda e: self._search(self.search_entry.get()))
        ctk.CTkButton(
            search_frame, text="🔍", width=40, height=32, fg_color=ACCENT,
            command=lambda: self._search(self.search_entry.get())
        ).pack(side="left")

        pill_outer = ctk.CTkFrame(nav, fg_color="transparent")
        pill_outer.place(relx=0.5, rely=0.5, anchor="center")
        pill = ctk.CTkFrame(pill_outer, fg_color="#2E2E2E", corner_radius=20, height=34)
        pill.pack()

        ctk.CTkButton(pill, text="Home", width=70, height=28, fg_color="transparent",
                      text_color="#AAAAAA", corner_radius=16, font=("Trebuchet MS", 11, "bold"),
                      command=lambda: self.app.show_page("dashboard")).pack(side="left", padx=(3,1), pady=3)
        ctk.CTkButton(pill, text="Genre Analysis", width=110, height=28, fg_color="transparent",
                      text_color="#AAAAAA", corner_radius=16, font=("Trebuchet MS", 11, "bold"),
                      command=lambda: self.app.show_page("genreanalyze")).pack(side="left", padx=1, pady=3)
        ctk.CTkButton(pill, text="Movie Table", width=92, height=28, fg_color=ACCENT,
                      text_color="#FFFFFF", corner_radius=16, font=("Trebuchet MS", 11, "bold")).pack(side="left", padx=(1,3), pady=3)
        ctk.CTkButton(pill, text="Watchlist", width=80, height=28, fg_color="transparent",
                      text_color="#AAAAAA", corner_radius=16, font=("Trebuchet MS", 11, "bold"),
                      command=lambda: self.app.show_page("watchlist")).pack(side="left", padx=(1,3), pady=3)

    # ── SORT & FILTER ─────────────────────────────────────────────────────────
    def _apply_sort(self, data):
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
        return data

    def _apply_filters(self):
        if hasattr(self, "_filter_job") and self._filter_job:
            try:
                self.after_cancel(self._filter_job)
            except Exception:
                pass
        self._filter_job = self.after(120, self._do_apply_filters)

    def _do_apply_filters(self):
        self._filter_job = None
        self.current_page = 0
        all_data = getattr(self.app, "movie_list", [])

        if self._genre_selected:
            filtered = []
            for m in all_data:
                film_genres = {g.strip() for g in str(m.get("genre", "")).split(",")}
                if self._genre_selected.issubset(film_genres):
                    filtered.append(m)
        else:
            filtered = all_data.copy()

        q = self.search_entry.get().lower().strip() if hasattr(self, "search_entry") else ""
        if q:
            filtered = [m for m in filtered
                        if q in str(m.get("title", "")).lower()
                        or q in str(m.get("genre", "")).lower()]

        self.filtered_list = self._apply_sort(filtered)
        self.render_table()

    def _search(self, query):
        self._apply_filters()

    def _toggle_genre_dropdown(self):
        if self._genre_dropdown_open:
            self._close_genre_dropdown()
        else:
            self._open_genre_dropdown()

    def _open_genre_dropdown(self):
        self._genre_dropdown_open = True
        self._genre_btn_main.configure(text="Genre ▲", fg_color=ACCENT)

        btn = self._genre_btn_main
        btn.update_idletasks()
        x = btn.winfo_rootx()
        y = btn.winfo_rooty() + btn.winfo_height() + 4

        popup = tk.Toplevel(self)
        popup.overrideredirect(True)
        popup.configure(bg="#222222")
        popup.geometry(f"540x{min(40 * ((len(self._all_genres) // 4) + 3), 400)}+{x}+{y}")
        popup.attributes("-topmost", True)
        self._genre_popup = popup

        inner = ctk.CTkFrame(popup, fg_color="#222222", corner_radius=12,
                              border_width=1, border_color="#444")
        inner.pack(fill="both", expand=True, padx=1, pady=1)

        self._btn_all = ctk.CTkButton(
            inner, text="✕ Clear All", width=100, height=26,
            fg_color="#444", text_color=TEXT_WHITE,
            corner_radius=13, font=("Trebuchet MS", 10, "bold"),
            command=self._clear_genres
        )
        self._btn_all.grid(row=0, column=0, columnspan=2, padx=8, pady=(8, 4), sticky="w")

        COLS = 4
        self._genre_buttons = {}
        for i, g in enumerate(self._all_genres):
            row_i = i // COLS + 1
            col_i = i % COLS
            active = g in self._genre_selected
            btn_g = ctk.CTkButton(
                inner, text=g, width=110, height=28,
                fg_color=ACCENT if active else "#333333",
                text_color=TEXT_WHITE if active else TEXT_GRAY,
                hover_color="#c0392b" if active else "#3E3E3E",
                corner_radius=13, font=("Trebuchet MS", 10, "bold"),
                border_width=1, border_color=ACCENT if active else "#555",
                command=lambda genre=g: self._toggle_genre(genre)
            )
            btn_g.grid(row=row_i, column=col_i, padx=5, pady=4, sticky="ew")
            self._genre_buttons[g] = btn_g

        for col in range(COLS):
            inner.columnconfigure(col, weight=1)

        popup.bind("<FocusOut>", lambda e: self.after(100, self._check_focus_and_close))
        popup.focus_set()

    def _check_focus_and_close(self):
        if self._genre_popup and self._genre_dropdown_open:
            try:
                focused = self._genre_popup.focus_get()
                if focused is None:
                    self._close_genre_dropdown()
            except Exception:
                self._close_genre_dropdown()

    def _close_genre_dropdown(self):
        self._genre_dropdown_open = False
        self._genre_btn_main.configure(
            text="Genre ▼",
            fg_color=ACCENT if self._genre_selected else "#2E2E2E"
        )
        if self._genre_popup:
            try:
                self._genre_popup.destroy()
            except Exception:
                pass
            self._genre_popup = None
        try:
            self.unbind("<Button-1>")
        except Exception:
            pass

    def _refresh_genre_buttons(self):
        has_selection = bool(self._genre_selected)
        self._genre_btn_main.configure(
            fg_color=ACCENT if has_selection else "#2E2E2E"
        )
        if self._genre_selected:
            label_text = ", ".join(sorted(self._genre_selected))
            if len(label_text) > 40:
                label_text = label_text[:37] + "..."
            self._genre_label.configure(text=label_text, text_color=TEXT_WHITE)
        else:
            self._genre_label.configure(text="All genres", text_color=TEXT_GRAY)

        if self._genre_popup:
            for g, btn in self._genre_buttons.items():
                active = g in self._genre_selected
                btn.configure(
                    fg_color=ACCENT if active else "#333333",
                    text_color=TEXT_WHITE if active else TEXT_GRAY,
                    border_color=ACCENT if active else "#555"
                )

    def _toggle_genre(self, genre):
        if genre in self._genre_selected:
            self._genre_selected.discard(genre)
        else:
            self._genre_selected.add(genre)
        self._refresh_genre_buttons()
        self._apply_filters()

    def _clear_genres(self):
        self._genre_selected.clear()
        self._refresh_genre_buttons()
        self._apply_filters()

    def _set_sort(self, key):
        self.sort_key = key
        self.current_page = 0
        self.filtered_list = self._apply_sort(self.filtered_list)
        self.render_table()
        self._refresh_sort_buttons()

    def _refresh_sort_buttons(self):
        for key, btn in self._sort_buttons.items():
            if key == self.sort_key:
                btn.configure(fg_color=ACCENT, text_color=TEXT_WHITE)
            else:
                btn.configure(fg_color="#2E2E2E", text_color=TEXT_GRAY)

    # ── BUILD UI ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        self._build_nav()

        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=(20, 8))
        ctk.CTkLabel(
            header_frame, text="Find your movie!",
            font=("Georgia", 38, "bold"), text_color=TEXT_WHITE, compound="center"
        ).pack()

        filter_sort_row = ctk.CTkFrame(self, fg_color="transparent")
        filter_sort_row.pack(fill="x", padx=40, pady=(0, 10))

        self._genre_dropdown_open = False
        self._genre_btn_main = ctk.CTkButton(
            filter_sort_row, text="Genre ▼", width=100, height=32,
            fg_color="#2E2E2E", text_color=TEXT_WHITE,
            hover_color="#3E3E3E", corner_radius=16,
            font=("Trebuchet MS", 11, "bold"),
            command=self._toggle_genre_dropdown
        )
        self._genre_btn_main.pack(side="left", padx=(0, 12))

        self._genre_label = ctk.CTkLabel(
            filter_sort_row, text="All genres",
            font=("Trebuchet MS", 11), text_color=TEXT_GRAY
        )
        self._genre_label.pack(side="left", padx=(0, 20))

        ctk.CTkFrame(filter_sort_row, fg_color="#444", width=1, height=24).pack(side="left", padx=(0, 12))

        ctk.CTkLabel(
            filter_sort_row, text="Sort :",
            font=("Trebuchet MS", 12, "bold"), text_color=TEXT_GRAY
        ).pack(side="left", padx=(0, 8))

        self._sort_buttons = {}
        sort_options = [
            ("Default",   "default"),
            ("A–Z Title", "title"),
            ("Newest",    "year_desc"),
            ("Oldest",    "year_asc"),
            ("Rating ↓",  "rating_desc"),
            ("Rating ↑",  "rating_asc"),
        ]
        for label, key in sort_options:
            is_active = (key == self.sort_key)
            btn = ctk.CTkButton(
                filter_sort_row, text=label, width=82, height=28,
                fg_color=ACCENT if is_active else "#2E2E2E",
                text_color=TEXT_WHITE if is_active else TEXT_GRAY,
                hover_color="#c0392b" if is_active else "#3E3E3E",
                font=("Trebuchet MS", 11, "bold"),
                corner_radius=14,
                command=lambda k=key: self._set_sort(k)
            )
            btn.pack(side="left", padx=3)
            self._sort_buttons[key] = btn

        self._count_label = ctk.CTkLabel(
            filter_sort_row, text="",
            font=("Trebuchet MS", 11), text_color=TEXT_GRAY
        )
        self._count_label.pack(side="right", padx=8)

        all_genres = set()
        for m in self.all_movies:
            for g in str(m.get("genre", "")).split(","):
                g = g.strip()
                if g:
                    all_genres.add(g)
        self._all_genres = sorted(all_genres)
        self._genre_buttons = {}
        self._genre_popup = None

        self.table_container = ctk.CTkFrame(self, fg_color="#1A1A1A", corner_radius=15)
        self.table_container.pack(fill="both", expand=True, padx=40, pady=(0, 20))

        self._setup_canvas_scroll()

        self.pagination_frame = ctk.CTkFrame(self.table_container, fg_color="transparent")
        self.pagination_frame.pack(fill="x", pady=15)

        self.render_table()

    def _setup_canvas_scroll(self):
        canvas_wrapper = ctk.CTkFrame(self.table_container, fg_color="transparent")
        canvas_wrapper.pack(fill="both", expand=True, padx=20, pady=(10, 0))

        # Scrollbar invisible tapi tetap fungsional
        self._scrollbar = tk.Scrollbar(canvas_wrapper, orient="vertical", width=0)

        self._canvas = tk.Canvas(
            canvas_wrapper, bg="#1A1A1A",
            highlightthickness=0,
            yscrollcommand=self._scrollbar.set
        )
        self._canvas.pack(side="left", fill="both", expand=True)
        self._scrollbar.config(command=self._canvas.yview)

        self.rows_frame = ctk.CTkFrame(self._canvas, fg_color="transparent", corner_radius=0)
        self._canvas_window = self._canvas.create_window(
            (0, 0), window=self.rows_frame, anchor="nw"
        )

        def _on_frame_configure(e):
            self._canvas.configure(scrollregion=self._canvas.bbox("all"))

        def _on_canvas_configure(e):
            self._canvas.itemconfig(self._canvas_window, width=e.width)

        self.rows_frame.bind("<Configure>", _on_frame_configure)
        self._canvas.bind("<Configure>", _on_canvas_configure)

        # Aktifkan scroll saat cursor masuk area canvas, nonaktifkan saat keluar
        # Touchpad dan mouse scroll dua-duanya jalan dengan cara ini
        self._canvas.bind("<Enter>", lambda e: self._bind_mousewheel())
        self._canvas.bind("<Leave>", lambda e: self._unbind_mousewheel())

    def _bind_mousewheel(self):
        self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self._canvas.bind_all("<Button-4>",   self._on_mousewheel_up)
        self._canvas.bind_all("<Button-5>",   self._on_mousewheel_down)

    def _unbind_mousewheel(self):
        try:
            self._canvas.unbind_all("<MouseWheel>")
            self._canvas.unbind_all("<Button-4>")
            self._canvas.unbind_all("<Button-5>")
        except Exception:
            pass

    def _on_mousewheel(self, event):
        delta = event.delta
        if delta == 0:
            return
        # delta/60: mouse wheel (±120) → ±2 unit, touchpad kecil → ±1 unit
        scroll = -int(delta / 60)
        if scroll == 0:
            scroll = -1 if delta > 0 else 1
        self._canvas.yview_scroll(scroll, "units")

    def _on_mousewheel_up(self, event):
        self._canvas.yview_scroll(-2, "units")

    def _on_mousewheel_down(self, event):
        self._canvas.yview_scroll(2, "units")

    def destroy(self):
        self._unbind_mousewheel()
        super().destroy()

    # ── RENDER TABEL ─────────────────────────────────────────────────────────
    def render_table(self):
        for widget in self.rows_frame.winfo_children():
            widget.destroy()
        for widget in self.pagination_frame.winfo_children():
            widget.destroy()

        self._canvas.yview_moveto(0)

        COLS = 5
        start = self.current_page * self.items_per_page
        end   = start + self.items_per_page
        movies_to_show = self.filtered_list[start:end]
        total = len(self.filtered_list)
        total_pages = (total + self.items_per_page - 1) // self.items_per_page

        genre_info = f"  •  {len(self._genre_selected)} genre selected" if self._genre_selected else ""
        self._count_label.configure(text=f"{total} films{genre_info}")

        if not movies_to_show:
            ctk.CTkLabel(
                self.rows_frame, text="No movies found. 😔",
                font=("Trebuchet MS", 14), text_color="#888888"
            ).pack(pady=60)
            self._render_pagination(total_pages, end)
            return

        grid = ctk.CTkFrame(self.rows_frame, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=6, pady=6)
        for col in range(COLS):
            grid.columnconfigure(col, weight=1, uniform="col")

        self._poster_cache = []

        for idx, movie in enumerate(movies_to_show):
            row_i = idx // COLS
            col_i = idx % COLS

            def go_to_detail(e, m=movie):
                self.app.show_page("moviedetail", data=m)

            BG_CARD       = "#2E2E2E"
            BG_CARD_HOVER = "#3D3D3D"

            card = ctk.CTkFrame(grid, fg_color=BG_CARD, corner_radius=10,
                                 cursor="hand2", border_width=1, border_color="#444")
            card.grid(row=row_i, column=col_i, padx=6, pady=6, sticky="n")

            POSTER_W, POSTER_H = 160, 220
            poster_lbl = ctk.CTkLabel(card, text="🎬", fg_color="#1A1A1A",
                                       width=POSTER_W, height=POSTER_H, corner_radius=8)
            poster_lbl.pack(padx=8, pady=(8, 0))

            path = movie.get("poster_local", "")
            if path and os.path.exists(path):
                try:
                    img = ctk.CTkImage(Image.open(path), size=(POSTER_W, POSTER_H))
                    self._poster_cache.append(img)
                    poster_lbl.configure(image=img, text="")
                except Exception:
                    pass

            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(fill="x", padx=8, pady=(6, 8))

            title_lbl = ctk.CTkLabel(
                info, text=movie.get("title", "Unknown"),
                font=("Trebuchet MS", 12, "bold"), text_color=TEXT_WHITE,
                anchor="w", wraplength=POSTER_W, justify="left"
            )
            title_lbl.pack(fill="x")

            sub_lbl = ctk.CTkLabel(
                info, text=f"{movie.get('year','N/A')}  •  {movie.get('genre','N/A')}",
                font=("Trebuchet MS", 10), text_color=TEXT_GRAY,
                anchor="w", wraplength=POSTER_W, justify="left"
            )
            sub_lbl.pack(fill="x")

            rating_row = ctk.CTkFrame(info, fg_color="transparent")
            rating_row.pack(fill="x", pady=(2, 0))

            rat_val = ctk.CTkLabel(
                rating_row, text=f"⭐ {movie.get('rating','N/A')}",
                font=("Trebuchet MS", 11, "bold"), text_color=ACCENT, anchor="w"
            )
            rat_val.pack(side="left")

            rat_imdb = ctk.CTkLabel(
                rating_row, text="IMDb",
                font=("Trebuchet MS", 9), text_color=TEXT_GRAY, anchor="w"
            )
            rat_imdb.pack(side="left", padx=(4, 0))

            # ── HOVER ANIMASI LIFT ─────────────────────────────────────────
            # Efek: card "naik" (pady atas dikurangi dari 6 → 2, bawah ditambah → 10)
            # border merah menyala, background sedikit lebih terang
            # Di-bind ke SEMUA child widget termasuk poster_lbl
            # sehingga hover aktif di seluruh area card, bukan cuma frame-nya saja
            def _enter(e, c=card):
                c.configure(fg_color=BG_CARD_HOVER, border_color=ACCENT, border_width=2)
                c.grid_configure(pady=(2, 10))

            def _leave(e, c=card):
                c.configure(fg_color=BG_CARD, border_color="#444", border_width=1)
                c.grid_configure(pady=6)

            all_widgets = [card, poster_lbl, info, title_lbl, sub_lbl, rating_row, rat_val, rat_imdb]
            for w in all_widgets:
                w.bind("<Enter>", _enter)
                w.bind("<Leave>", _leave)
                w.bind("<Button-1>", go_to_detail)

        self._render_pagination(total_pages, end)

    def _render_pagination(self, total_pages, end):
        ctk.CTkButton(
            self.pagination_frame, text="◀ Prev", width=100, fg_color=ACCENT,
            command=self.prev_page,
            state="normal" if self.current_page > 0 else "disabled"
        ).pack(side="left", padx=40)
        ctk.CTkLabel(
            self.pagination_frame,
            text=f"Page {self.current_page + 1} of {max(1, total_pages)}",
            text_color=TEXT_WHITE
        ).pack(side="left", expand=True)
        ctk.CTkButton(
            self.pagination_frame, text="Next ▶", width=100, fg_color=ACCENT,
            command=self.next_page,
            state="normal" if end < len(self.filtered_list) else "disabled"
        ).pack(side="right", padx=40)

    def prev_page(self):
        self.current_page -= 1
        self.render_table()
        self._canvas.yview_moveto(0)

    def next_page(self):
        self.current_page += 1
        self.render_table()
        self._canvas.yview_moveto(0)
