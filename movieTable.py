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
    # Parameter genre_filter udah ditambahkan di sini biar gak error lagi
    def __init__(self, master, app, genre_filter=None):
        super().__init__(master, fg_color=BG_MAIN, corner_radius=0)
        self.app = app
        self.current_page = 0
        self.items_per_page = 10
        
        self.all_movies = getattr(self.app, "movie_list", [])
        self.filtered_list = self.all_movies.copy()
        
        self._build_ui()

        # Eksekusi filter otomatis (dari search bar atau klik genre)
        if genre_filter:
            self.after(100, lambda: self.filter_data(genre_filter))
        else:
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
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search Local...", width=200, height=35, fg_color="#222", border_color="#444", font=("Trebuchet MS", 13))
        self.search_entry.pack(side="left", padx=5)
        
        ctk.CTkButton(search_frame, text="🔍", width=40, height=35, fg_color="#E53935", 
                    command=lambda: self.filter_data(self.search_entry.get())).pack(side="left")

        pill_outer = ctk.CTkFrame(nav, fg_color="transparent")
        pill_outer.place(relx=0.5, rely=0.5, anchor="center")
        pill = ctk.CTkFrame(pill_outer, fg_color="#2E2E2E", corner_radius=20, height=38)
        pill.pack()

        ctk.CTkButton(pill, text="Home", width=80, height=32, fg_color="transparent", text_color="#AAAAAA", corner_radius=16, font=("Trebuchet MS", 13, "bold"), command=lambda: self.app.show_page("dashboard")).pack(side="left", padx=(3, 1), pady=3)
        ctk.CTkButton(pill, text="Genre Analysis", width=130, height=32, fg_color="transparent", text_color="#AAAAAA", corner_radius=16, font=("Trebuchet MS", 13, "bold"), command=lambda: self.app.show_page("genreanalyze")).pack(side="left", padx=1, pady=3)
        ctk.CTkButton(pill, text="Movie Table", width=110, height=32, fg_color="#E53935", text_color="#FFFFFF", corner_radius=16, font=("Trebuchet MS", 13, "bold")).pack(side="left", padx=(1, 3), pady=3)
        ctk.CTkButton(pill, text="Watchlist", width=90, height=32, fg_color="transparent", text_color="#AAAAAA", corner_radius=16, font=("Trebuchet MS", 13, "bold"), command=lambda: self.app.show_page("watchlist")).pack(side="left", padx=(1, 3), pady=3)

    def filter_data(self, query):
        if query is None: return
        query = query.lower().strip()
        self.current_page = 0 
        
        all_data = getattr(self.app, "movie_list", [])
        self.all_movies = all_data
        
        if not query:
            self.filtered_list = all_data.copy()
        else:
            self.filtered_list = [
                m for m in all_data 
                if query in str(m.get("title", "")).lower() or 
                   query in str(m.get("genre", "")).lower()
            ]
        self.render_table()

    def _build_ui(self):
        self._build_nav()

        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=(30, 10))
        ctk.CTkLabel(header_frame, text="Movie Database", font=("Helvetica", 38, "bold"), text_color=TEXT_WHITE).pack()

        self.table_container = ctk.CTkFrame(self, fg_color=BG_LIGHT, corner_radius=15)
        self.table_container.pack(fill="both", expand=True, padx=40, pady=(0, 20))

        self.rows_frame = ctk.CTkScrollableFrame(self.table_container, fg_color="transparent")
        self.rows_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.pagination_frame = ctk.CTkFrame(self.table_container, fg_color="transparent")
        self.pagination_frame.pack(fill="x", pady=15)

        self.render_table()

    def render_table(self):
        for widget in self.rows_frame.winfo_children(): widget.destroy()
        for widget in self.pagination_frame.winfo_children(): widget.destroy()

        start = self.current_page * self.items_per_page
        end = start + self.items_per_page
        movies_to_show = self.filtered_list[start:end]
        total_pages = max(1, (len(self.filtered_list) + self.items_per_page - 1) // self.items_per_page)

        for movie in movies_to_show:
            card = ctk.CTkFrame(self.rows_frame, fg_color="#FFFFFF", corner_radius=12, height=100, cursor="hand2")
            card.pack(fill="x", padx=10, pady=8)
            card.pack_propagate(False)

            def go_to_detail(e, m=movie):
                self.app.show_page("moviedetail", data=m)

            poster_lbl = ctk.CTkLabel(card, text="🎬", fg_color="#E0E0E0", width=60, height=85, corner_radius=5)
            poster_lbl.pack(side="left", padx=10, pady=7)
            
            path = movie.get("poster_local", "")
            if path and os.path.exists(path):
                try:
                    img = ctk.CTkImage(Image.open(path), size=(60, 85))
                    poster_lbl.configure(image=img, text="")
                except: pass

            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", fill="both", expand=True, padx=15, pady=15)
            
            title_lbl = ctk.CTkLabel(info, text=movie.get("title", "Unknown"), font=("Trebuchet MS", 18, "bold"), text_color="#7A1C1C", anchor="w")
            title_lbl.pack(fill="x")
            
            subtitle_lbl = ctk.CTkLabel(info, text=f"{movie.get('year', 'N/A')} • {movie.get('genre', 'N/A')}", font=("Trebuchet MS", 14), text_color="#555555", anchor="w")
            subtitle_lbl.pack(fill="x")

            rt_frame = ctk.CTkFrame(card, fg_color="transparent")
            rt_frame.pack(side="right", padx=30)
            
            rat_val = ctk.CTkLabel(rt_frame, text=f"{movie.get('rating', 'N/A')}", font=("Helvetica", 20, "bold"), text_color="#8A4B1A")
            rat_val.pack()
            rat_text = ctk.CTkLabel(rt_frame, text="⭐ IMDb", font=("Trebuchet MS", 12), text_color="#AAAAAA")
            rat_text.pack()

            widgets_to_bind = [card, poster_lbl, info, title_lbl, subtitle_lbl, rt_frame, rat_val, rat_text]
            for w in widgets_to_bind:
                w.bind("<Button-1>", go_to_detail)

        ctk.CTkButton(self.pagination_frame, text="◀ Prev", width=120, height=35, font=("Inter", 13, "bold"), fg_color=ACCENT, command=self.prev_page, state="normal" if self.current_page > 0 else "disabled").pack(side="left", padx=40)
        ctk.CTkLabel(self.pagination_frame, text=f"Page {self.current_page + 1} of {total_pages}", font=("Inter", 14), text_color="black").pack(side="left", expand=True)
        ctk.CTkButton(self.pagination_frame, text="Next ▶", width=120, height=35, font=("Inter", 13, "bold"), fg_color=ACCENT, command=self.next_page, state="normal" if end < len(self.filtered_list) else "disabled").pack(side="right", padx=40)

    def prev_page(self):
        self.current_page -= 1
        self.render_table()

    def next_page(self):
        self.current_page += 1
        self.render_table()