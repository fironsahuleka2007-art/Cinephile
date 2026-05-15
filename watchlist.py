import customtkinter as ctk
import json
import os
from tkinter import messagebox
from datetime import datetime
from PIL import Image  # Pastikan library Pillow terinstall (pip install Pillow)

# Tema (Konsisten dengan Dashboard)
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
        
        # Cek User
        self.current_user = "guest"
        try:
            if os.path.exists("session.json"):
                with open("session.json", "r") as f:
                    s = json.load(f)
                    self.current_user = s.get("username", "guest")
        except: pass
        
        self.data_file = f"watchlist_{self.current_user}.json"
        self.watchlist_data = self._load_data()
        
        self._build_ui()
        self.bind("<Visibility>", lambda e: self._refresh())

    def _load_data(self):
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
        # --- NAVBAR ---
        nav = ctk.CTkFrame(self, fg_color=BG_NAV, corner_radius=0, height=60)
        nav.pack(fill="x", side="top")
        nav.pack_propagate(False)

        ctk.CTkButton(nav, text="← Back", width=80, fg_color="transparent", text_color=ORANGE, 
                      font=("Trebuchet MS", 12, "bold"), command=lambda: self.app.show_page("dashboard")).pack(side="left", padx=10)
        
        ctk.CTkLabel(nav, text=f"Cinema Logbook: {self.current_user}", 
                     font=("Helvetica", 18, "bold"), text_color=TEXT_WHITE).pack(side="left", padx=20)

        # Tab Filter
        tab_frame = ctk.CTkFrame(nav, fg_color="transparent")
        tab_frame.pack(side="right", padx=20)
        tabs = [("All", "all"), ("Plan", "Plan to Watch"), ("Watching", "Watching"), ("📔 My Diary", "Watched")]
        for lbl, st in tabs:
            btn = ctk.CTkButton(tab_frame, text=lbl, width=90, height=32, fg_color="transparent", 
                          text_color=TEXT_WHITE, font=("Trebuchet MS", 11, "bold"), 
                          hover_color=ACCENT, command=lambda s=st: self._set_filter(s))
            btn.pack(side="left", padx=2)

        self.body = ctk.CTkScrollableFrame(self, fg_color=BG_MAIN, corner_radius=0)
        self.body.pack(fill="both", expand=True)

        self._build_form()

        self.movie_area = ctk.CTkFrame(self.body, fg_color="transparent")
        self.movie_area.pack(fill="both", expand=True, padx=30, pady=10)
        
        self._refresh()

    def _build_form(self):
        form = ctk.CTkFrame(self.body, fg_color=BG_CARD, corner_radius=15, border_width=1, border_color="#333")
        form.pack(fill="x", padx=30, pady=20)
        
        row = ctk.CTkFrame(form, fg_color="transparent")
        row.pack(pady=15, padx=20)
        
        self.e_title = ctk.CTkEntry(row, placeholder_text="Movie Title...", width=300, height=35)
        self.e_title.pack(side="left", padx=5)
        self.e_year = ctk.CTkEntry(row, placeholder_text="Year", width=80, height=35)
        self.e_year.pack(side="left", padx=5)
        
        self.status_var = ctk.StringVar(value="Plan to Watch")
        ctk.CTkOptionMenu(row, values=["Plan to Watch", "Watching", "Watched"], 
                          variable=self.status_var, width=140, height=35, 
                          fg_color="#444", button_color=ORANGE).pack(side="left", padx=5)
        
        ctk.CTkButton(row, text="Add Movie", width=100, height=35, fg_color=GREEN, 
                      font=("Inter", 12, "bold"), command=self._add_movie).pack(side="left", padx=10)

    def _refresh(self):
        for w in self.movie_area.winfo_children(): w.destroy()
        
        if self.filter == "Watched":
            data = [m for m in self.watchlist_data if m.get("status") == "Watched"]
            data.sort(key=lambda x: x.get("watch_date", ""), reverse=True)
            self._render_diary_timeline(data)
        else:
            data = [m for m in self.watchlist_data if (self.filter == "all" or m.get("status") == self.filter)]
            for movie in data:
                self._render_standard_card(movie)

    def _render_standard_card(self, movie):
        card = ctk.CTkFrame(self.movie_area, fg_color=BG_CARD, corner_radius=10, height=80)
        card.pack(fill="x", pady=5)
        
        title_box = ctk.CTkFrame(card, fg_color="transparent")
        title_box.pack(side="left", padx=20, pady=10)
        
        ctk.CTkLabel(title_box, text=movie['title'], font=("Helvetica", 16, "bold"), text_color=TEXT_WHITE).pack(anchor="w")
        ctk.CTkLabel(title_box, text=movie['year'], font=("Helvetica", 12), text_color=ORANGE).pack(anchor="w")

        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(side="right", padx=20)

        status_menu = ctk.CTkOptionMenu(btn_frame, values=["Plan to Watch", "Watching", "Watched"],
                                        width=130, height=28, fg_color="#444",
                                        command=lambda v, m=movie: self._handle_status_change(m, v))
        status_menu.set(movie.get("status"))
        status_menu.pack(side="left", padx=10)

        ctk.CTkButton(btn_frame, text="🗑️", width=35, height=28, fg_color="transparent", 
                      text_color=RED, command=lambda m=movie: self._delete_movie(m)).pack(side="left")

    def _render_diary_timeline(self, data):
        if not data:
            ctk.CTkLabel(self.movie_area, text="No diary entries yet.", text_color=TEXT_GRAY).pack(pady=50)
            return

        for movie in data:
            item = ctk.CTkFrame(self.movie_area, fg_color="#222", corner_radius=12, border_width=1, border_color="#333")
            item.pack(fill="x", pady=10)

            # --- SISI KIRI: POSTER ---
            left_poster = ctk.CTkFrame(item, fg_color=BG_NAV, width=85, height=125, corner_radius=8)
            left_poster.pack(side="left", padx=15, pady=10)
            left_poster.pack_propagate(False)

            p_path = movie.get("poster_local")
            if p_path and os.path.exists(p_path):
                try:
                    img = Image.open(p_path)
                    ctk_img = ctk.CTkImage(img, size=(85, 125))
                    ctk.CTkLabel(left_poster, image=ctk_img, text="").pack(fill="both", expand=True)
                except:
                    ctk.CTkLabel(left_poster, text="No\nImage", text_color=TEXT_GRAY).pack(expand=True)
            else:
                ctk.CTkLabel(left_poster, text="No\nImage", text_color=TEXT_GRAY).pack(expand=True)

            # --- SISI TENGAH: INFO & CATATAN ---
            mid = ctk.CTkFrame(item, fg_color="transparent")
            mid.pack(side="left", fill="both", expand=True, padx=5, pady=15)
            
            # Judul
            ctk.CTkLabel(mid, text=movie['title'], font=("Helvetica", 18, "bold"), text_color=TEXT_WHITE, anchor="w").pack(fill="x")
            
            # INFO (Tanggal & Platform) - Pindah ke samping judul (di bawahnya sedikit agar rapi)
            info_text = f"🗓️ {movie.get('watch_date', '-')}   •   📺 {movie.get('platform', 'Other')}"
            ctk.CTkLabel(mid, text=info_text, font=("Inter", 11, "bold"), text_color=ORANGE, anchor="w").pack(fill="x", pady=(2, 8))

            # Catatan
            notes = movie.get("notes", "No notes provided.")
            ctk.CTkLabel(mid, text=notes, font=("Trebuchet MS", 13), text_color="#CCC", 
                         wraplength=500, justify="left", anchor="w").pack(fill="x")

            # --- SISI KANAN: ACTION ---
            right = ctk.CTkFrame(item, fg_color="transparent")
            right.pack(side="right", padx=15)
            
            ctk.CTkButton(right, text="Edit Log", width=80, height=30, fg_color="#333", 
                          command=lambda m=movie: self._open_diary_popup(m)).pack(pady=5)
            ctk.CTkButton(right, text="Re-watch", width=80, height=30, fg_color=BLUE, 
                          command=lambda m=movie: self._handle_status_change(m, "Watching")).pack(pady=5)

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
        popup.geometry("450x550")
        popup.attributes("-topmost", True)
        popup.configure(fg_color=BG_MAIN)

        cont = ctk.CTkFrame(popup, fg_color="transparent")
        cont.pack(fill="both", expand=True, padx=30, pady=30)

        ctk.CTkLabel(cont, text="📔 Movie Logbook", font=("Helvetica", 22, "bold"), text_color=ORANGE).pack(pady=(0, 20))

        ctk.CTkLabel(cont, text="When did you watch it? (YYYY-MM-DD)", font=("Inter", 12, "bold")).pack(anchor="w")
        e_date = ctk.CTkEntry(cont, height=35, fg_color="#222")
        e_date.pack(fill="x", pady=(5, 15))
        e_date.insert(0, movie.get("watch_date", datetime.now().strftime("%Y-%m-%d")))

        ctk.CTkLabel(cont, text="Where did you watch it?", font=("Inter", 12, "bold")).pack(anchor="w")
        e_plat = ctk.CTkOptionMenu(cont, values=["Cinema", "Netflix", "Disney+", "Prime Video", "Blu-ray/DVD", "Download", "Other"], 
                                   height=35, fg_color="#222", button_color="#444")
        e_plat.pack(fill="x", pady=(5, 15))
        e_plat.set(movie.get("platform", "Cinema"))

        ctk.CTkLabel(cont, text="Personal Notes / Thoughts:", font=("Inter", 12, "bold")).pack(anchor="w")
        t_notes = ctk.CTkTextbox(cont, height=150, fg_color="#222", border_width=1, border_color="#444")
        t_notes.pack(fill="both", expand=True, pady=(5, 20))
        t_notes.insert("1.0", movie.get("notes", ""))

        def save_log():
            movie["status"] = "Watched"
            movie["watch_date"] = e_date.get()
            movie["platform"] = e_plat.get()
            movie["notes"] = t_notes.get("1.0", "end-1c")
            self._save_data()
            self._refresh()
            popup.destroy()
            self.app.show_toast("Log Entry Saved! 🎬")

        ctk.CTkButton(cont, text="Save to Diary", fg_color=GREEN, height=40, font=("Inter", 13, "bold"), command=save_log).pack(fill="x")

    def _add_movie(self):
        t = self.e_title.get().strip()
        if not t: return
        self.watchlist_data.insert(0, {
            "title": t, "year": self.e_year.get().strip() or "N/A",
            "status": self.status_var.get(), "notes": "", "platform": "Cinema",
            "watch_date": datetime.now().strftime("%Y-%m-%d"),
            "poster_local": "" # Default kosong jika input manual
        })
        self._save_data()
        self.e_title.delete(0, 'end')
        self.e_year.delete(0, 'end')
        self._refresh()

    def _delete_movie(self, movie):
        if messagebox.askyesno("Delete", f'Remove "{movie["title"]}"?'):
            self.watchlist_data.remove(movie)
            self._save_data()
            self._refresh()

    def _set_filter(self, status):
        self.filter = status
        self._refresh()