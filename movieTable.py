import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import threading
import json
import shutil
from PIL import Image
from styles import *

BG_MAIN       = "#1A1A1A"
TEXT_WHITE     = "#FFFFFF"
TEXT_GRAY      = "#AAAAAA"
ACCENT         = "#E53935"
BG_CARD        = "#2E2E2E"
BG_CARD_HOVER  = "#3D3D3D"
POSTER_W, POSTER_H = 160, 220

DATA_FILE = "data_film.json"


# ─────────────────────────────────────────────────────────────────────────────
#  HELPER DB
# ─────────────────────────────────────────────────────────────────────────────
def _read_db():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def _write_db(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# ─────────────────────────────────────────────────────────────────────────────
#  POPUP: Add / Edit Movie
# ─────────────────────────────────────────────────────────────────────────────
class MovieFormPopup(ctk.CTkToplevel):
    FIELDS = [
        ("Title *",    "title",    False),
        ("Year *",     "year",     False),
        ("Genre",      "genre",    False),
        ("Rating",     "rating",   False),
        ("Director",   "director", False),
        ("Actors",     "actors",   False),
        ("Duration",   "runtime",  False),
        ("Language",   "language", False),
        ("Country",    "country",  False),
        ("Synopsis",   "synopsis", True),
    ]

    def __init__(self, master, app, movie_data=None, on_save=None):
        super().__init__(master)
        self.app        = app
        self.movie_data = movie_data or {}
        self.on_save    = on_save
        self._poster_path = self.movie_data.get("poster_local", "")

        self.title("Edit Movie" if movie_data else "Add New Movie")
        self.geometry("520x680")
        self.configure(fg_color="#1A1A1A")
        self.resizable(False, False)

        self.update_idletasks()
        x = app.winfo_x() + (app.winfo_width()  // 2) - 260
        y = app.winfo_y() + (app.winfo_height() // 2) - 340
        self.geometry(f"+{x}+{y}")
        self.attributes("-topmost", True)
        self.grab_set()
        self._build()

    def _build(self):
        header = "✏️  Edit Movie" if self.movie_data else "➕  Add New Movie"
        ctk.CTkLabel(self, text=header, font=("Georgia", 22, "bold"),
                     text_color=TEXT_WHITE).pack(pady=(22, 2))
        ctk.CTkLabel(self, text="Fields marked * are required.",
                     font=("Trebuchet MS", 11), text_color=TEXT_GRAY).pack(pady=(0, 8))

        body = ctk.CTkScrollableFrame(self, fg_color="#1A1A1A",
                                       scrollbar_button_color="#444",
                                       scrollbar_button_hover_color=ACCENT)
        body.pack(fill="both", expand=True, padx=24, pady=(0, 8))

        self._vars  = {}
        self._texts = {}

        for label, key, multiline in self.FIELDS:
            ctk.CTkLabel(body, text=label, font=("Trebuchet MS", 11, "bold"),
                         text_color=TEXT_GRAY, anchor="w").pack(fill="x", pady=(8, 1))
            if multiline:
                tb = ctk.CTkTextbox(body, height=88, fg_color="#222", border_color="#444",
                                    border_width=1, text_color=TEXT_WHITE, corner_radius=8,
                                    font=("Trebuchet MS", 12))
                tb.pack(fill="x")
                val = self.movie_data.get(key, "")
                if val:
                    tb.insert("0.0", val)
                self._texts[key] = tb
            else:
                var = ctk.StringVar(value=str(self.movie_data.get(key, "")))
                ctk.CTkEntry(body, textvariable=var, height=38,
                              fg_color="#222", border_color="#444", border_width=1,
                              text_color=TEXT_WHITE, corner_radius=8,
                              font=("Trebuchet MS", 12)).pack(fill="x")
                self._vars[key] = var

        # Poster picker
        ctk.CTkLabel(body, text="Poster Image", font=("Trebuchet MS", 11, "bold"),
                     text_color=TEXT_GRAY, anchor="w").pack(fill="x", pady=(10, 1))

        pr = ctk.CTkFrame(body, fg_color="transparent")
        pr.pack(fill="x")
        self._poster_lbl = ctk.CTkLabel(pr, text="No file selected",
                                         font=("Trebuchet MS", 11), text_color=TEXT_GRAY, anchor="w")
        self._poster_lbl.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(pr, text="📁 Browse", width=90, height=32,
                       fg_color="#333", hover_color="#444", corner_radius=8,
                       font=("Trebuchet MS", 11, "bold"), text_color=TEXT_WHITE,
                       command=self._pick_poster).pack(side="right")

        if self._poster_path:
            self._poster_lbl.configure(
                text=os.path.basename(self._poster_path)[:40], text_color=TEXT_WHITE)

        self._thumb_lbl = ctk.CTkLabel(body, text="", fg_color="transparent")
        self._thumb_lbl.pack(pady=(6, 0))
        if self._poster_path and os.path.exists(self._poster_path):
            self._show_thumb(self._poster_path)

        # Tombol aksi
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=24, pady=(4, 18))
        ctk.CTkButton(btn_row, text="Cancel", width=110, height=40,
                       fg_color="#333", hover_color="#444", corner_radius=10,
                       font=("Trebuchet MS", 12, "bold"), text_color=TEXT_WHITE,
                       command=self.destroy).pack(side="left")
        ctk.CTkButton(btn_row, text="💾  Save", width=160, height=40,
                       fg_color=ACCENT, hover_color="#c0392b", corner_radius=10,
                       font=("Trebuchet MS", 12, "bold"), text_color=TEXT_WHITE,
                       command=self._save).pack(side="right")

    def _pick_poster(self):
        path = filedialog.askopenfilename(
            title="Select Poster Image",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.webp")])
        if not path:
            return
        self._poster_path = path
        self._poster_lbl.configure(text=os.path.basename(path)[:40], text_color=TEXT_WHITE)
        self._show_thumb(path)

    def _show_thumb(self, path):
        try:
            img = ctk.CTkImage(Image.open(path), size=(80, 112))
            self._thumb_lbl.configure(image=img, text="")
            self._thumb_lbl._ctk_image = img
        except Exception:
            pass

    def _save(self):
        result = dict(self.movie_data)
        for key, var in self._vars.items():
            result[key] = var.get().strip()
        for key, tb in self._texts.items():
            result[key] = tb.get("0.0", "end").strip()

        if not result.get("title"):
            messagebox.showwarning("Required", "Title is required.", parent=self)
            return
        if not result.get("year"):
            messagebox.showwarning("Required", "Year is required.", parent=self)
            return

        new_poster = self._poster_path
        old_poster = self.movie_data.get("poster_local", "")
        if new_poster and new_poster != old_poster and os.path.exists(new_poster):
            os.makedirs("posters", exist_ok=True)
            safe = result["title"].replace(" ", "_").replace("/", "-")[:60]
            ext  = os.path.splitext(new_poster)[1].lower() or ".jpg"
            dest = os.path.join("posters", safe + ext)
            try:
                shutil.copy2(new_poster, dest)
                result["poster_local"] = dest
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy poster:\n{e}", parent=self)
                return
        elif new_poster:
            result["poster_local"] = new_poster

        self.destroy()
        if self.on_save:
            self.on_save(result)


# ─────────────────────────────────────────────────────────────────────────────
#  POPUP: Admin Action Menu
# ─────────────────────────────────────────────────────────────────────────────
class AdminActionPopup(ctk.CTkToplevel):
    """Popup yang muncul saat admin klik tombol 'Admin Mode'.
    Berisi pilihan: Tambah Film, Hapus Film, atau Cancel."""

    def __init__(self, master, app, on_add, on_delete):
        super().__init__(master)
        self.app       = app
        self.on_add    = on_add
        self.on_delete = on_delete

        self.title("Admin Panel")
        self.geometry("380x280")
        self.configure(fg_color="#1A1A1A")
        self.resizable(False, False)

        self.update_idletasks()
        x = app.winfo_x() + (app.winfo_width()  // 2) - 190
        y = app.winfo_y() + (app.winfo_height() // 2) - 140
        self.geometry(f"+{x}+{y}")
        self.attributes("-topmost", True)
        self.grab_set()
        self._build()

    def _build(self):
        # Header
        ctk.CTkLabel(self, text="🔓 Admin Panel",
                     font=("Arial Black", 20, "bold"),
                     text_color=TEXT_WHITE).pack(pady=(28, 4))
        ctk.CTkLabel(self, text="Pilih aksi yang ingin dilakukan:",
                     font=("Trebuchet MS", 12), text_color=TEXT_GRAY).pack(pady=(0, 20))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=36)

        # Tombol Tambah Film
        ctk.CTkButton(
            btn_frame,
            text="➕  Tambah Film Baru",
            height=48, corner_radius=10,
            fg_color=ACCENT, hover_color="#c0392b",
            font=("Trebuchet MS", 13, "bold"), text_color=TEXT_WHITE,
            command=self._do_add
        ).pack(fill="x", pady=(0, 10))

        # Tombol Hapus Film
        ctk.CTkButton(
            btn_frame,
            text="🗑  Hapus Film",
            height=48, corner_radius=10,
            fg_color="#AA2222", hover_color="#CC3333",
            font=("Trebuchet MS", 13, "bold"), text_color=TEXT_WHITE,
            command=self._do_delete
        ).pack(fill="x", pady=(0, 10))

        # Tombol Cancel
        ctk.CTkButton(
            btn_frame,
            text="Batal",
            height=36, corner_radius=10,
            fg_color="#333", hover_color="#444",
            font=("Trebuchet MS", 12), text_color=TEXT_GRAY,
            command=self.destroy
        ).pack(fill="x")

    def _do_add(self):
        self.destroy()
        self.on_add()

    def _do_delete(self):
        self.destroy()
        self.on_delete()


# ─────────────────────────────────────────────────────────────────────────────
#  POPUP: Pilih Film untuk Dihapus
# ─────────────────────────────────────────────────────────────────────────────
class DeleteMoviePopup(ctk.CTkToplevel):
    """Popup daftar film dengan search, user pilih film mana yang dihapus."""

    def __init__(self, master, app, movie_list, on_delete):
        super().__init__(master)
        self.app        = app
        self.movie_list = movie_list
        self.on_delete  = on_delete
        self._filtered  = movie_list.copy()

        self.title("Hapus Film")
        self.geometry("500x580")
        self.configure(fg_color="#1A1A1A")
        self.resizable(False, True)

        self.update_idletasks()
        x = app.winfo_x() + (app.winfo_width()  // 2) - 250
        y = app.winfo_y() + (app.winfo_height() // 2) - 290
        self.geometry(f"+{x}+{y}")
        self.attributes("-topmost", True)
        self.grab_set()
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="🗑  Pilih Film yang Ingin Dihapus",
                     font=("Arial Black", 16, "bold"),
                     text_color=TEXT_WHITE).pack(pady=(22, 8))

        # Search bar
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", padx=24, pady=(0, 10))
        self._search_var = ctk.StringVar()
        self._search_var.trace_add("write", self._on_search)
        ctk.CTkEntry(search_frame, textvariable=self._search_var,
                     placeholder_text="Cari judul film...",
                     height=36, fg_color="#222", border_color="#444",
                     text_color=TEXT_WHITE, corner_radius=8,
                     font=("Trebuchet MS", 12)).pack(fill="x")

        # List film
        self._list_frame = ctk.CTkScrollableFrame(self, fg_color="#111",
                                                   corner_radius=10,
                                                   scrollbar_button_color="#333")
        self._list_frame.pack(fill="both", expand=True, padx=24, pady=(0, 12))
        self._render_list()

        ctk.CTkButton(self, text="Batal", height=36, corner_radius=10,
                      fg_color="#333", hover_color="#444",
                      font=("Trebuchet MS", 12), text_color=TEXT_GRAY,
                      command=self.destroy).pack(fill="x", padx=24, pady=(0, 18))

    def _on_search(self, *_):
        q = self._search_var.get().lower().strip()
        self._filtered = [m for m in self.movie_list
                          if q in m.get("title", "").lower()] if q else self.movie_list.copy()
        self._render_list()

    def _render_list(self):
        for w in self._list_frame.winfo_children():
            w.destroy()

        if not self._filtered:
            ctk.CTkLabel(self._list_frame, text="Film tidak ditemukan.",
                         text_color=TEXT_GRAY, font=("Trebuchet MS", 12)).pack(pady=20)
            return

        # Render bertahap agar UI tidak freeze
        self._render_batch(self._filtered, 0)

    def _render_batch(self, movies, start, batch=30):
        end = min(start + batch, len(movies))
        for movie in movies[start:end]:
            row = ctk.CTkFrame(self._list_frame, fg_color="#222", corner_radius=8)
            row.pack(fill="x", pady=3, padx=4)

            # Judul bisa wrap jadi 2 baris kalau terlalu panjang
            ctk.CTkLabel(row,
                         text=f"{movie.get('title', 'Unknown')}  ({movie.get('year', '?')})",
                         font=("Trebuchet MS", 12, "bold"), text_color=TEXT_WHITE,
                         anchor="w", wraplength=310, justify="left"
                         ).pack(side="left", padx=12, pady=10, fill="x", expand=True)

            # Tombol fixed width supaya tidak terpotong
            ctk.CTkButton(row, text="🗑 Hapus", width=90, height=32,
                          fg_color="#AA2222", hover_color="#CC3333",
                          corner_radius=8, font=("Trebuchet MS", 11, "bold"),
                          text_color=TEXT_WHITE,
                          command=lambda m=movie: self._confirm(m)
                          ).pack(side="right", padx=10, pady=10)

        if end < len(movies):
            # Render sisa di idle berikutnya agar UI tetap responsif
            self.after(0, lambda: self._render_batch(movies, end, batch))

    def _confirm(self, movie):
        title = movie.get("title", "film ini")
        if messagebox.askyesno(
            "Konfirmasi Hapus",
            f"Hapus '{title}' secara permanen?\nAksi ini tidak bisa dibatalkan.",
            icon="warning", parent=self
        ):
            self.destroy()
            self.on_delete(movie)


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN PAGE
# ─────────────────────────────────────────────────────────────────────────────
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
        self._render_gen   = 0

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

        pages = [
            ("Home",         "dashboard",    False),
            ("Genre Analyze","genreanalyze", False),
            ("Movie Table",  None,           True),
            ("Watchlist",    "watchlist",    False),
        ]
        widths = {"Genre Analyze": 110, "Movie Table": 92, "Watchlist": 80, "Home": 70}
        for i, (text, page, active) in enumerate(pages):
            px_l = 6 if i == 0 else 2
            px_r = 6 if i == len(pages) - 1 else 2
            ctk.CTkButton(
                pill, text=text,
                width=widths.get(text, 80), height=28, corner_radius=16,
                font=("Trebuchet MS", 11, "bold"),
                fg_color=ACCENT if active else "transparent",
                text_color=TEXT_WHITE if active else TEXT_GRAY,
                hover_color="#c0392b" if active else "#3A3A3A",
                command=(lambda p=page: self.app.show_page(p)) if page else None,
            ).pack(side="left", padx=(px_l, px_r), pady=3)

        # ── TOMBOL ADMIN MODE DI NAVBAR ──
        self._admin_nav_btn = ctk.CTkButton(
            nav,
            text="🔓 Admin Mode" if getattr(self.app, "is_admin", False) else "🔒 Admin Mode",
            width=130, height=30, corner_radius=15,
            fg_color="#AA2222" if getattr(self.app, "is_admin", False) else "#333",
            hover_color="#CC3333" if getattr(self.app, "is_admin", False) else "#444",
            font=("Trebuchet MS", 10, "bold"), text_color=TEXT_WHITE,
            command=self._on_admin_btn_click
        )
        self._admin_nav_btn.pack(side="left", padx=(16, 0), pady=14)

    def _on_admin_btn_click(self):
        if getattr(self.app, "is_admin", False):
            AdminActionPopup(
                self, self.app,
                on_add=self._open_add_movie,
                on_delete=self._open_delete_picker
            )
        else:
            messagebox.showwarning(
                "Akses Ditolak",
                "⛔ Fitur ini hanya untuk Admin.\n\n"
                "Kamu bisa mendaftar sebagai Admin\nmelalui halaman Profile."
            )

    # ── SORT / FILTER ────────────────────────────────────────────────────────
    def _apply_sort(self, data):
        k = self.sort_key
        if k == "title":       return sorted(data, key=lambda m: m.get("title", "").lower())
        if k == "year_desc":   return sorted(data, key=lambda m: m.get("year", "0"), reverse=True)
        if k == "year_asc":    return sorted(data, key=lambda m: m.get("year", "0"))
        if k == "rating_desc": return sorted(data, key=lambda m: float(m.get("rating", 0) or 0), reverse=True)
        if k == "rating_asc":  return sorted(data, key=lambda m: float(m.get("rating", 0) or 0))
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
                fg = {g.strip() for g in str(m.get("genre", "")).split(",")}
                if self._genre_selected.issubset(fg):
                    result.append(m)
        else:
            result = data.copy()

        q = self.search_entry.get().lower().strip()
        if q:
            result = [m for m in result
                      if q in str(m.get("title", "")).lower()
                      or q in str(m.get("genre", "")).lower()]

        self.filtered_list = self._apply_sort(result)
        self.render_table()

    def _set_sort(self, key):
        self.sort_key = key
        self.current_page = 0
        self.filtered_list = self._apply_sort(self.filtered_list)
        for k, b in self._sort_buttons.items():
            b.configure(fg_color=ACCENT if k == key else "#2E2E2E",
                        text_color=TEXT_WHITE if k == key else TEXT_GRAY)
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
            self._genre_label.configure(
                text=txt[:40] + "..." if len(txt) > 40 else txt,
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
                       font=("Trebuchet MS", 10, "bold"),
                       command=self._clear_genres
                       ).grid(row=0, column=0, columnspan=2, padx=8, pady=(8, 4), sticky="w")

        COLS = 4
        self._genre_buttons = {}
        for i, g in enumerate(self._all_genres):
            active = g in self._genre_selected
            b = ctk.CTkButton(inner, text=g, width=110, height=28,
                               fg_color=ACCENT if active else "#333",
                               text_color=TEXT_WHITE if active else TEXT_GRAY,
                               hover_color="#c0392b" if active else "#3E3E3E",
                               corner_radius=13, font=("Trebuchet MS", 10, "bold"),
                               border_width=1, border_color=ACCENT if active else "#555",
                               command=lambda genre=g: self._toggle_genre(genre))
            b.grid(row=i // COLS + 1, column=i % COLS, padx=5, pady=4, sticky="ew")
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

        ctk.CTkLabel(
            self, text="Find your movie!",
            font=("Georgia", 38, "bold"), text_color=TEXT_WHITE,
            anchor="center", justify="center",
        ).pack(pady=(20, 8), fill="x")

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=40, pady=(0, 10))

        self._genre_btn_main = ctk.CTkButton(
            row, text="Genre ▼", width=100, height=32,
            fg_color="#2E2E2E", text_color=TEXT_WHITE,
            hover_color="#3E3E3E", corner_radius=16,
            font=("Trebuchet MS", 11, "bold"),
            command=self._toggle_genre_dropdown)
        self._genre_btn_main.pack(side="left", padx=(0, 8))

        self._genre_label = ctk.CTkLabel(row, text="All genres",
                                          font=("Trebuchet MS", 11), text_color=TEXT_GRAY)
        self._genre_label.pack(side="left", padx=(0, 16))

        ctk.CTkFrame(row, fg_color="#444", width=1, height=24).pack(side="left", padx=(0, 12))
        ctk.CTkLabel(row, text="Sort :", font=("Trebuchet MS", 12, "bold"),
                     text_color=TEXT_GRAY).pack(side="left", padx=(0, 6))

        for label, key in [("Default", "default"), ("A–Z", "title"), ("Newest", "year_desc"),
                            ("Oldest", "year_asc"), ("Rating ↓", "rating_desc"), ("Rating ↑", "rating_asc")]:
            b = ctk.CTkButton(row, text=label, width=78, height=28,
                               fg_color=ACCENT if key == self.sort_key else "#2E2E2E",
                               text_color=TEXT_WHITE if key == self.sort_key else TEXT_GRAY,
                               hover_color="#c0392b" if key == self.sort_key else "#3E3E3E",
                               corner_radius=14, font=("Trebuchet MS", 11, "bold"),
                               command=lambda k=key: self._set_sort(k))
            b.pack(side="left", padx=3)
            self._sort_buttons[key] = b

        self._count_label = ctk.CTkLabel(row, text="", font=("Trebuchet MS", 11), text_color=TEXT_GRAY)
        self._count_label.pack(side="right", padx=8)

        self.table_container = ctk.CTkFrame(self, fg_color="#1A1A1A", corner_radius=15)
        self.table_container.pack(fill="both", expand=True, padx=40, pady=(0, 20))
        self._setup_canvas()

        self.pagination_frame = ctk.CTkFrame(self.table_container, fg_color="transparent")
        self.pagination_frame.pack(fill="x", pady=15)

        self.render_table()

    # ── SETUP CANVAS ─────────────────────────────────────────────────────────
    def _setup_canvas(self):
        wrap = ctk.CTkFrame(self.table_container, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=20, pady=(10, 0))

        self._canvas = tk.Canvas(wrap, bg="#1A1A1A", highlightthickness=0)
        self._canvas.pack(fill="both", expand=True)

        self._scrollbar = tk.Scrollbar(wrap, orient="vertical", width=0,
                                        command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=self._scrollbar.set)

        self.rows_frame = ctk.CTkFrame(self._canvas, fg_color="transparent", corner_radius=0)
        self._win = self._canvas.create_window((0, 0), window=self.rows_frame, anchor="nw")

        self.rows_frame.bind("<Configure>",
                              lambda e: self._canvas.configure(
                                  scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>",
                           lambda e: self._canvas.itemconfig(self._win, width=e.width))

        self._canvas.bind("<Enter>", self._bind_scroll)
        self._canvas.bind("<Leave>", self._unbind_scroll)

    def _bind_scroll(self, e=None):
        self._canvas.bind_all("<MouseWheel>", self._scroll)
        self._canvas.bind_all("<Button-4>",   self._scroll_up)
        self._canvas.bind_all("<Button-5>",   self._scroll_down)

    def _unbind_scroll(self, e=None):
        self._canvas.unbind_all("<MouseWheel>")
        self._canvas.unbind_all("<Button-4>")
        self._canvas.unbind_all("<Button-5>")

    def _scroll(self, e):
        if e.delta == 0:
            return
        direction = -1 if e.delta > 0 else 1
        self._canvas.yview_scroll(direction, "units")

    def _scroll_up(self, e):
        self._canvas.yview_scroll(-1, "units")

    def _scroll_down(self, e):
        self._canvas.yview_scroll(1, "units")

    def destroy(self):
        try:
            self._canvas.unbind_all("<MouseWheel>")
            self._canvas.unbind_all("<Button-4>")
            self._canvas.unbind_all("<Button-5>")
        except: pass
        super().destroy()

    # ── RENDER ───────────────────────────────────────────────────────────────
    def render_table(self):
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
                          font=("Trebuchet MS", 14), text_color="#888").pack(pady=60)
            self._render_pagination(total_pages, end)
            return

        grid = ctk.CTkFrame(self.rows_frame, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=6, pady=6)
        for c in range(COLS):
            grid.columnconfigure(c, weight=1)

        for idx, movie in enumerate(page_movies):
            self._make_card(grid, movie, idx // COLS, idx % COLS)

        self._render_pagination(total_pages, end)

    # ── CARD ─────────────────────────────────────────────────────────────────
    def _make_card(self, grid, movie, row_i, col_i):
        def go(e, m=movie): self.app.show_page("moviedetail", data=m)

        card = ctk.CTkFrame(grid, fg_color=BG_CARD, corner_radius=10,
                             cursor="hand2", border_width=1, border_color="#444")
        card.grid(row=row_i, column=col_i, padx=6, pady=6, sticky="n")

        poster_wrap = ctk.CTkFrame(card, fg_color="transparent",
                                    width=POSTER_W, height=POSTER_H)
        poster_wrap.pack(padx=8, pady=(8, 0))
        poster_wrap.pack_propagate(False)

        poster_lbl = ctk.CTkLabel(poster_wrap, text="🎬", fg_color="#1A1A1A",
                                   width=POSTER_W, height=POSTER_H, corner_radius=8)
        poster_lbl.place(x=0, y=0, relwidth=1, relheight=1)

        path = movie.get("poster_local", "")
        if path and os.path.exists(path):
            self._load_poster_async(poster_lbl, path, self._render_gen)

        # Info di bawah poster
        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(fill="x", padx=8, pady=(6, 8))

        ctk.CTkLabel(info, text=movie.get("title", "Unknown"),
                     font=("Trebuchet MS", 12, "bold"), text_color=TEXT_WHITE,
                     anchor="w", wraplength=POSTER_W, justify="left").pack(fill="x")

        ctk.CTkLabel(info,
                     text=f"{movie.get('year', 'N/A')}  •  {movie.get('genre', 'N/A')}",
                     font=("Trebuchet MS", 10), text_color=TEXT_GRAY,
                     anchor="w", wraplength=POSTER_W, justify="left").pack(fill="x")

        rat_row = ctk.CTkFrame(info, fg_color="transparent")
        rat_row.pack(fill="x", pady=(2, 0))
        ctk.CTkLabel(rat_row, text=f"⭐ {movie.get('rating', 'N/A')}",
                     font=("Trebuchet MS", 11, "bold"), text_color=ACCENT,
                     anchor="w").pack(side="left")
        ctk.CTkLabel(rat_row, text="IMDb",
                     font=("Trebuchet MS", 9), text_color=TEXT_GRAY,
                     anchor="w").pack(side="left", padx=(4, 0))

        # Hover + click
        def _all_widgets(parent):
            result = [parent]
            for child in parent.winfo_children():
                result.extend(_all_widgets(child))
            return result

        def _enter(e, c=card): c.configure(fg_color=BG_CARD_HOVER, border_color=ACCENT, border_width=2)
        def _leave(e, c=card): c.configure(fg_color=BG_CARD, border_color="#444", border_width=1)

        for w in _all_widgets(card):
            w.bind("<Enter>", _enter)
            w.bind("<Leave>", _leave)
            w.bind("<Button-1>", go)

    # ── ADMIN CRUD ────────────────────────────────────────────────────────────
    def _open_add_movie(self):
        MovieFormPopup(self, self.app, movie_data=None, on_save=self._do_add_movie)

    def _open_delete_picker(self):
        DeleteMoviePopup(self, self.app,
                         movie_list=self.all_movies,
                         on_delete=self._do_delete_movie)

    def _do_add_movie(self, new_data):
        db = _read_db()
        db.append(new_data)
        _write_db(db)
        self._reload_movie_list(db)
        messagebox.showinfo("Berhasil", f"'{new_data.get('title')}' berhasil ditambahkan!")

    def _do_delete_movie(self, movie):
        db = _read_db()
        db = [m for m in db if not (
            m.get("title") == movie.get("title") and
            m.get("year")  == movie.get("year")
        )]
        _write_db(db)
        self._reload_movie_list(db)
        messagebox.showinfo("Berhasil", f"'{movie.get('title')}' berhasil dihapus dari database.")

    def _reload_movie_list(self, db):
        self.app.movie_list = db
        self.all_movies     = db
        self.current_page   = 0
        self._do_filter()

    # ── POSTER ASYNC ─────────────────────────────────────────────────────────
    def _load_poster_async(self, label, path, gen):
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
                     text=f"Page {self.current_page + 1} of {total_pages}",
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