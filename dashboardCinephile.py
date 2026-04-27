import customtkinter as ctk
from PIL import Image, ImageTk, ImageOps
import os
import tkinter.font as tkfont
import tkinter as tk

# ── Konstanta Warna & Font ───────────────────────────────────────────────────
BG_MAIN    = "#1A1A1A"
BG_NAV     = "#111111"
BG_TAB     = "#2E2E2E"
BG_LIGHT   = "#F4F4F4"  # Background terang untuk tabel
ACCENT     = "#E53935"
TEXT_WHITE = "#FFFFFF"
TEXT_GRAY  = "#AAAAAA"
TEXT_DARK  = "#111111"

# Warna teks khusus tabel sesuai desain Figma
COL_FILM     = "#7A1C1C"  # Merah gelap
COL_YEAR     = "#111111"  # Hitam
COL_MOOD     = "#2A368F"  # Biru gelap
COL_SYNOPSIS = "#8A4B1A"  # Cokelat gelap

class DashboardPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=BG_MAIN, corner_radius=0)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        self._build_nav()
        
        # Scrollable Body
        self.body = ctk.CTkScrollableFrame(self, fg_color=BG_MAIN, scrollbar_button_color="#444", scrollbar_button_hover_color=ACCENT)
        self.body.pack(fill="both", expand=True, side="top")

        self._build_hero()
        self._build_movie_list()
        self._build_tagline()
        self._build_watchlist_banner()
        self._build_footer()

    def _build_nav(self):
        nav = ctk.CTkFrame(self, fg_color=BG_NAV, corner_radius=0, height=44)
        nav.pack(fill="x", side="top")
        nav.pack_propagate(False)

        # ── KIRI: Logo / Log Out ──
        logout_btn = ctk.CTkLabel(nav, text="◎ Log Out", cursor="hand2", font=("Trebuchet MS", 12, "bold"), text_color=ACCENT)
        logout_btn.pack(side="left", padx=16, pady=8)
        logout_btn.bind("<Button-1>", lambda e: self.app.logout())

        # ── KANAN: Kotak Pencarian (Local Search) ──
        search_frame = ctk.CTkFrame(nav, fg_color="transparent")
        search_frame.pack(side="right", padx=16)

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search Local Database...", 
                                        width=200, height=28, font=("Trebuchet MS", 11),
                                        fg_color="#222", border_color="#444")
        self.search_entry.pack(side="left", padx=5)
        
        search_btn = ctk.CTkButton(search_frame, text="🔍", width=35, height=28, 
                                fg_color=ACCENT, hover_color="#C62828",
                                command=lambda: self.app.handle_local_search(self.search_entry.get()))
        search_btn.pack(side="left")

        # ── TENGAH: Pill Tabs ──
        pill_outer = ctk.CTkFrame(nav, fg_color="transparent")
        pill_outer.place(relx=0.5, rely=0.5, anchor="center")
        
        pill = ctk.CTkFrame(pill_outer, fg_color=BG_TAB, corner_radius=20, height=30)
        pill.pack()

        # Tombol Home (MERAH)
        btn_home = ctk.CTkButton(pill, text="Home", width=60, height=26, fg_color=ACCENT, hover_color="#C62828", text_color=TEXT_WHITE, font=("Trebuchet MS", 10, "bold"), corner_radius=16)
        btn_home.pack(side="left", padx=(3, 1), pady=2)

        # Tombol Genre Analysis (ABU)
        btn_genre = ctk.CTkButton(pill, text="Genre Analysis", width=110, height=26, fg_color="transparent", hover_color="#3A3A3A", text_color=TEXT_GRAY, font=("Trebuchet MS", 10, "bold"), corner_radius=16)
        btn_genre.pack(side="left", padx=1, pady=2)
        btn_genre.configure(command=lambda: self.app.show_page("genreanalyze"))

        # Tombol Movie Table (ABU) - Fungsi Pindah Halaman
        btn_table = ctk.CTkButton(pill, text="Movie Table", width=92, height=26, fg_color="transparent", hover_color="#3A3A3A", text_color=TEXT_GRAY, font=("Trebuchet MS", 10, "bold"), corner_radius=16)
        btn_table.pack(side="left", padx=(1, 3), pady=2)
        btn_table.configure(command=lambda: self.app.show_page("movietable")) 

        # Tombol Watchlist 
        btn_watchlist = ctk.CTkButton(pill, text="Watchlist", width=80, height=26, fg_color="transparent", hover_color="#3A3A3A", text_color=TEXT_GRAY, font=("Trebuchet MS", 10, "bold"), corner_radius=16)
        btn_watchlist.pack(side="left", padx=(1, 3), pady=2)
        btn_watchlist.configure(command=lambda: self.app.show_page("watchlist"))

    # ── BAGIAN HERO (Carousel Gambar) ──────────────────────────────────────────
    def _build_hero(self):
        self.hero_frame = ctk.CTkFrame(self.body, fg_color="#2A2A2A", corner_radius=15, height=450)
        self.hero_frame.pack(fill="x")
        self.hero_frame.pack_propagate(False)

        self.hero_images_list = ["hero1.jpeg", "hero2.jpeg", "hero3.jpeg"] 
        self.current_hero_index = 0

        self.hero_label = ctk.CTkLabel(self.hero_frame, text="")
        self.hero_label.pack(expand=True, fill="both")

        self._update_hero_image()
        self._start_carousel()

    def _update_hero_image(self):
        img_name = self.hero_images_list[self.current_hero_index]
        base_dir = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(base_dir, img_name)
        
        if os.path.exists(img_path):
            try:
                raw_img = Image.open(img_path)
                try:
                    resample_method = Image.Resampling.LANCZOS
                except AttributeError:
                    resample_method = Image.LANCZOS
                
                fitted_img = ImageOps.fit(raw_img, (1400, 450), method=resample_method)
                ctk_img = ctk.CTkImage(light_image=fitted_img, dark_image=fitted_img, size=(1400, 450))
                self.hero_label.configure(image=ctk_img, text="")
            except Exception as e:
                print(f"❌ Error saat memuat gambar {img_path}: {e}")
                self.hero_label.configure(image="", text=f"Gagal memuat {img_name}")
        else:
            self.hero_label.configure(text=f"Gambar {img_name} tidak ditemukan", font=("Trebuchet MS", 14))

    def _start_carousel(self):
        if not self.winfo_exists():
            return
        self.current_hero_index = (self.current_hero_index + 1) % len(self.hero_images_list)
        self._update_hero_image()
        self.after(3000, self._start_carousel)

    def _build_movie_list(self):
        list_container = ctk.CTkFrame(self.body, fg_color=BG_LIGHT, corner_radius=10)
        list_container.pack(fill="x", padx=10, pady=(0, 20))

        ctk.CTkLabel(list_container, text="Top 10\nMovies", font=("Helvetica", 60, "bold"), text_color=TEXT_DARK, justify="left", anchor="w").pack(fill="x", padx=40, pady=(40, 20))

        header_frame = ctk.CTkFrame(list_container, fg_color="transparent")
        header_frame.pack(fill="x", padx=40, pady=(10, 5))
        
        header_font = ("Trebuchet MS", 12, "bold")
        ctk.CTkLabel(header_frame, text="Film", font=header_font, text_color=TEXT_GRAY, width=240, anchor="w").grid(row=0, column=0, sticky="w", padx=(0, 15))
        ctk.CTkLabel(header_frame, text="Year", font=header_font, text_color=TEXT_GRAY, width=60, anchor="w").grid(row=0, column=1, sticky="w", padx=(0, 15))
        ctk.CTkLabel(header_frame, text="Mood", font=header_font, text_color=TEXT_GRAY, width=160, anchor="w").grid(row=0, column=2, sticky="w", padx=(0, 15))
        ctk.CTkLabel(header_frame, text="Synopsis", font=header_font, text_color=TEXT_GRAY, anchor="e").grid(row=0, column=3, sticky="e")
        header_frame.columnconfigure(3, weight=1)

        ctk.CTkFrame(list_container, fg_color="#DDDDDD", height=2).pack(fill="x", padx=40, pady=5)

        movies_data = self.app.movie_list[:10] 
        row_font = ("Trebuchet MS", 13, "bold")

        for movie in movies_data:
            row = ctk.CTkFrame(list_container, fg_color="transparent")
            row.pack(fill="x", padx=40, pady=12)
            row.configure(cursor="hand2")

            lbl_title = ctk.CTkLabel(row, text=movie.get("title", "Unknown"), font=row_font, text_color=COL_FILM, width=240, anchor="w", justify="left", wraplength=230)
            lbl_title.grid(row=0, column=0, sticky="nw", padx=(0, 15))
            
            bersih_tahun = str(movie.get("year", "N/A")).replace("1'", "")
            lbl_year = ctk.CTkLabel(row, text=bersih_tahun, font=row_font, text_color=COL_YEAR, width=60, anchor="w")
            lbl_year.grid(row=0, column=1, sticky="nw", padx=(0, 15))
            
            lbl_mood = ctk.CTkLabel(row, text=movie.get("genre", "N/A"), font=row_font, text_color=COL_MOOD, width=160, anchor="w", justify="left", wraplength=150)
            lbl_mood.grid(row=0, column=2, sticky="nw", padx=(0, 15))
            
            raw_syn = movie.get("description", movie.get("synopsis", "No synopsis available."))
            if len(raw_syn) > 130:
                raw_syn = raw_syn[:127] + "..."
                
            lbl_synopsis = ctk.CTkLabel(row, text=raw_syn, font=("Trebuchet MS", 12), text_color=COL_SYNOPSIS, justify="right", wraplength=380)
            lbl_synopsis.grid(row=0, column=3, sticky="ne")
            
            row.columnconfigure(3, weight=1)

            klik_detail = lambda e, m=movie: self.app.show_page("moviedetail", m)
            row.bind("<Button-1>", klik_detail)
            lbl_title.bind("<Button-1>", klik_detail)
            lbl_year.bind("<Button-1>", klik_detail)
            lbl_mood.bind("<Button-1>", klik_detail)
            lbl_synopsis.bind("<Button-1>", klik_detail)

            ctk.CTkFrame(list_container, fg_color="#DDDDDD", height=1).pack(fill="x", padx=40, pady=5)

    def _build_tagline(self):
        families = tkfont.families()
        tagline_font = ("Instrument Serif", 24, "italic") if "Instrument Serif" in families else ("Georgia", 24, "italic")
        tl = ctk.CTkFrame(self.body, fg_color=BG_MAIN, height=100)
        tl.pack(fill="x")
        tl.pack_propagate(False)
        ctk.CTkLabel(tl, text="a passionate enthusiast — a passionate enthusiast — a passionate", font=tagline_font, text_color=TEXT_WHITE).pack(expand=True)

    def _build_watchlist_banner(self):
        wrapper = ctk.CTkFrame(self.body, fg_color=BG_MAIN)
        wrapper.pack(fill="x", padx=20, pady=12)
        banner = ctk.CTkFrame(wrapper, fg_color="#FF8C00", corner_radius=0, height=200) 
        banner.pack(fill="x")
        banner.pack_propagate(False)

        content = ctk.CTkFrame(banner, fg_color="transparent")
        content.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(content, text="Don't forget your watchlist!", font=("Georgia", 36, "italic"), text_color="#111111").pack(pady=(0,5))
        ctk.CTkLabel(content, text="Update it and discover what to watch next.", font=("Trebuchet MS", 14, "bold"), text_color="#222222").pack(pady=(0, 20))
        ctk.CTkButton(content, text="Go to Watchlist", fg_color="#111111", hover_color="#333333", 
                    text_color=TEXT_WHITE, font=("Trebuchet MS", 12, "bold"), width=160, height=40, 
                    corner_radius=0, command=lambda: self.app.show_page("watchlist")).pack()

    def _build_footer(self):
        footer = ctk.CTkFrame(self.body, fg_color="#0A0A0A", corner_radius=0, height=170)
        footer.pack(fill="x", pady=(20, 0))
        footer.pack_propagate(False)

        ctk.CTkLabel(footer, text="Cinephile", font=("Helvetica", 60, "bold"), text_color=TEXT_WHITE).place(relx=0.04, rely=0.5, anchor="w")
        ctk.CTkLabel(footer, text="©2026 Movie Archive\nWords, images, and signals from the edge", font=("Trebuchet MS", 10), text_color=TEXT_GRAY, justify="right").place(relx=0.96, rely=0.8, anchor="e")