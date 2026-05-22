import customtkinter as ctk
import json
import os
from tkinter import messagebox
from datetime import datetime
from PIL import Image, ImageOps, ImageDraw
from tkcalendar import Calendar

BG_MAIN    = "#1A1A1A"
BG_NAV     = "#111111"
BG_TAB     = "#2E2E2E"
ACCENT     = "#5C1D24"
BG_CARD    = "#2A2A2A"
TEXT_WHITE = "#FFFFFF"
TEXT_GRAY  = "#AAAAAA"
ORANGE     = "#F5A623"
GREEN      = "#2d5a27"
GREEN_BTN  = "#2d5a27"
BLUE       = "#2A368F"
RED        = "#E53E3E"
STAR_ON    = "#F5A623"
STAR_OFF   = "#444444"


class StarRatingWidget(ctk.CTkFrame):
    """Reusable interactive star rating widget (1–10 stars)."""

    def __init__(self, master, initial=0, max_stars=10, size=22, command=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.max_stars = max_stars
        self.size      = size
        self.command   = command
        self._rating   = initial
        self._stars    = []
        self._build(initial)

    def _build(self, initial):
        for i in range(1, self.max_stars + 1):
            lbl = ctk.CTkLabel(
                self,
                text="★" if i <= initial else "☆",
                font=("Arial", self.size),
                text_color=STAR_ON if i <= initial else STAR_OFF,
            )
            lbl.pack(side="left", padx=1)
            lbl.bind("<Button-1>", lambda e, v=i: self._click(v))
            lbl.bind("<Enter>",    lambda e, v=i: self._hover(v))
            lbl.bind("<Leave>",    lambda e:       self._leave())
            try:
                lbl._label.bind("<Button-1>", lambda e, v=i: self._click(v))
                lbl._label.bind("<Enter>",    lambda e, v=i: self._hover(v))
                lbl._label.bind("<Leave>",    lambda e:       self._leave())
            except Exception:
                pass
            self._stars.append(lbl)

    def _hover(self, val):
        for i, lbl in enumerate(self._stars, 1):
            lbl.configure(text="★" if i <= val else "☆",
                          text_color=STAR_ON if i <= val else STAR_OFF)

    def _leave(self):
        for i, lbl in enumerate(self._stars, 1):
            lbl.configure(text="★" if i <= self._rating else "☆",
                          text_color=STAR_ON if i <= self._rating else STAR_OFF)

    def _click(self, val):
        self._rating = val
        self._leave()
        if self.command:
            self.command(val)

    def get(self):
        return self._rating

    def set(self, val):
        self._rating = val
        self._leave()


class WatchlistPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=BG_MAIN, corner_radius=0)
        self.app = app
        self.filter = "all"

        self.current_user = getattr(self.app, "username", "guest")
        if self.current_user == "guest":
            try:
                if os.path.exists("session.json"):
                    with open("session.json", "r") as f:
                        self.current_user = json.load(f).get("active_user", "guest")
            except:
                pass

        self.data_file = f"watchlist_{self.current_user}.json"
        self.watchlist_data = self._load_data()
        self._build_ui()
        self.bind("<Visibility>", lambda e: self._refresh())

    # ── DATA ──────────────────────────────────────────────────────────────────
    def _load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

    def _save_data(self):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.watchlist_data, f, indent=4)

    # ── BUILD UI ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        self._build_nav()

        self.body = ctk.CTkScrollableFrame(
            self, fg_color=BG_MAIN,
            scrollbar_button_color="#444",
            corner_radius=0
        )
        self.body.pack(fill="both", expand=True)

        self._build_form()
        self._build_stats_bar()

        self.movie_area = ctk.CTkFrame(self.body, fg_color="transparent")
        self.movie_area.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        self._refresh()

    # ── NAVBAR ────────────────────────────────────────────────────────────────
    def _build_nav(self):
        nav = ctk.CTkFrame(self, fg_color=BG_NAV, corner_radius=0, height=75)
        nav.pack(fill="x", side="top")
        nav.pack_propagate(False)

        ctk.CTkButton(
            nav, text="❮", width=80, height=34,
            fg_color="transparent", text_color=TEXT_GRAY,
            font=("Trebuchet MS", 20, "bold"),
            hover_color=BG_TAB,
            command=lambda: self.app.show_page("dashboard")
        ).pack(side="left", padx=20)

        self.nav_title_lbl = ctk.CTkLabel(
            nav, text="Watchlist",
            font=("Arial", 18, "bold"), text_color=TEXT_WHITE
        )
        self.nav_title_lbl.pack(side="left", padx=10)

        self._tab_btns = {}
        btn = ctk.CTkButton(
            nav, text="My Diary", width=120, height=38,
            fg_color=ACCENT,
            corner_radius=19,
            font=("Trebuchet MS", 12, "bold"),
            text_color=TEXT_WHITE,
            hover_color="#6C6C6C",
            command=lambda: self._set_filter("diary")   # ← HANYA INI YANG BERUBAH
        )
        btn.place(relx=0.99, rely=0.5, anchor="e", x=-20)
        self._tab_btns["diary"] = btn

    def _update_tab_highlight(self):
        pass

    # ── FORM TAMBAH FILM ─────────────────────────────────────────────────────
    def _build_form(self):
        form = ctk.CTkFrame(
            self.body, fg_color=BG_CARD,
            corner_radius=20, border_width=1, border_color="#333"
        )
        form.pack(fill="x", padx=30, pady=(25, 10))

        ctk.CTkLabel(
            form, text="Add to Watchlist",
            font=("Arial", 15, "bold"), text_color=TEXT_WHITE
        ).pack(anchor="w", padx=25, pady=(18, 0))

        row = ctk.CTkFrame(form, fg_color="transparent")
        row.pack(pady=(10, 18), padx=25)

        self.e_title = ctk.CTkEntry(
            row, placeholder_text="Movie title...",
            width=320, height=38,
            fg_color="#1E1E1E", border_color="#444",
            font=("Trebuchet MS", 13)
        )
        self.e_title.pack(side="left", padx=(0, 8))

        self.e_year = ctk.CTkEntry(
            row, placeholder_text="Year",
            width=90, height=38,
            fg_color="#1E1E1E", border_color="#444",
            font=("Trebuchet MS", 13)
        )
        self.e_year.pack(side="left", padx=(0, 8))

        self.status_var = ctk.StringVar(value="Plan to Watch")
        ctk.CTkOptionMenu(
            row, values=["Plan to Watch", "Watching", "Watched"],
            variable=self.status_var,
            width=150, height=38,
            fg_color="#1E1E1E", button_color="#444444",
            font=("Trebuchet MS", 12)
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            row, text="+ Add Movie",
            width=120, height=38,
            fg_color="#1E1E1E", hover_color="#2d5a27",
            font=("Trebuchet MS", 13, "bold"),
            corner_radius=10,
            command=self._add_movie
        ).pack(side="left")

    # ── STATS BAR ─────────────────────────────────────────────────────────────
    def _build_stats_bar(self):
        self.stats_frame = ctk.CTkFrame(self.body, fg_color="transparent")
        self.stats_frame.pack(fill="x", padx=30, pady=(5, 15))

    def _refresh_stats(self):
        for w in self.stats_frame.winfo_children():
            w.destroy()

        total    = len(self.watchlist_data)
        planning = sum(1 for m in self.watchlist_data if m.get("status") == "Plan to Watch")
        watching = sum(1 for m in self.watchlist_data if m.get("status") == "Watching")
        watched  = sum(1 for m in self.watchlist_data if m.get("status") == "Watched")

        stats = [
            ("Total",    str(total),    "#233D6D", "all"),
            ("Planning", str(planning), "#6D2323", "Plan to Watch"),
            ("Watching", str(watching), "#6D3F23", "Watching"),
            ("Watched",  str(watched),  "#3A4B38", "Watched"),
        ]
        for label, val, col, filt in stats:
            card = ctk.CTkFrame(
                self.stats_frame, fg_color=col,
                corner_radius=12, height=64,
                cursor="hand2"
            )
            card.pack(side="left", fill="x", expand=True, padx=6)
            card.pack_propagate(False)
            lbl_val = ctk.CTkLabel(
                card, text=val,
                font=("Arial Black", 20, "bold"),
                text_color=TEXT_WHITE
            )
            lbl_val.place(relx=0.5, rely=0.35, anchor="center")
            lbl_name = ctk.CTkLabel(
                card, text=label,
                font=("Trebuchet MS", 11),
                text_color="#DDD"
            )
            lbl_name.place(relx=0.5, rely=0.78, anchor="center")
            card.bind("<Button-1>", lambda e, f=filt: self._set_filter(f))
            lbl_val.bind("<Button-1>", lambda e, f=filt: self._set_filter(f))
            lbl_name.bind("<Button-1>", lambda e, f=filt: self._set_filter(f))

    # ── REFRESH ───────────────────────────────────────────────────────────────
    def _refresh(self):
        self.current_user = getattr(self.app, "username", "guest")
        if self.current_user == "guest" and os.path.exists("session.json"):
            try:
                with open("session.json", "r") as f:
                    self.current_user = json.load(f).get("active_user", "guest")
            except:
                pass

        self.data_file = f"watchlist_{self.current_user}.json"
        self.watchlist_data = self._load_data()

        if hasattr(self, "nav_title_lbl"):
            self.nav_title_lbl.configure(text=f"Watchlist")

        self._refresh_stats()

        for w in self.movie_area.winfo_children():
            w.destroy()

        if self.filter == "diary":                          # ← HANYA INI YANG BERUBAH
            data = [m for m in self.watchlist_data if m.get("status") == "Watched"]
            data.sort(key=lambda x: x.get("watch_date", ""), reverse=True)
            self._render_diary_timeline(data)
        else:
            data = [m for m in self.watchlist_data
                    if self.filter == "all" or m.get("status") == self.filter]
            if not data:
                self._render_empty()
            else:
                for movie in data:
                    self._render_standard_card(movie)

    def _render_empty(self):
        wrap = ctk.CTkFrame(self.movie_area, fg_color=BG_CARD, corner_radius=20)
        wrap.pack(fill="x", pady=20)
        ctk.CTkLabel(wrap, text="🎞️", font=("Arial", 40)).pack(pady=(30, 5))
        ctk.CTkLabel(wrap, text="Your watchlist is empty.",
                     font=("Trebuchet MS", 15, "bold"), text_color=TEXT_GRAY).pack()
        ctk.CTkLabel(wrap, text="Add a movie above to get started.",
                     font=("Trebuchet MS", 12), text_color="#555").pack(pady=(4, 30))

    # ── STANDARD CARD (All / Plan / Watching / Watched) ──────────────────────
    def _render_standard_card(self, movie):
        card = ctk.CTkFrame(
            self.movie_area, fg_color=BG_CARD,
            corner_radius=14, border_width=1, border_color="#333"
        )
        card.pack(fill="x", pady=6)

        poster_box = ctk.CTkFrame(card, fg_color="#1E1E1E", width=52, height=76, corner_radius=8)
        poster_box.pack(side="left", padx=16, pady=12)
        poster_box.pack_propagate(False)

        p_path = movie.get("poster_local", "")
        if p_path and os.path.exists(p_path):
            try:
                img = Image.open(p_path).convert("RGB")
                ctk_img = ctk.CTkImage(img, size=(52, 76))
                ctk.CTkLabel(poster_box, image=ctk_img, text="").pack(fill="both", expand=True)
            except:
                ctk.CTkLabel(poster_box, text="🎬", font=("Arial", 20), text_color="#555").pack(expand=True)
        else:
            ctk.CTkLabel(poster_box, text="🎬", font=("Arial", 20), text_color="#555").pack(expand=True)

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, pady=12)

        ctk.CTkLabel(info, text=movie.get("title", "Unknown"),
                     font=("Trebuchet MS", 15, "bold"),
                     text_color=TEXT_WHITE, anchor="w").pack(anchor="w")

        year   = movie.get("year", "N/A")
        status = movie.get("status", "")
        status_color = {
            "Plan to Watch": "#6D2323",
            "Watching":      "#6D3F23",
            "Watched":       "#3A4B38"
        }.get(status, TEXT_GRAY)

        meta = ctk.CTkFrame(info, fg_color="transparent")
        meta.pack(anchor="w", pady=(4, 0))
        ctk.CTkLabel(meta, text=year, font=("Trebuchet MS", 12), text_color="#B9B3B3").pack(side="left")
        ctk.CTkLabel(meta, text="  •  ", font=("Trebuchet MS", 12), text_color="#444").pack(side="left")
        badge = ctk.CTkFrame(meta, fg_color=status_color, corner_radius=8)
        badge.pack(side="left")
        ctk.CTkLabel(badge, text=status, font=("Trebuchet MS", 11, "bold"),
                     text_color=TEXT_WHITE).pack(padx=10, pady=3)

        rating = int(float(movie.get("rating", 0) or 0))
        if rating > 0:
            r_row = ctk.CTkFrame(info, fg_color="transparent")
            r_row.pack(anchor="w", pady=(4, 0))
            ctk.CTkLabel(r_row, text=f"⭐ {rating}/10",
                         font=("Trebuchet MS", 12, "bold"),
                         text_color=STAR_ON).pack(side="left")

        notes = movie.get("notes", "").strip()
        if notes:
            snippet = notes if len(notes) <= 80 else notes[:80] + "…"
            ctk.CTkLabel(info, text=f'"{snippet}"',
                         font=("Trebuchet MS", 11, "italic"),
                         text_color="#888", anchor="w", wraplength=460).pack(anchor="w", pady=(3, 0))

        ctrl = ctk.CTkFrame(card, fg_color="transparent")
        ctrl.pack(side="right", padx=16)

        status_menu = ctk.CTkOptionMenu(
            ctrl, values=["Plan to Watch", "Watching", "Watched"],
            width=140, height=32,
            fg_color="#1E1E1E", button_color="#444",
            font=("Trebuchet MS", 12),
            command=lambda v, m=movie: self._handle_status_change(m, v)
        )
        status_menu.set(movie.get("status", "Plan to Watch"))
        status_menu.pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            ctrl, text="Delete", width=34, height=32,
            fg_color="#2A2A2A", hover_color="#3A1A1A",
            border_width=1, border_color="#444",
            text_color=RED, corner_radius=8,
            command=lambda m=movie: self._delete_movie(m)
        ).pack(side="left")

    # ── DIARY TIMELINE ────────────────────────────────────────────────────────
    def _render_diary_timeline(self, data):
        if not data:
            wrap = ctk.CTkFrame(self.movie_area, fg_color=BG_CARD, corner_radius=20)
            wrap.pack(fill="x", pady=20)
            ctk.CTkLabel(wrap, text="🎞️", font=("Arial", 40)).pack(pady=(30, 5))
            ctk.CTkLabel(wrap, text="No diary entries yet.",
                         font=("Trebuchet MS", 15, "bold"), text_color=TEXT_GRAY).pack()
            ctk.CTkLabel(wrap, text="Mark a movie as Watched to log it here.",
                         font=("Trebuchet MS", 12), text_color="#555").pack(pady=(4, 30))
            return

        hdr = ctk.CTkFrame(self.movie_area, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(hdr, text="My Movie Diary",
                     font=("Trebuchet MS", 20, "bold"), text_color=TEXT_WHITE).pack(side="left")
        ctk.CTkLabel(hdr, text=f"{len(data)} entries",
                     font=("Trebuchet MS", 13), text_color=TEXT_GRAY).pack(side="left", padx=16, pady=6)

        for movie in data:
            item = ctk.CTkFrame(
                self.movie_area, fg_color=BG_CARD,
                corner_radius=16, border_width=1, border_color="#333"
            )
            item.pack(fill="x", pady=8)

            poster_box = ctk.CTkFrame(item, fg_color="#1E1E1E", width=90, height=130, corner_radius=10)
            poster_box.pack(side="left", padx=18, pady=14)
            poster_box.pack_propagate(False)

            p_path = movie.get("poster_local", "")
            if p_path and os.path.exists(p_path):
                try:
                    img = Image.open(p_path).convert("RGB")
                    ctk_img = ctk.CTkImage(img, size=(90, 130))
                    ctk.CTkLabel(poster_box, image=ctk_img, text="").pack(fill="both", expand=True)
                except:
                    ctk.CTkLabel(poster_box, text="🎬", font=("Arial", 28), text_color="#555").pack(expand=True)
            else:
                ctk.CTkLabel(poster_box, text="🎬", font=("Arial", 28), text_color="#555").pack(expand=True)

            mid = ctk.CTkFrame(item, fg_color="transparent")
            mid.pack(side="left", fill="both", expand=True, pady=14)

            ctk.CTkLabel(mid, text=movie.get("title", "Unknown"),
                         font=("Trebuchet MS", 16, "bold"),
                         text_color=TEXT_WHITE, anchor="w").pack(fill="x")

            info_row = ctk.CTkFrame(mid, fg_color="transparent")
            info_row.pack(anchor="w", pady=(4, 4))
            ctk.CTkLabel(info_row, text=f"{movie.get('watch_date', '–')}",
                         font=("Trebuchet MS", 12, "bold"), text_color="#BBBBBB").pack(side="left")
            ctk.CTkLabel(info_row, text="  •  ",
                         font=("Trebuchet MS", 12), text_color="#444").pack(side="left")
            ctk.CTkLabel(info_row, text=f"📺 {movie.get('platform', 'Other')}",
                         font=("Trebuchet MS", 12, "bold"), text_color="#2d5a27").pack(side="left")

            rating = int(float(movie.get("rating", 0) or 0))
            if rating > 0:
                r_row = ctk.CTkFrame(mid, fg_color="transparent")
                r_row.pack(anchor="w", pady=(2, 4))
                ctk.CTkLabel(r_row, text=f"⭐ {rating}/10",
                             font=("Trebuchet MS", 13, "bold"),
                             text_color=STAR_ON).pack(side="left")

            notes = movie.get("notes", "").strip()
            if notes:
                ctk.CTkLabel(mid, text=notes,
                             font=("Trebuchet MS", 12),
                             text_color="#959595",
                             wraplength=520, justify="left", anchor="w").pack(fill="x")

            right = ctk.CTkFrame(item, fg_color="transparent")
            right.pack(side="right", padx=18, pady=14)

            ctk.CTkButton(
                right, text="✏ Edit Log",
                width=90, height=34,
                fg_color=BG_TAB, hover_color="#3A3A3A",
                border_width=1, border_color="#444",
                font=("Trebuchet MS", 12, "bold"),
                corner_radius=10,
                command=lambda m=movie: self._open_diary_popup(m)
            ).pack(pady=(0, 8))

            ctk.CTkButton(
                right, text="↺ Re-watch",
                width=90, height=34,
                fg_color=BLUE, hover_color="#1a2a70",
                font=("Trebuchet MS", 12, "bold"),
                corner_radius=10,
                command=lambda m=movie: self._handle_status_change(m, "Watching")
            ).pack()

    # ── ACTIONS ───────────────────────────────────────────────────────────────
    def _handle_status_change(self, movie, new_status):
        if new_status == "Watched":
            self._open_diary_popup(movie)
        else:
            movie["status"] = new_status
            self._save_data()
            self._refresh()

    def _open_diary_popup(self, movie):
        popup = ctk.CTkToplevel(self)
        popup.title("Log Entry")
        popup.geometry("500x660")
        popup.attributes("-topmost", True)
        popup.configure(fg_color=BG_MAIN)

        cont = ctk.CTkFrame(popup, fg_color="transparent")
        cont.pack(fill="both", expand=True, padx=35, pady=30)

        ctk.CTkLabel(cont, text="Movie Logbook",
                     font=("Georgia", 22, "bold"), text_color=ORANGE).pack(pady=(0, 6))
        ctk.CTkLabel(cont, text=movie.get("title", ""),
                     font=("Trebuchet MS", 14), text_color=TEXT_GRAY).pack(pady=(0, 16))

        # ── Watch Date dengan tombol kalender ────────────────────────────────
        ctk.CTkLabel(cont, text="Watch Date",
                     font=("Trebuchet MS", 12, "bold"), text_color=TEXT_WHITE).pack(anchor="w")

        date_row = ctk.CTkFrame(cont, fg_color="transparent")
        date_row.pack(fill="x", pady=(5, 14))

        e_date = ctk.CTkEntry(
            date_row, height=38,
            fg_color="#1E1E1E", border_color="#444",
            font=("Trebuchet MS", 13)
        )
        e_date.pack(side="left", fill="x", expand=True, padx=(0, 8))
        e_date.insert(0, movie.get("watch_date", datetime.now().strftime("%Y-%m-%d")))

        def open_calendar():
            cal_win = ctk.CTkToplevel(popup)
            cal_win.title("Pick a Date")
            cal_win.resizable(False, False)
            cal_win.attributes("-topmost", True)
            cal_win.grab_set()

            try:
                init_date = datetime.strptime(e_date.get(), "%Y-%m-%d")
            except ValueError:
                init_date = datetime.now()

            cal = Calendar(
                cal_win,
                selectmode="day",
                year=init_date.year,
                month=init_date.month,
                day=init_date.day,
                date_pattern="yyyy-mm-dd",
                background="#1E1E1E",
                foreground="#FFFFFF",
                headersbackground="#2E2E2E",
                headersforeground="#F5A623",
                selectbackground="#5C1D24",
                selectforeground="#FFFFFF",
                normalbackground="#1E1E1E",
                normalforeground="#FFFFFF",
                weekendbackground="#1E1E1E",
                weekendforeground="#AAAAAA",
                othermonthforeground="#555555",
                othermonthbackground="#1E1E1E",
                font=("Trebuchet MS", 11),
                borderwidth=0,
            )
            cal.pack(padx=12, pady=(12, 6))

            def pick_date():
                e_date.delete(0, "end")
                e_date.insert(0, cal.get_date())
                cal_win.destroy()

            ctk.CTkButton(
                cal_win, text="✔ Pick a Date",
                fg_color="#5C1D24", hover_color="#7a2530",
                height=36, font=("Trebuchet MS", 12, "bold"),
                corner_radius=10,
                command=pick_date
            ).pack(pady=(0, 12), padx=12, fill="x")

        ctk.CTkButton(
            date_row, text="📅",
            width=42, height=38,
            fg_color="#1E1E1E", hover_color="#2E2E2E",
            border_width=1, border_color="#444",
            font=("Arial", 16),
            corner_radius=8,
            command=open_calendar
        ).pack(side="left")

        # ── Platform ─────────────────────────────────────────────────────────
        ctk.CTkLabel(cont, text="Where did you watch it?",
                     font=("Trebuchet MS", 12, "bold"), text_color=TEXT_WHITE).pack(anchor="w")
        e_plat = ctk.CTkOptionMenu(
            cont, values=["Cinema", "Netflix", "Disney+", "Prime Video", "Blu-ray/DVD", "Download", "Other"],
            height=38, fg_color="#1E1E1E", button_color="#444",
            font=("Trebuchet MS", 12)
        )
        e_plat.pack(fill="x", pady=(5, 14))
        e_plat.set(movie.get("platform", "Cinema"))

        # ── Rating ────────────────────────────────────────────────────────────
        ctk.CTkLabel(cont, text="Your Rating (1–10 stars):",
                     font=("Trebuchet MS", 12, "bold"), text_color=TEXT_WHITE).pack(anchor="w")
        star_frame = ctk.CTkFrame(cont, fg_color="transparent")
        star_frame.pack(anchor="w", pady=(6, 4))

        init_rating = int(float(movie.get("rating", 0) or 0))
        rating_var = [init_rating]

        rating_lbl = ctk.CTkLabel(
            star_frame,
            text=f"  {init_rating}/10" if init_rating > 0 else "  Not rated",
            font=("Trebuchet MS", 12, "bold"),
            text_color=STAR_ON
        )

        def on_star_click(v):
            rating_var[0] = v
            rating_lbl.configure(text=f"  {v}/10")

        star_widget = StarRatingWidget(
            star_frame, initial=init_rating, max_stars=10, size=24, command=on_star_click
        )
        star_widget.pack(side="left")
        rating_lbl.pack(side="left", padx=(8, 0))

        # ── Notes ─────────────────────────────────────────────────────────────
        ctk.CTkLabel(cont, text="Personal Notes / Review:",
                     font=("Trebuchet MS", 12, "bold"), text_color=TEXT_WHITE).pack(anchor="w", pady=(10, 0))
        t_notes = ctk.CTkTextbox(cont, height=130, fg_color="#1E1E1E",
                                 border_width=1, border_color="#444",
                                 font=("Trebuchet MS", 12))
        t_notes.pack(fill="both", expand=True, pady=(5, 18))
        t_notes.insert("1.0", movie.get("notes", ""))

        # ── Save ──────────────────────────────────────────────────────────────
        def save_log():
            movie["status"]     = "Watched"
            movie["watch_date"] = e_date.get()
            movie["platform"]   = e_plat.get()
            movie["rating"]     = rating_var[0]
            movie["notes"]      = t_notes.get("1.0", "end-1c")
            self._save_data()
            self._refresh()
            popup.destroy()
            if hasattr(self.app, "show_toast"):
                self.app.show_toast("Log Entry Saved!")

        ctk.CTkButton(cont, text="Save to Diary",
                      fg_color=GREEN_BTN, hover_color="#717171",
                      height=42, font=("Trebuchet MS", 13, "bold"),
                      corner_radius=12, command=save_log).pack(fill="x")

    def _add_movie(self):
        t = self.e_title.get().strip()
        if not t:
            return
        self.watchlist_data.insert(0, {
            "title":        t,
            "year":         self.e_year.get().strip() or "N/A",
            "status":       self.status_var.get(),
            "notes":        "",
            "rating":       0,
            "platform":     "Cinema",
            "watch_date":   datetime.now().strftime("%Y-%m-%d"),
            "poster_local": ""
        })
        self._save_data()
        self.e_title.delete(0, "end")
        self.e_year.delete(0, "end")
        self._refresh()

    def _delete_movie(self, movie):
        if messagebox.askyesno("Delete", f'Remove "{movie["title"]}"?'):
            self.watchlist_data.remove(movie)
            self._save_data()
            self._refresh()

    def _set_filter(self, status):
        self.filter = status
        self._refresh()
