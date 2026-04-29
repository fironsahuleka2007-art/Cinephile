import customtkinter as ctk
import json
import os
from tkinter import messagebox

# Tema disamakan dengan Dashboard biar ga belang
BG_MAIN    = "#1A1A1A"
BG_NAV     = "#111111"
ACCENT     = "#E53935"
BG_CARD    = "#2A2A2A"
ORANGE     = "#FF8C00"
TEXT_WHITE = "#FFFFFF"
TEXT_GRAY  = "#AAAAAA"
GREEN      = "#38a169"
BLUE       = "#3182ce"
RED        = "#c0392b"

class WatchlistPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=BG_MAIN, corner_radius=0)
        self.app = app 
        self.filter = "all"
        self.bind("<Visibility>", lambda e: self._refresh())
        
        # Cek User yang sedang login dari session.json
        self.current_user = "guest"
        try:
            if os.path.exists("session.json"):
                with open("session.json", "r") as f:
                    session_data = json.load(f)
                    self.current_user = session_data.get("username", "guest")
        except: pass
        
        # Nama file database watchlist dinamis sesuai user
        self.data_file = f"watchlist_{self.current_user}.json"
        self.watchlist_data = self._load_data()
        
        self._build_ui()

    def _load_data(self):
        # Kalau belum ada file watchlist buat user ini, bikin array kosong (bukan ambil dari DB utama)
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: return []
        return []

    def _save_data(self):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.watchlist_data, f, indent=4)

    def _build_ui(self):
        # NAVBAR (Warna #111111 biar ga belang sama dashboard)
        nav = ctk.CTkFrame(self, fg_color=BG_NAV, corner_radius=0, height=50)
        nav.pack(fill="x", side="top")
        nav.pack_propagate(False)

        ctk.CTkButton(nav, text="← Back to Dashboard", fg_color="transparent", text_color=ORANGE, hover_color="#333", font=("Trebuchet MS", 12, "bold"), command=lambda: self.app.show_page("dashboard")).pack(side="left", padx=10, pady=10)
        ctk.CTkLabel(nav, text=f"My Watchlist ({self.current_user})", font=("Helvetica", 16, "bold"), text_color=TEXT_WHITE).pack(side="left", padx=20)

        tab_frame = ctk.CTkFrame(nav, fg_color="transparent")
        tab_frame.pack(side="right", padx=20)
        for lbl, st in [("All", "all"), ("Plan to Watch", "Plan to Watch"), ("Watching", "Watching"), ("Watched", "Watched")]:
            ctk.CTkButton(tab_frame, text=lbl, width=80, height=30, fg_color="transparent", text_color=ORANGE, font=("Trebuchet MS", 11, "bold"), command=lambda s=st: self._set_filter(s)).pack(side="left", padx=5)

        self.body = ctk.CTkScrollableFrame(self, fg_color=BG_MAIN, corner_radius=0)
        self.body.pack(fill="both", expand=True)

        self._build_form()

        self.movie_area = ctk.CTkFrame(self.body, fg_color="transparent")
        self.movie_area.pack(fill="both", expand=True, padx=20, pady=20)
        
        self._refresh()

    def _build_form(self):
        form = ctk.CTkFrame(self.body, fg_color=BG_CARD, corner_radius=10)
        form.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(form, text="Add Custom Movie to Watchlist", font=("Trebuchet MS", 16, "bold"), text_color=TEXT_WHITE).pack(pady=(15, 5))
        
        row = ctk.CTkFrame(form, fg_color="transparent")
        row.pack(pady=10)
        self.e_title = ctk.CTkEntry(row, placeholder_text="Movie Title", width=200)
        self.e_title.pack(side="left", padx=5)
        self.e_year = ctk.CTkEntry(row, placeholder_text="Year", width=70)
        self.e_year.pack(side="left", padx=5)
        
        self.status_var = ctk.StringVar(value="Plan to Watch")
        ctk.CTkOptionMenu(row, values=["Plan to Watch", "Watching", "Watched"], variable=self.status_var, width=130, fg_color=ORANGE, text_color="black").pack(side="left", padx=5)
        ctk.CTkButton(row, text="Add", width=60, fg_color=GREEN, hover_color="#2f855a", command=self._add_movie).pack(side="left", padx=10)

    def _refresh(self):
        self.watchlist_data = self._load_data()
        for w in self.movie_area.winfo_children(): w.destroy()
            
        filtered = [m for m in self.watchlist_data if (self.filter == "all" or m.get("status", "Plan to Watch") == self.filter)]
        if not filtered:
            ctk.CTkLabel(self.movie_area, text="Your watchlist is empty.", text_color=TEXT_GRAY).pack(pady=50)
            return

        row_frame = None
        for i, movie in enumerate(filtered):
            if i % 3 == 0:
                row_frame = ctk.CTkFrame(self.movie_area, fg_color="transparent")
                row_frame.pack(fill="x", pady=10)
            self._render_card(row_frame, movie)

    def _render_card(self, parent, movie):
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=10, width=280, height=130)
        card.pack(side="left", padx=10, fill="both", expand=True)
        card.pack_propagate(False)
        
        title = movie.get("title", "Unknown")
        ctk.CTkLabel(card, text=title[:25]+"..." if len(title)>25 else title, font=("Helvetica", 15, "bold"), text_color=TEXT_WHITE).pack(anchor="w", padx=15, pady=(15, 0))
        ctk.CTkLabel(card, text=movie.get("year", "N/A"), font=("Helvetica", 12), text_color=ORANGE).pack(anchor="w", padx=15)
        
        action_frame = ctk.CTkFrame(card, fg_color="transparent")
        action_frame.pack(fill="x", side="bottom", padx=15, pady=15)

        current_status = movie.get("status", "Plan to Watch")
        btn_color = GREEN if current_status == "Watched" else (BLUE if current_status == "Watching" else "#555")
        
        status_menu = ctk.CTkOptionMenu(action_frame, values=["Plan to Watch", "Watching", "Watched"],
                                        fg_color=btn_color, button_color=btn_color, width=120, height=26,
                                        command=lambda v, m=movie: self._update_status(m, v))
        status_menu.set(current_status)
        status_menu.pack(side="left")

        ctk.CTkButton(action_frame, text="Delete", width=50, height=26, fg_color=RED, command=lambda m=movie: self._delete_movie(m)).pack(side="right")

    def _update_status(self, movie, new_status):
        movie["status"] = new_status
        self._save_data()
        self._refresh()

    def _add_movie(self):
        title = self.e_title.get().strip()
        if not title: return
        self.watchlist_data.insert(0, {
            "title": title, "year": self.e_year.get().strip() or "Unknown",
            "genre": "N/A", "rating": "N/A", "status": self.status_var.get()
        })
        self._save_data()
        self.e_title.delete(0, 'end')
        self.e_year.delete(0, 'end')
        self._refresh()

    def _delete_movie(self, movie):
        if messagebox.askyesno("Delete", f'Remove "{movie.get("title")}"?'):
            self.watchlist_data.remove(movie)
            self._save_data()
            self._refresh()

    def _set_filter(self, status):
        self.filter = status
        self._refresh()