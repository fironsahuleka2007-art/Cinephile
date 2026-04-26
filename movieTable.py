import customtkinter as ctk
import os
from PIL import Image

BG_MAIN    = "#1A1A1A"
BG_LIGHT   = "#F4F4F4"
TEXT_WHITE = "#FFFFFF"
TEXT_GRAY  = "#AAAAAA"
ACCENT     = "#E53935"

class MovietablePage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=BG_MAIN, corner_radius=0)
        self.app = app
        self.current_page = 0
        self.items_per_page = 10
        self.search_query = ""
        self.filtered_list = self.app.movie_list 
        self._build_ui()

    def _build_nav(self):
        nav = ctk.CTkFrame(self, fg_color="#111111", corner_radius=0, height=50)
        nav.pack(fill="x", side="top")
        nav.pack_propagate(False)

        btn_frame = ctk.CTkFrame(nav, fg_color="transparent")
        btn_frame.pack(side="left", padx=20, pady=10)

        # FULL NAVBAR
        ctk.CTkButton(btn_frame, text="Home", fg_color="transparent", text_color="orange", font=("Arial", 12, "bold"), command=lambda: self.app.show_page("dashboard")).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Movie Table", fg_color="transparent", text_color="white", font=("Arial", 12, "bold")).pack(side="left", padx=10) # Aktif
        ctk.CTkButton(btn_frame, text="Watchlist", fg_color="transparent", text_color="orange", font=("Arial", 12, "bold"), command=lambda: self.app.show_page("watchlist")).pack(side="left", padx=10)

    def _build_ui(self):
        self._build_nav()

        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=(30, 10))
        ctk.CTkLabel(header_frame, text="Movie Database", font=("Helvetica", 36, "bold"), text_color=TEXT_WHITE).pack()
        ctk.CTkLabel(header_frame, text="Daftar semua film yang tersimpan secara lokal.", font=("Trebuchet MS", 14), text_color=TEXT_GRAY).pack()

        self.table_container = ctk.CTkFrame(self, fg_color=BG_LIGHT, corner_radius=15)
        self.table_container.pack(fill="both", expand=True, padx=40, pady=(0, 20))

        self.rows_frame = ctk.CTkScrollableFrame(self.table_container, fg_color="transparent", corner_radius=0)
        self.rows_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.pagination_frame = ctk.CTkFrame(self.table_container, fg_color="transparent")
        self.pagination_frame.pack(fill="x", pady=15)

        self.render_table()

    def render_table(self):
        for widget in self.rows_frame.winfo_children(): widget.destroy()
        for widget in self.pagination_frame.winfo_children(): widget.destroy()

        start_index = self.current_page * self.items_per_page
        end_index = start_index + self.items_per_page
        movies_to_show = self.filtered_list[start_index:end_index]
        total_movies = len(self.filtered_list)
        total_pages = (total_movies + self.items_per_page - 1) // self.items_per_page

        for movie in movies_to_show:
            card = ctk.CTkFrame(self.rows_frame, fg_color="#FFFFFF", corner_radius=10, border_width=1, border_color="#DDDDDD", height=90)
            card.pack(fill="x", padx=10, pady=6)
            card.pack_propagate(False)
            card.configure(cursor="hand2")

            poster_lbl = ctk.CTkLabel(card, text="Image", fg_color="#E0E0E0", width=50, height=75, corner_radius=5)
            poster_lbl.pack(side="left", padx=10, pady=7)
            
            # Load poster lokal jika ada
            path = movie.get("poster_local", "")
            if path and os.path.exists(path):
                try:
                    im = Image.open(path)
                    poster_lbl.configure(image=ctk.CTkImage(im, size=(50, 75)), text="")
                except: pass

            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            
            lbl_title = ctk.CTkLabel(info_frame, text=movie.get("title", "Unknown"), font=("Trebuchet MS", 16, "bold"), text_color="#7A1C1C", anchor="w")
            lbl_title.pack(fill="x")
            lbl_desc = ctk.CTkLabel(info_frame, text=f"{movie.get('year', 'N/A')}  •  {movie.get('genre', 'N/A')}", font=("Trebuchet MS", 12), text_color="#555555", anchor="w")
            lbl_desc.pack(fill="x")

            rating_frame = ctk.CTkFrame(card, fg_color="transparent", width=80)
            rating_frame.pack(side="right", fill="y", padx=20)
            lbl_rate = ctk.CTkLabel(rating_frame, text=f"{movie.get('rating', 'N/A')}", font=("Helvetica", 18, "bold"), text_color="#8A4B1A")
            lbl_rate.pack(side="top", pady=(15,0))
            lbl_star = ctk.CTkLabel(rating_frame, text="⭐ IMDb", font=("Trebuchet MS", 10), text_color="#AAAAAA")
            lbl_star.pack(side="top")

            # --- SANGAT PENTING: BINDING KLIK AGAR PINDAH PAGE ---
            def go_to_detail(event, m=movie):
                self.app.show_page("moviedetail", data=m)

            card.bind("<Button-1>", go_to_detail)
            info_frame.bind("<Button-1>", go_to_detail)
            lbl_title.bind("<Button-1>", go_to_detail)
            lbl_desc.bind("<Button-1>", go_to_detail)
            poster_lbl.bind("<Button-1>", go_to_detail)
            rating_frame.bind("<Button-1>", go_to_detail)
            lbl_rate.bind("<Button-1>", go_to_detail)
            lbl_star.bind("<Button-1>", go_to_detail)

        # Pagination
        ctk.CTkButton(self.pagination_frame, text="◀ Prev", width=100, fg_color=ACCENT, state="normal" if self.current_page > 0 else "disabled", command=self.prev_page).pack(side="left", padx=40)
        ctk.CTkLabel(self.pagination_frame, text=f"Page {self.current_page + 1} of {max(1, total_pages)}", text_color="black").pack(side="left", expand=True)
        ctk.CTkButton(self.pagination_frame, text="Next ▶", width=100, fg_color=ACCENT, state="normal" if end_index < total_movies else "disabled", command=self.next_page).pack(side="right", padx=40)

    def prev_page(self):
        if self.current_page > 0: self.current_page -= 1; self.render_table()

    def next_page(self):
        if (self.current_page + 1) * self.items_per_page < len(self.filtered_list): self.current_page += 1; self.render_table()