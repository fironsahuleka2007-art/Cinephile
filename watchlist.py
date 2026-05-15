import customtkinter as ctk
import json
import os
from tkinter import messagebox

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

        self.current_user = "guest"
        try:
            if os.path.exists("session.json"):
                with open("session.json", "r") as f:
                    session_data = json.load(f)
                    self.current_user = session_data.get("username", "guest")
        except:
            pass

        self.data_file = f"watchlist_{self.current_user}.json"
        self.watchlist_data = self._load_data()

        self._build_ui()

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

    def _build_ui(self):
        nav = ctk.CTkFrame(self, fg_color=BG_NAV, corner_radius=0, height=50)
        nav.pack(fill="x", side="top")
        nav.pack_propagate(False)

        ctk.CTkButton(nav, text="← Back to Dashboard", fg_color="transparent", text_color=ORANGE,
                      hover_color="#333", font=("Trebuchet MS", 12, "bold"),
                      command=lambda: self.app.show_page("dashboard")).pack(side="left", padx=10, pady=10)
        ctk.CTkLabel(nav, text=f"My Watchlist ({self.current_user})", font=("Helvetica", 16, "bold"),
                     text_color=TEXT_WHITE).pack(side="left", padx=20)

        tab_frame = ctk.CTkFrame(nav, fg_color="transparent")
        tab_frame.pack(side="right", padx=20)
        for lbl, st in [("All", "all"), ("Plan to Watch", "Plan to Watch"), ("Watching", "Watching"), ("Watched", "Watched")]:
            ctk.CTkButton(tab_frame, text=lbl, width=80, height=30, fg_color="transparent",
                          text_color=ORANGE, font=("Trebuchet MS", 11, "bold"),
                          command=lambda s=st: self._set_filter(s)).pack(side="left", padx=5)

        self.body = ctk.CTkScrollableFrame(self, fg_color=BG_MAIN, corner_radius=0)
        self.body.pack(fill="both", expand=True)

        self._build_form()

        self.movie_area = ctk.CTkFrame(self.body, fg_color="transparent")
        self.movie_area.pack(fill="both", expand=True, padx=20, pady=20)

        self._refresh()

    def _build_form(self):
        form = ctk.CTkFrame(self.body, fg_color=BG_CARD, corner_radius=10)
        form.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(form, text="Add Custom Movie to Watchlist", font=("Trebuchet MS", 16, "bold"),
                     text_color=TEXT_WHITE).pack(pady=(15, 5))

        row = ctk.CTkFrame(form, fg_color="transparent")
        row.pack(pady=10)
        self.e_title = ctk.CTkEntry(row, placeholder_text="Movie Title", width=200)
        self.e_title.pack(side="left", padx=5)
        self.e_year = ctk.CTkEntry(row, placeholder_text="Year", width=70)
        self.e_year.pack(side="left", padx=5)

        self.status_var = ctk.StringVar(value="Plan to Watch")
        ctk.CTkOptionMenu(row, values=["Plan to Watch", "Watching", "Watched"],
                          variable=self.status_var, width=130, fg_color=ORANGE,
                          text_color="black").pack(side="left", padx=5)
        ctk.CTkButton(row, text="Add", width=60, fg_color=GREEN, hover_color="#2f855a",
                      command=self._add_movie).pack(side="left", padx=10)

    def _refresh(self):
        self.watchlist_data = self._load_data()
        for w in self.movie_area.winfo_children():
            w.destroy()

        filtered = [m for m in self.watchlist_data if (
            self.filter == "all" or m.get("status", "Plan to Watch") == self.filter
        )]
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
        # Card lebih tinggi untuk tampung review
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=10, width=280)
        card.pack(side="left", padx=10, fill="both", expand=True)

        # TITLE
        title = movie.get("title", "Unknown")
        ctk.CTkLabel(card, text=title[:25] + "..." if len(title) > 25 else title,
                     font=("Helvetica", 15, "bold"), text_color=TEXT_WHITE).pack(anchor="w", padx=15, pady=(15, 0))

        # YEAR
        ctk.CTkLabel(card, text=movie.get("year", "N/A"),
                     font=("Helvetica", 12), text_color=ORANGE).pack(anchor="w", padx=15)

        # RATING SCRAPING (dari database asli, tidak diubah)
        scraped_rating = movie.get("rating", "N/A")
        if scraped_rating != "N/A":
            ctk.CTkLabel(card, text=f"★ {scraped_rating}/10 (Global)",
                         font=("Helvetica", 11), text_color="#FF3333").pack(anchor="w", padx=15, pady=(2, 0))

        # USER REVIEW SECTION
        user_rating = movie.get("user_rating", 0)
        user_review = movie.get("user_review", "")

        if user_rating > 0 or user_review:
            review_frame = ctk.CTkFrame(card, fg_color="#1E1E1E", corner_radius=8)
            review_frame.pack(fill="x", padx=15, pady=(8, 5))

            # Bintang user
            if user_rating > 0:
                stars_str = "★" * user_rating + "☆" * (10 - user_rating)
                ctk.CTkLabel(review_frame, text=f"My Rating:  {stars_str}",
                             font=("Arial", 13), text_color=ORANGE).pack(anchor="w", padx=10, pady=(8, 2))

            # Teks review user
            if user_review:
                short_review = user_review[:60] + "..." if len(user_review) > 60 else user_review
                ctk.CTkLabel(review_frame, text=f'"{short_review}"',
                             font=("Helvetica", 11, "italic"), text_color=TEXT_GRAY,
                             wraplength=220, justify="left").pack(anchor="w", padx=10, pady=(0, 8))
        else:
            # Belum ada review
            ctk.CTkLabel(card, text="No review yet", font=("Helvetica", 11, "italic"),
                         text_color="#555555").pack(anchor="w", padx=15, pady=(5, 0))

        # ACTION BUTTONS
        action_frame = ctk.CTkFrame(card, fg_color="transparent")
        action_frame.pack(fill="x", padx=15, pady=(8, 15))

        current_status = movie.get("status", "Plan to Watch")
        btn_color = GREEN if current_status == "Watched" else (BLUE if current_status == "Watching" else "#555")

        status_menu = ctk.CTkOptionMenu(
            action_frame, values=["Plan to Watch", "Watching", "Watched"],
            fg_color=btn_color, button_color=btn_color, width=120, height=26,
            command=lambda v, m=movie: self._update_status(m, v)
        )
        status_menu.set(current_status)
        status_menu.pack(side="left")

        ctk.CTkButton(action_frame, text="Delete", width=50, height=26, fg_color=RED,
                      command=lambda m=movie: self._delete_movie(m)).pack(side="right")

        # Tombol edit review inline
        ctk.CTkButton(action_frame, text="✏ Review", width=65, height=26,
                      fg_color="#444444", hover_color="#555555", text_color=TEXT_WHITE,
                      font=("Trebuchet MS", 10),
                      command=lambda m=movie: self._open_review_popup(m)).pack(side="right", padx=5)

    def _open_review_popup(self, movie):
        """Popup untuk edit bintang + review langsung dari watchlist"""
        popup = ctk.CTkToplevel(self)
        popup.title(f"Review: {movie.get('title', '')}")
        popup.geometry("380x320")
        popup.resizable(False, False)
        popup.configure(fg_color=BG_CARD)
        popup.grab_set()

        ctk.CTkLabel(popup, text=movie.get("title", "")[:30],
                     font=("Helvetica", 16, "bold"), text_color=TEXT_WHITE).pack(pady=(20, 5))

        # Bintang
        star_frame = ctk.CTkFrame(popup, fg_color="transparent")
        star_frame.pack(pady=10)
        ctk.CTkLabel(star_frame, text="Rating:", font=("Helvetica", 13), text_color=TEXT_GRAY).pack(side="left", padx=(0, 10))

        star_buttons = []
        current_rating = movie.get("user_rating", 0)
        selected = [current_rating]  # pakai list biar bisa dimodif di nested func

        def set_stars(n):
            selected[0] = n
            for i, b in enumerate(star_buttons):
                b.configure(text="★" if i < n else "☆",
                            text_color=ORANGE if i < n else "#555555")

        for i in range(1, 11):
            btn = ctk.CTkButton(star_frame, text="★" if i <= current_rating else "☆",
                                width=26, height=28, fg_color="transparent",
                                hover_color="#3A3A3A", font=("Arial", 16),
                                text_color=ORANGE if i <= current_rating else "#555555",
                                command=lambda n=i: set_stars(n))
            btn.pack(side="left", padx=1)
            star_buttons.append(btn)

        # Text review
        ctk.CTkLabel(popup, text="Notes / Review:", font=("Helvetica", 13), text_color=TEXT_GRAY).pack(anchor="w", padx=25)
        review_box = ctk.CTkTextbox(popup, width=330, height=100, fg_color="#1E1E1E",
                                    text_color=TEXT_WHITE, font=("Helvetica", 12), corner_radius=8)
        review_box.pack(padx=25, pady=5)

        existing_review = movie.get("user_review", "")
        if existing_review:
            review_box.insert("1.0", existing_review)

        def save_review():
            movie["user_rating"] = selected[0]
            movie["user_review"] = review_box.get("1.0", "end").strip()
            self._save_data()
            self._refresh()
            popup.destroy()

        ctk.CTkButton(popup, text="Save Review", fg_color=ORANGE, text_color="black",
                      font=("Helvetica", 13, "bold"), height=38, width=200,
                      command=save_review).pack(pady=15)

    def _update_status(self, movie, new_status):
        movie["status"] = new_status
        self._save_data()
        self._refresh()

    def _add_movie(self):
        title = self.e_title.get().strip()
        if not title:
            return
        self.watchlist_data.insert(0, {
            "title": title,
            "year": self.e_year.get().strip() or "Unknown",
            "genre": "N/A",
            "rating": "N/A",
            "status": self.status_var.get(),
            "user_rating": 0,
            "user_review": ""
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