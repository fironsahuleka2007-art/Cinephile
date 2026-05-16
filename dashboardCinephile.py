import customtkinter as ctk
from PIL import Image, ImageTk, ImageOps, ImageDraw
import os
import json
import random
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

# -- WARNA TETAP SAMA --
BG_MAIN    = "#1A1A1A"
BG_NAV     = "#111111"
BG_TAB     = "#2E2E2E"
BG_LIGHT   = "#F4F4F4"
ACCENT     = "#E53935"
TEXT_WHITE = "#FFFFFF"
TEXT_DARK  = "#111111"
COL_FILM     = "#7A1C1C"
COL_YEAR     = "#111111"
COL_MOOD     = "#2A368F"
COL_SYNOPSIS = "#8A4B1A"
COL_PLATFORM = "#006400"

class DashboardPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=BG_MAIN, corner_radius=0)
        self.app = app
        self._load_user_data()
        self.hero_images = ["hero1.jpeg", "hero2.jpeg", "hero3.jpeg"]
        self.h_idx = 0
        self._build_ui()

    def _load_user_data(self):
        self.username = "Guest"
        self.user_data = {}
        try:
            if os.path.exists("session.json"):
                with open("session.json", "r") as f:
                    self.username = json.load(f).get("active_user", "Guest")
            if os.path.exists("users.json"):
                with open("users.json", "r") as f:
                    u_db = json.load(f)
                    self.user_data = u_db.get(self.username, {})
        except: pass

    def _get_round_avatar(self, image_path, size=(40, 40)):
        try:
            mask = Image.new('L', size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + size, fill=255)
            img = Image.open(image_path).convert("RGBA")
            img = ImageOps.fit(img, size, centering=(0.5, 0.5))
            img.putalpha(mask)
            return ctk.CTkImage(img, size=size)
        except: return None

    def _build_ui(self):
        self._build_nav()
        self.body = ctk.CTkScrollableFrame(self, fg_color=BG_MAIN, scrollbar_button_color="#444", corner_radius=0)
        self.body.pack(fill="both", expand=True)
        self._build_hero()              
        self._build_insights_section()  
        self._build_trending_now()      
        self._build_top_10_list()       
        self._build_tagline_section()   
        self._build_watchlist_banner()  
        self._build_footer()    
        self._show_scroll_notification()        
        self.drop_box = ctk.CTkFrame(self, fg_color="#1E1E1E", border_color="#444", border_width=1, corner_radius=10, width=280)

    def _build_nav(self):
        self.nav = ctk.CTkFrame(self, fg_color=BG_NAV, corner_radius=0, height=75)
        self.nav.pack(fill="x", side="top")
        self.nav.pack_propagate(False)

        # Frame Profil
        self.prof = ctk.CTkFrame(self.nav, fg_color="transparent", cursor="hand2")
        self.prof.pack(side="left", padx=25)

        avatar_path = self.user_data.get("avatar_path", "")
        if avatar_path and os.path.exists(avatar_path):
            img_round = self._get_round_avatar(avatar_path)
            self.p_img = ctk.CTkLabel(self.prof, image=img_round, text="")
        else:
            self.p_img = ctk.CTkLabel(self.prof, text="👤", font=("Arial", 24), text_color="white")
        
        self.p_img.pack(side="left")
        
        self.p_name = ctk.CTkLabel(self.prof, text=f"  {self.username}", 
                                   font=("Trebuchet MS", 15, "bold"), text_color="white")
        self.p_name.pack(side="left")

        # --- FIX LOGIC DISINI ---
        # Buat fungsi perantara
        def go_to_profile(e=None):
            self.app.show_page("profile")

        # Bind klik ke Frame, Label Foto, DAN Label Nama
        self.prof.bind("<Button-1>", go_to_profile)
        self.p_img.bind("<Button-1>", go_to_profile)
        self.p_name.bind("<Button-1>", go_to_profile)
        # ------------------------

        # Navigation Pills
        pill = ctk.CTkFrame(self.nav, fg_color=BG_TAB, corner_radius=25, height=42)
        pill.place(relx=0.5, rely=0.5, anchor="center")
        
        menu_items = [
            ("Home", None), 
            ("Genre Analyze", "genreanalyze"), 
            ("Movie Table", "movietable"), 
            ("Watchlist", "watchlist")
        ]

        for txt, pg in menu_items:
            btn = ctk.CTkButton(pill, text=txt, width=95, height=34, 
                                fg_color=ACCENT if pg is None else "transparent", 
                                corner_radius=20, font=("Trebuchet MS", 12, "bold"),
                                command=lambda p=pg: self.app.show_page(p) if p else None)
            btn.pack(side="left", padx=4, pady=4)

        # Search Bar
        self.search_cont = ctk.CTkFrame(self.nav, fg_color="transparent")
        self.search_cont.pack(side="right", padx=25)
        
        self.entry_s = ctk.CTkEntry(self.search_cont, placeholder_text="Search movie...", 
                                    width=200, height=35, fg_color="#222", 
                                    border_color="#444", corner_radius=8)
        self.entry_s.pack(side="left", padx=(0, 5))
        self.entry_s.bind("<KeyRelease>", self._on_search_typing) 
        
        self.btn_s = ctk.CTkButton(self.search_cont, text="🔍", width=45, height=35, 
                                   fg_color=ACCENT, corner_radius=8, 
                                   command=lambda: self.app.handle_local_search(self.entry_s.get()))
        self.btn_s.pack(side="left")

    def _on_search_typing(self, event):
        query = self.entry_s.get().lower().strip()
        if not query:
            self.drop_box.place_forget()
            return
        all_movies = getattr(self.app, "movie_list", [])
        matches = [m for m in all_movies if query in m.get("title", "").lower()][:5]
        for w in self.drop_box.winfo_children(): w.destroy()
        if matches:
            self.drop_box.place(relx=1.0, x=-330, y=75) 
            self.drop_box.lift()
            for m in matches:
                item_f = ctk.CTkFrame(self.drop_box, fg_color="transparent", cursor="hand2")
                item_f.pack(fill="x", padx=5, pady=2)
                p_path = m.get("poster_local", "")
                if p_path and os.path.exists(p_path):
                    try:
                        img_s = ctk.CTkImage(Image.open(p_path), size=(30, 45))
                        ctk.CTkLabel(item_f, image=img_s, text="").pack(side="left", padx=5)
                    except: pass
                ctk.CTkLabel(item_f, text=m.get("title", "Unknown"), font=("Trebuchet MS", 12), 
                             text_color="white", anchor="w").pack(side="left", fill="x")
                item_f.bind("<Button-1>", lambda e, item=m: self._go_to_detail(item))
        else: self.drop_box.place_forget()

    def _go_to_detail(self, movie):
        self.drop_box.place_forget()
        self.app.show_page("moviedetail", data=movie)

    def _build_hero(self):
        self.hero_frame = ctk.CTkFrame(self.body, fg_color="#222", corner_radius=20, height=400)
        self.hero_frame.pack(fill="x", padx=30, pady=(20, 0))
        self.hero_frame.pack_propagate(False)
        self.hero_label = ctk.CTkLabel(self.hero_frame, text="")
        self.hero_label.pack(expand=True, fill="both")
        self._rotate_hero()

    def _rotate_hero(self):
        if not self.winfo_exists(): return
        img_n = self.hero_images[self.h_idx]
        p = os.path.join(os.path.dirname(__file__), "assets", "heroes", img_n)
        if not os.path.exists(p): p = img_n
        if os.path.exists(p):
            try:
                raw = Image.open(p)
                fitted = ImageOps.fit(raw, (1300, 400), method=Image.Resampling.LANCZOS)
                self.h_ctk = ctk.CTkImage(fitted, size=(1300, 400))
                self.hero_label.configure(image=self.h_ctk)
                if hasattr(self, 'tag_bg_label'):
                    slogan_raw = ImageOps.fit(raw, (1300, 300))
                    overlay = Image.new('RGBA', slogan_raw.size, (0,0,0,150))
                    slogan_final = Image.alpha_composite(slogan_raw.convert('RGBA'), overlay)
                    self.tag_ctk = ctk.CTkImage(slogan_final, size=(1300, 300))
                    self.tag_bg_label.configure(image=self.tag_ctk)
            except: pass
        self.h_idx = (self.h_idx + 1) % len(self.hero_images)
        self.after(5000, self._rotate_hero)

    # --- BAGIAN YANG DI FIX (TABEL) ---
    def _build_top_10_list(self):
        # Container utama diperlebar
        cont = ctk.CTkFrame(self.body, fg_color="#F8F9FA", corner_radius=20)
        cont.pack(fill="x", padx=30, pady=20)
        
        ctk.CTkLabel(cont, text="Top 10 Movies", font=("Helvetica", 32, "bold"), 
                     text_color="#1A1A1A").pack(anchor="w", padx=40, pady=(25, 15))

        # --- HEADER TABEL (DIPERLEBAR BIAR SIMETRIS) ---
        h_frame = ctk.CTkFrame(cont, fg_color="transparent")
        h_frame.pack(fill="x", padx=40, pady=(0, 10))
        
        # Penyesuaian Lebar Baru (Total lebih lebar agar memenuhi layar)
        w_poster = 80
        w_title = 280  # Ditambah
        w_year = 90
        w_mood = 150   # Ditambah
        w_platform = 200 # Ditambah
        w_synopsis = 500 # Diperlebar maksimal

        headers = [
            ("", w_poster), ("Film", w_title), ("Year", w_year), 
            ("Mood", w_mood), ("Platform", w_platform), ("Synopsis", w_synopsis)
        ]

        for text, width in headers:
            ctk.CTkLabel(h_frame, text=text, font=("Trebuchet MS", 14, "bold"), 
                         text_color="#555", anchor="w", width=width).pack(side="left")

        # --- ISI TABEL ---
        movies = getattr(self.app, "movie_list", [])[:10]
        for m in movies:
            # Baris utama
            row = ctk.CTkFrame(cont, fg_color="transparent", cursor="hand2")
            row.pack(fill="x", padx=40, pady=12)
            
            # Fungsi klik untuk satu baris penuh
            click_cmd = lambda e, data=m: self._go_to_detail(data)
            row.bind("<Button-1>", click_cmd)

            # 1. Poster
            p_lbl = ctk.CTkLabel(row, text="", width=w_poster)
            p_path = m.get("poster_local", "")
            if p_path and os.path.exists(p_path):
                try: 
                    img = ctk.CTkImage(Image.open(p_path), size=(50, 75))
                    p_lbl.configure(image=img)
                except: pass
            p_lbl.pack(side="left")
            p_lbl.bind("<Button-1>", click_cmd)

            # 2. Judul Film
            t_lbl = ctk.CTkLabel(row, text=m.get("title", "N/A"), width=w_title, anchor="w",
                                 font=("Trebuchet MS", 15, "bold"), text_color="#800000", 
                                 wraplength=260, justify="left")
            t_lbl.pack(side="left")
            t_lbl.bind("<Button-1>", click_cmd)

            # 3. Year
            y_lbl = ctk.CTkLabel(row, text=str(m.get("year", "N/A")), width=w_year, anchor="w",
                                 font=("Trebuchet MS", 14, "bold"), text_color="#1A1A1A")
            y_lbl.pack(side="left")
            y_lbl.bind("<Button-1>", click_cmd)

            # 4. Mood
            genre = m.get("genre", "N/A").split(',')[0]
            g_lbl = ctk.CTkLabel(row, text=genre, width=w_mood, anchor="w",
                                 font=("Trebuchet MS", 14, "bold"), text_color="#2A52BE")
            g_lbl.pack(side="left")
            g_lbl.bind("<Button-1>", click_cmd)
            
            # 5. Platform (Dinamis dari platform_string)
            raw_plat = m.get("platform_string", "N/A")
            display_plat = raw_plat.split(',')[0].strip() if raw_plat else "N/A"
            pl_lbl = ctk.CTkLabel(row, text=f"📺 {display_plat}", width=w_platform, anchor="w",
                                  font=("Trebuchet MS", 13, "bold"), text_color="#2D5A27")
            pl_lbl.pack(side="left")
            pl_lbl.bind("<Button-1>", click_cmd)
            
            # 6. Synopsis
            syn = m.get("description", "No synopsis available.")
            display_syn = (syn[:180] + "..") if len(syn) > 180 else syn
            s_lbl = ctk.CTkLabel(row, text=display_syn, width=w_synopsis, anchor="w",
                                font=("Trebuchet MS", 12), text_color="#444", 
                                wraplength=480, justify="left")
            s_lbl.pack(side="left")
            s_lbl.bind("<Button-1>", click_cmd)

            # Garis Pemisah
            line = ctk.CTkFrame(cont, fg_color="#E0E0E0", height=1)
            line.pack(fill="x", padx=40)

    # --- SISA FUNGSI TETAP ---
    def _build_tagline_section(self):
        self.tagline_frame = ctk.CTkFrame(self.body, fg_color="#000", corner_radius=20, height=300)
        self.tagline_frame.pack(fill="x", padx=30, pady=10)
        self.tagline_frame.pack_propagate(False)
        self.tag_bg_label = ctk.CTkLabel(self.tagline_frame, text="")
        self.tag_bg_label.place(relwidth=1, relheight=1)
        ctk.CTkLabel(self.tagline_frame, text="\"Every story has a beginning.\"", 
                    font=("Georgia", 40, "bold", "italic"), text_color="white").place(relx=0.5, rely=0.5, anchor="center")

    def _build_insights_section(self):
        ins_frame = ctk.CTkFrame(self.body, fg_color="transparent")
        ins_frame.pack(fill="x", padx=40, pady=(30, 10))
        ctk.CTkLabel(ins_frame, text="Cinephile Insights", font=("Helvetica", 24, "bold"), text_color="white").pack(anchor="w")
        cards_f = ctk.CTkFrame(ins_frame, fg_color="transparent")
        cards_f.pack(fill="x", pady=15)
        stats = [("Total Movies", "250 Titles", "🎬", "#2d5a27"), ("Trending Genre", "Action/Sci-Fi", "🔥", "#2A368F"), ("Global Rating", "4.9/5.0", "⭐", "#8A4B1A")]
        for tit, val, ico, col in stats:
            card = ctk.CTkFrame(cards_f, fg_color=col, corner_radius=15, height=100)
            card.pack(side="left", fill="x", expand=True, padx=10)
            card.pack_propagate(False)
            ctk.CTkLabel(card, text=ico, font=("Arial", 35)).pack(side="left", padx=20)
            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", fill="y", pady=20)
            ctk.CTkLabel(info, text=tit, font=("Trebuchet MS", 13), text_color="#DDD").pack(anchor="w")
            ctk.CTkLabel(info, text=val, font=("Arial Black", 20, "bold"), text_color="white").pack(anchor="w")

    def _build_trending_now(self):
        ctk.CTkLabel(self.body, text="Trending Now", font=("Helvetica", 24, "bold"), 
                     text_color="white").pack(anchor="w", padx=40, pady=(20, 5))
        
        # Frame scroll horizontal
        self.scroll_h = ctk.CTkScrollableFrame(self.body, orientation="horizontal", height=280, fg_color="transparent")
        self.scroll_h.pack(fill="x", padx=30)
        
        movies = getattr(self.app, "movie_list", [])
        if not movies: return
        
        # --- FIX 1: BATASI JUMLAH FILM ---
        # Jangan masukin semua film. Ambil 15 film aja, lalu duplikasi 4x (Total 60 item).
        # Ini udah cukup banget buat bikin efek looping tanpa bikin RAM jebol.
        base_pool = movies[:15] 
        extended_pool = base_pool * 4 
        
        # --- FIX 2: BIKIN IMAGE CACHE ---
        # Biar Python nggak usah Image.open() gambar yang sama berulang kali
        image_cache = {}
        
        for m in extended_pool:
            card = ctk.CTkFrame(self.scroll_h, fg_color="transparent", width=160, cursor="hand2")
            card.pack(side="left", padx=10)
            
            click_cmd = lambda e, d=m: self._go_to_detail(d)
            
            # Poster dengan Cache System
            p_path = m.get("poster_local", "")
            img_label = ctk.CTkLabel(card, text="", width=150, height=220)
            
            if p_path and os.path.exists(p_path):
                # Kalau gambar belum ada di cache, kita buka dan simpan
                if p_path not in image_cache:
                    try:
                        raw_img = Image.open(p_path)
                        # Simpan hasil convert ke dalam dictionary
                        image_cache[p_path] = ctk.CTkImage(raw_img, size=(150, 220))
                    except: pass
                
                # Panggil gambar langsung dari RAM (Cache)
                if p_path in image_cache:
                    img_label.configure(image=image_cache[p_path])
            
            img_label.pack()
            
            # Judul
            t_text = m.get("title", "Unknown")
            if len(t_text) > 18: t_text = t_text[:15] + "..."
            ctk.CTkLabel(card, text=t_text, font=("Trebuchet MS", 12, "bold"), text_color="white").pack(pady=8)
            
            # Binding klik supaya interaktif
            for w in [card, img_label]: 
                w.bind("<Button-1>", click_cmd)

        # Inisialisasi posisi scroll
        self._current_scroll_pos = 0.0
        self._auto_scroll_trending()

    def _auto_scroll_trending(self):
        # Proteksi jika widget sudah dihancurkan
        if not hasattr(self, "scroll_h") or not self.scroll_h.winfo_exists():
            return
        
        # Tambah kecepatan dikit karena FPS kita turunkan biar CPU nggak kerja keras
        self._current_scroll_pos += 0.0003  
        
        if self._current_scroll_pos >= 1.0:
            self._current_scroll_pos = 0.0
            
        try:
            self.scroll_h._parent_canvas.xview_moveto(self._current_scroll_pos)
        except: pass
        
        # --- FIX 3: KURANGI BEBAN CPU ---
        # 20ms itu terlalu ngebut buat Tkinter. Kita ganti ke 40ms (setara ~25 FPS). 
        # Udah cukup smooth dan aman dari nge-lag.
        self.after(40, self._auto_scroll_trending)
    
    def _show_scroll_notification(self):
        # Desain lebih estetik: warna abu-abu gelap, tanpa border tebal, bentuk kapsul memanjang
        self.notif_frame = ctk.CTkFrame(self, fg_color="#2A2A2A", corner_radius=20, border_width=1, border_color="#333333")
        
        # Mulai dari rely=1.1 (ngumpet di luar layar bawah)
        self._current_rely = 1.1 
        self.notif_frame.place(relx=0.5, rely=self._current_rely, anchor="center")
        
        # Teks lebih kalem dan elegan
        lbl = ctk.CTkLabel(self.notif_frame, text="↓  Scroll down to explore more", 
                           font=("Trebuchet MS", 13, "bold"), text_color="#E0E0E0")
        lbl.pack(padx=30, pady=10)
        
        # Jalankan animasi naik
        self._target_rely_up = 0.92  # Posisi estetik di tengah-bawah layar
        self._slide_up()
        
        # Set timer 5 detik untuk mulai animasi turun
        self.after(5000, self._start_slide_down)

    def _slide_up(self):
        if not hasattr(self, "notif_frame") or not self.notif_frame.winfo_exists(): return
        
        if self._current_rely > self._target_rely_up:
            self._current_rely -= 0.008  # Kecepatan naik
            self.notif_frame.place(relx=0.5, rely=self._current_rely, anchor="center")
            self.after(15, self._slide_up) # Loop animasi setiap 15ms

    def _start_slide_down(self):
        self._target_rely_down = 1.1
        self._slide_down()

    def _slide_down(self):
        if not hasattr(self, "notif_frame") or not self.notif_frame.winfo_exists(): return
        
        if self._current_rely < self._target_rely_down:
            self._current_rely += 0.008  # Kecepatan turun
            self.notif_frame.place(relx=0.5, rely=self._current_rely, anchor="center")
            self.after(15, self._slide_down)
        else:
            self.notif_frame.destroy() # Hancurkan widget kalau udah di luar layar

    def _build_watchlist_banner(self):
        banner = ctk.CTkFrame(self.body, fg_color="#FF8C00", corner_radius=20, height=140)
        banner.pack(fill="x", padx=30, pady=(20, 30))
        banner.pack_propagate(False)
        ctx = ctk.CTkFrame(banner, fg_color="transparent")
        ctx.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(ctx, text="Manage your watchlist now!", font=("Georgia", 28, "bold", "italic"), text_color="#111").pack()
        ctk.CTkButton(ctx, text="GO TO WATCHLIST", fg_color="#111", text_color="white", font=("Trebuchet MS", 12, "bold"), 
                    width=200, height=40, corner_radius=10, command=lambda: self.app.show_page("watchlist")).pack(pady=15)

    def _build_footer(self):
        footer = ctk.CTkFrame(self.body, fg_color="#0A0A0A", height=200)
        footer.pack(fill="x")
        ctk.CTkLabel(footer, text="Cinephile Archive", font=("Helvetica", 22, "bold"), text_color="white").place(relx=0.5, rely=0.3, anchor="center")
        ctk.CTkLabel(footer, text="Created by Kelompok D5", font=("Trebuchet MS", 14, "bold"), text_color=ACCENT).place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(footer, text="Your Ultimate Cinematic Database © 2026", font=("Trebuchet MS", 11), text_color="gray").place(relx=0.5, rely=0.7, anchor="center")