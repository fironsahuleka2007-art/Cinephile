import customtkinter as ctk
import tkinter as tk
import os
import threading
from PIL import Image
from styles import *

BG_MAIN       = "#1A1A1A"
TEXT_WHITE     = "#FFFFFF"
TEXT_GRAY      = "#AAAAAA"
ACCENT         = "#7A1C1C"
BG_CARD        = "#2E2E2E"
BG_CARD_HOVER  = "#3D3D3D"
POSTER_W, POSTER_H = 160, 220

class MovietablePage(ctk.CTkFrame):
    def __init__(self, master, app, genre_filter=None):
        super().__init__(master, fg_color=BG_MAIN, corner_radius=0)
        self.app           = app
        self.current_page  = 0
        self.items_per_page = 20
        self.sort_key      = "default"
        self._filter_job   = None
        self._genre_selected  = set()
        self._genre_dropdown_open = False
        self._genre_popup  = None
        self._poster_cache = {}
        self._sort_buttons = {}
        self._genre_buttons = {}

        # FIX tiling: counter generasi render
        self._render_gen = 0

        self.all_movies    = getattr(self.app, "movie_list", [])
        self.filtered_list = self.all_movies.copy()

        genres = set()
        for m in self.all_movies:
            for g in str(m.get("genre", "")).split(","):
                g = g.strip()
                if g:
                    genres.add(g)
        self._all_genres = sorted(genres)

        self._build_ui()

        if genre_filter:
            self.after(100, lambda: self._toggle_genre(genre_filter))
        else:
            pending = getattr(self.app, "search_query_pending", None)
            if pending:
                self.app.search_query_pending = None
                self.after(100, lambda: self._apply_filters())

    # ── NAVBAR ───────────────────────────────────────────────────────────────
    def _build_nav(self):
        nav = ctk.CTkFrame(self, fg_color="#111111", corner_radius=0, height=60)
        nav.pack(fill="x", side="top")
        nav.pack_propagate(False)

        sf = ctk.CTkFrame(nav, fg_color="transparent")
        sf.pack(side="right", padx=20, pady=10)
        self.search_entry = ctk.CTkEntry(sf, placeholder_text="Search...",
                                          width=150, height=32, fg_color="#222", border_color="#444")
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<Return>", lambda e: self._apply_filters())
        ctk.CTkButton(sf, text="🔍", width=40, height=32, fg_color=ACCENT,
                      command=self._apply_filters).pack(side="left")

        pill_outer = ctk.CTkFrame(nav, fg_color="transparent")
        pill_outer.place(relx=0.5, rely=0.5, anchor="center")
        pill = ctk.CTkFrame(pill_outer, fg_color="#2E2E2E", corner_radius=20, height=34)
        pill.pack()
        for text, page, active in [("Home","dashboard",False),("Genre Analyze","genreanalyze",False),
                                    ("Movie Table",None,True),("Watchlist","watchlist",False)]:
            ctk.CTkButton(pill, text=text, width=90 if text=="Genre Analyze" else 80,
                          height=28, corner_radius=16, font=("Trebuchet MS",11,"bold"),
                          fg_color=ACCENT if active else "transparent",
                          text_color=TEXT_WHITE if active else TEXT_GRAY,
                          hover_color="#c0392b" if active else "#3A3A3A",
                          command=(lambda p=page: self.app.show_page(p)) if page else None
                          ).pack(side="left", padx=2, pady=3)

    # ── SORT / FILTER ────────────────────────────────────────────────────────
    def _apply_sort(self, data):
        k = self.sort_key
        if k == "title":      return sorted(data, key=lambda m: m.get("title","").lower())
        if k == "year_desc":  return sorted(data, key=lambda m: m.get("year","0"), reverse=True)
        if k == "year_asc":   return sorted(data, key=lambda m: m.get("year","0"))
        if k == "rating_desc":return sorted(data, key=lambda m: float(m.get("rating",0) or 0), reverse=True)
        if k == "rating_asc": return sorted(data, key=lambda m: float(m.get("rating",0) or 0))
        return data

    def _apply_filters(self, *_):
        if self._filter_job:
            try: self.after_cancel(self._filter_job)
            except: pass
        self._filter_job = self.after(150, self._do_filter)

    def _do_filter(self):
        self._filter_job = None
        self.current_page = 0
        data = getattr(self.app, "movie_list", [])

        if self._genre_selected:
            result = []
            for m in data:
                fg = {g.strip() for g in str(m.get("genre","")).split(",")}
                if self._genre_selected.issubset(fg):
                    result.append(m)
        else:
            result = data.copy()

        q = self.search_entry.get().lower().strip()
        if q:
            result = [m for m in result
                      if q in str(m.get("title","")).lower()
                      or q in str(m.get("genre","")).lower()]

        self.filtered_list = self._apply_sort(result)
        self.render_table()

    def _set_sort(self, key):
        self.sort_key = key
        self.current_page = 0
        self.filtered_list = self._apply_sort(self.filtered_list)
        for k, b in self._sort_buttons.items():
            b.configure(fg_color=ACCENT if k==key else "#2E2E2E",
                        text_color=TEXT_WHITE if k==key else TEXT_GRAY)
        self.render_table()

    def _toggle_genre(self, genre):
        if genre in self._genre_selected: self._genre_selected.discard(genre)
        else:                              self._genre_selected.add(genre)
        self._refresh_genre_ui()
        self._apply_filters()

    def _clear_genres(self):
        self._genre_selected.clear()
        self._refresh_genre_ui()
        self._apply_filters()

    def _refresh_genre_ui(self):
        has = bool(self._genre_selected)
        self._genre_btn_main.configure(fg_color=ACCENT if has else "#2E2E2E")
        if has:
            txt = ", ".join(sorted(self._genre_selected))
            self._genre_label.configure(text=txt[:40]+"..." if len(txt)>40 else txt,
                                         text_color=TEXT_WHITE)
        else:
            self._genre_label.configure(text="All genres", text_color=TEXT_GRAY)
        if self._genre_popup:
            for g, b in self._genre_buttons.items():
                active = g in self._genre_selected
                b.configure(fg_color=ACCENT if active else "#333",
                             text_color=TEXT_WHITE if active else TEXT_GRAY,
                             border_color=ACCENT if active else "#555")

    # ── GENRE DROPDOWN ───────────────────────────────────────────────────────
    def _toggle_genre_dropdown(self):
        if self._genre_dropdown_open: self._close_genre_dropdown()
        else:                          self._open_genre_dropdown()

    def _open_genre_dropdown(self):
        self._genre_dropdown_open = True
        self._genre_btn_main.configure(text="Genre ▲", fg_color=ACCENT)
        btn = self._genre_btn_main
        btn.update_idletasks()
        x = btn.winfo_rootx()
        y = btn.winfo_rooty() + btn.winfo_height() + 4
        rows = (len(self._all_genres) + 3) // 4
        h = min(rows * 38 + 56, 420)

        popup = tk.Toplevel(self)
        popup.overrideredirect(True)
        popup.configure(bg="#222222")
        popup.geometry(f"540x{h}+{x}+{y}")
        popup.attributes("-topmost", True)
        self._genre_popup = popup

        inner = ctk.CTkFrame(popup, fg_color="#222222", corner_radius=12,
                               border_width=1, border_color="#444")
        inner.pack(fill="both", expand=True, padx=1, pady=1)

        ctk.CTkButton(inner, text="✕ Clear All", width=100, height=26,
                       fg_color="#444", text_color=TEXT_WHITE, corner_radius=13,
                       font=("Trebuchet MS",10,"bold"),
                       command=self._clear_genres
                       ).grid(row=0, column=0, columnspan=2, padx=8, pady=(8,4), sticky="w")

        COLS = 4
        self._genre_buttons = {}
        for i, g in enumerate(self._all_genres):
            active = g in self._genre_selected
            b = ctk.CTkButton(inner, text=g, width=110, height=28,
                               fg_color=ACCENT if active else "#333",
                               text_color=TEXT_WHITE if active else TEXT_GRAY,
                               hover_color="#7A1C1C" if active else "#3E3E3E",
                               corner_radius=13, font=("Trebuchet MS",10,"bold"),
                               border_width=1, border_color=ACCENT if active else "#555",
                               command=lambda genre=g: self._toggle_genre(genre))
            b.grid(row=i//COLS+1, column=i%COLS, padx=5, pady=4, sticky="ew")
            self._genre_buttons[g] = b
        for c in range(COLS):
            inner.columnconfigure(c, weight=1)

        popup.bind("<FocusOut>", lambda e: self.after(100, self._check_focus))
        popup.focus_set()

    def _check_focus(self):
        if self._genre_popup and self._genre_dropdown_open:
            try:
                if self._genre_popup.focus_get() is None:
                    self._close_genre_dropdown()
            except: self._close_genre_dropdown()

    def _close_genre_dropdown(self):
        self._genre_dropdown_open = False
        self._genre_btn_main.configure(
            text="Genre ▼",
            fg_color=ACCENT if self._genre_selected else "#2E2E2E")
        if self._genre_popup:
            try: self._genre_popup.destroy()
            except: pass
            self._genre_popup = None

    # ── BUILD UI ─────────────────────────────────────────────────────────────
    def _build_ui(self):
        self._build_nav()

        ctk.CTkLabel(self, text="Find your movie!",
                     font=("Georgia",38,"bold"), text_color=TEXT_WHITE
                     ).pack(pady=(20,8))

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=40, pady=(0,10))

        self._genre_btn_main = ctk.CTkButton(
            row, text="Genre ▼", width=100, height=32,
            fg_color="#2E2E2E", text_color=TEXT_WHITE,
            hover_color="#3E3E3E", corner_radius=16,
            font=("Trebuchet MS",11,"bold"),
            command=self._toggle_genre_dropdown)
        self._genre_btn_main.pack(side="left", padx=(0,8))

        self._genre_label = ctk.CTkLabel(row, text="All genres",
                                          font=("Trebuchet MS",11), text_color=TEXT_GRAY)
        self._genre_label.pack(side="left", padx=(0,16))

        ctk.CTkFrame(row, fg_color="#444", width=1, height=24).pack(side="left", padx=(0,12))
        ctk.CTkLabel(row, text="Sort :", font=("Trebuchet MS",12,"bold"),
                     text_color=TEXT_GRAY).pack(side="left", padx=(0,6))

        for label, key in [("Default","default"),("A–Z","title"),("Newest","year_desc"),
                            ("Oldest","year_asc"),("Rating ↓","rating_desc"),("Rating ↑","rating_asc")]:
            b = ctk.CTkButton(row, text=label, width=78, height=28,
                               fg_color=ACCENT if key==self.sort_key else "#2E2E2E",
                               text_color=TEXT_WHITE if key==self.sort_key else TEXT_GRAY,
                               hover_color="#7A1C1C" if key==self.sort_key else "#3E3E3E",
                               corner_radius=14, font=("Trebuchet MS",11,"bold"),
                               command=lambda k=key: self._set_sort(k))
            b.pack(side="left", padx=3)
            self._sort_buttons[key] = b

        self._count_label = ctk.CTkLabel(row, text="", font=("Trebuchet MS",11), text_color=TEXT_GRAY)
        self._count_label.pack(side="right", padx=8)

        self.table_container = ctk.CTkFrame(self, fg_color="#1A1A1A", corner_radius=15)
        self.table_container.pack(fill="both", expand=True, padx=40, pady=(0,20))
        self._setup_canvas()

        self.pagination_frame = ctk.CTkFrame(self.table_container, fg_color="transparent")
        self.pagination_frame.pack(fill="x", pady=15)

        self.render_table()

    def _setup_canvas(self):
        wrap = ctk.CTkFrame(self.table_container, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=20, pady=(10,0))

        self._canvas = tk.Canvas(wrap, bg="#1A1A1A", highlightthickness=0)
        self._canvas.pack(fill="both", expand=True)

        self._scrollbar = tk.Scrollbar(wrap, orient="vertical", width=0,
                                        command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=self._scrollbar.set)

        self.rows_frame = ctk.CTkFrame(self._canvas, fg_color="transparent", corner_radius=0)
        self._win = self._canvas.create_window((0,0), window=self.rows_frame, anchor="nw")

        self.rows_frame.bind("<Configure>",
                              lambda e: self._canvas.configure(
                                  scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>",
                           lambda e: self._canvas.itemconfig(self._win, width=e.width))

        # Scroll binding sama persis seperti aslinya
        self._canvas.bind("<Enter>", lambda e: self._canvas.bind_all("<MouseWheel>", self._scroll))
        self._canvas.bind("<Leave>", lambda e: self._canvas.unbind_all("<MouseWheel>"))

    def _scroll(self, e):
        # Scroll 1 unit per notch (lambat tapi tetap jalan)
        # Throttle 30ms agar tidak terlalu cepat saat scroll ngebut
        if getattr(self, "_scroll_job", None):
            return
        direction = -1 if e.delta > 0 else 1
        self._canvas.yview_scroll(direction, "units")
        self._scroll_job = self.after(30, self._clear_scroll_job)

    def _clear_scroll_job(self):
        self._scroll_job = None

    def destroy(self):
        try: self._canvas.unbind_all("<MouseWheel>")
        except: pass
        super().destroy()

    # ── RENDER ───────────────────────────────────────────────────────────────
    def render_table(self):
        # FIX tiling: naikkan counter generasi setiap render baru
        self._render_gen += 1

        for w in self.rows_frame.winfo_children(): w.destroy()
        for w in self.pagination_frame.winfo_children(): w.destroy()
        self._canvas.yview_moveto(0)

        COLS = 5
        start = self.current_page * self.items_per_page
        end   = start + self.items_per_page
        page_movies = self.filtered_list[start:end]
        total       = len(self.filtered_list)
        total_pages = max(1, (total + self.items_per_page - 1) // self.items_per_page)

        self._count_label.configure(text=f"{total} films")

        if not page_movies:
            ctk.CTkLabel(self.rows_frame, text="No movies found. 😔",
                          font=("Trebuchet MS",14), text_color="#888").pack(pady=60)
            self._render_pagination(total_pages, end)
            return

        grid = ctk.CTkFrame(self.rows_frame, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=6, pady=6)
        for c in range(COLS):
            grid.columnconfigure(c, weight=1)

        for idx, movie in enumerate(page_movies):
            self._make_card(grid, movie, idx // COLS, idx % COLS)

        self._render_pagination(total_pages, end)

    def _make_card(self, grid, movie, row_i, col_i):
        def go(e, m=movie): self.app.show_page("moviedetail", data=m)

        card = ctk.CTkFrame(grid, fg_color=BG_CARD, corner_radius=10,
                             cursor="hand2", border_width=1, border_color="#444")
        card.grid(row=row_i, column=col_i, padx=6, pady=6, sticky="n")

        poster_lbl = ctk.CTkLabel(card, text="🎬", fg_color="#1A1A1A",
                                   width=POSTER_W, height=POSTER_H, corner_radius=8)
        poster_lbl.pack(padx=8, pady=(8,0))

        path = movie.get("poster_local", "")
        if path and os.path.exists(path):
            # FIX tiling: kirim generasi saat ini
            self._load_poster_async(poster_lbl, path, self._render_gen)

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(fill="x", padx=8, pady=(6,8))

        title_lbl = ctk.CTkLabel(info, text=movie.get("title","Unknown"),
                                  font=("Trebuchet MS",12,"bold"), text_color=TEXT_WHITE,
                                  anchor="w", wraplength=POSTER_W, justify="left")
        title_lbl.pack(fill="x")

        sub_lbl = ctk.CTkLabel(info,
                                text=f"{movie.get('year','N/A')}  •  {movie.get('genre','N/A')}",
                                font=("Trebuchet MS",10), text_color=TEXT_GRAY,
                                anchor="w", wraplength=POSTER_W, justify="left")
        sub_lbl.pack(fill="x")

        rat_row = ctk.CTkFrame(info, fg_color="transparent")
        rat_row.pack(fill="x", pady=(2,0))
        ctk.CTkLabel(rat_row, text=f"⭐ {movie.get('rating','N/A')}",
                     font=("Trebuchet MS",11,"bold"), text_color=ACCENT, anchor="w").pack(side="left")
        ctk.CTkLabel(rat_row, text="IMDb",
                     font=("Trebuchet MS",9), text_color=TEXT_GRAY, anchor="w").pack(side="left", padx=(4,0))

        def _enter(e, c=card): c.configure(fg_color=BG_CARD_HOVER, border_color=ACCENT, border_width=2)
        def _leave(e, c=card): c.configure(fg_color=BG_CARD, border_color="#444", border_width=1)
        for w in card.winfo_children() + [card]:
            w.bind("<Enter>", _enter)
            w.bind("<Leave>", _leave)
            w.bind("<Button-1>", go)
        for w in info.winfo_children() + [info, rat_row]:
            w.bind("<Enter>", _enter)
            w.bind("<Leave>", _leave)
            w.bind("<Button-1>", go)

    def _load_poster_async(self, label, path, gen):
        # Cache hit → langsung tampil tanpa thread
        if path in self._poster_cache:
            img = self._poster_cache[path]
            try: label.configure(image=img, text="")
            except: pass
            return

        def load():
            try:
                img = ctk.CTkImage(Image.open(path), size=(POSTER_W, POSTER_H))
                self._poster_cache[path] = img

                def update():
                    # FIX tiling: hanya update kalau generasi masih cocok
                    if self._render_gen != gen:
                        return
                    try: label.configure(image=img, text="")
                    except: pass

                self.after(0, update)
            except: pass

        threading.Thread(target=load, daemon=True).start()

    # ── PAGINATION ───────────────────────────────────────────────────────────
    def _render_pagination(self, total_pages, end):
        ctk.CTkButton(self.pagination_frame, text="◀ Prev", width=100, fg_color=ACCENT,
                       command=self.prev_page,
                       state="normal" if self.current_page > 0 else "disabled"
                       ).pack(side="left", padx=40)
        ctk.CTkLabel(self.pagination_frame,
                     text=f"Page {self.current_page+1} of {total_pages}",
                     text_color=TEXT_WHITE).pack(side="left", expand=True)
        ctk.CTkButton(self.pagination_frame, text="Next ▶", width=100, fg_color=ACCENT,
                       command=self.next_page,
                       state="normal" if end < len(self.filtered_list) else "disabled"
                       ).pack(side="right", padx=40)

    def prev_page(self):
        self.current_page -= 1
        self.render_table()

    def next_page(self):
        self.current_page += 1
        self.render_table()
