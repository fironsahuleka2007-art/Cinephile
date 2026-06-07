import customtkinter as ctk
from PIL import Image, ImageTk, ImageOps, ImageDraw, ImageFilter, ImageEnhance
import os
import json
import random
import math
import threading
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

# ── Warna ──────────────────────────────────────────────────────────────────
BG_MAIN    = "#1A1A1A"
BG_NAV     = "#111111"
BG_TAB     = "#2E2E2E"
BG_LIGHT   = "#F4F4F4"
ACCENT     = "#7A1C1C"
TEXT_WHITE = "#FFFFFF"
TEXT_DARK  = "#111111"
COL_FILM     = "#8d2827"
COL_YEAR     = "#111111"
COL_MOOD     = "#2A368F"
COL_SYNOPSIS = "#8A4B1A"
COL_PLATFORM = "#006400"


# ══════════════════════════════════════════════════════ HERO PARALLAX FRAME
class HeroParallaxFrame(ctk.CTkFrame):

    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color="#111111", corner_radius=20,
                         height=420, **kwargs)
        self.app = app
        self._mx = 0.0
        self._my = 0.0
        self._target_mx = 0.0
        self._target_my = 0.0

        self._images       = []
        self._poster_items = []
        self._featured_movie = None

        self._movie_pool   = []
        self._current_idx  = 0
        self._dot_widgets  = []
        self._swipe_start_x = None
        self._auto_slide_id = None

        self._build_layers()
        self._load_hero_posters()

        self.bind("<Motion>",         self._on_motion)
        self.bind("<ButtonPress-1>",  self._on_press)
        self.bind("<ButtonRelease-1>",self._on_release)
        self._parallax_loop()

    # ---------------------------------------------------------------- LAYERS
    def _build_layers(self):
        self.bg_canvas = ctk.CTkCanvas(self, bg="#0A0A0A", highlightthickness=0)
        self.bg_canvas.place(relwidth=1, relheight=1)

        self.overlay = ctk.CTkFrame(self, fg_color="transparent", corner_radius=20)
        self.overlay.place(relwidth=1, relheight=1)
        self.ov_canvas = ctk.CTkCanvas(self.overlay, bg="#0A0A0A",
                                        highlightthickness=0)
        self.ov_canvas.place(relwidth=1, relheight=1)

        self.content = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.content.place(relwidth=1, relheight=1)

        self._build_content_layer()

        for widget in [self.bg_canvas, self.overlay, self.ov_canvas, self.content]:
            widget.bind("<Motion>",         self._on_motion)
            widget.bind("<ButtonPress-1>",  self._on_press)
            widget.bind("<ButtonRelease-1>",self._on_release)

    def _build_content_layer(self):
        c = self.content

        self.btn_prev = ctk.CTkButton(
            c, text="❮", width=42, height=42,
            fg_color="#222222", hover_color="#7A1C1C",
            text_color="white", font=("Arial", 18, "bold"),
            corner_radius=21, command=self._prev_movie
        )
        self.btn_prev.place(relx=0.01, rely=0.72, anchor="w")

        self.btn_next = ctk.CTkButton(
            c, text="❯", width=42, height=42,
            fg_color="#222222", hover_color="#7A1C1C",
            text_color="white", font=("Arial", 18, "bold"),
            corner_radius=21, command=self._next_movie
        )
        self.btn_next.place(relx=0.99, rely=0.72, anchor="e")

        main = ctk.CTkFrame(c, fg_color="transparent")
        main.place(x=110, rely=0.5, anchor="w")

        feat_frame = ctk.CTkFrame(main, fg_color="#7A1C1C", corner_radius=12)
        feat_frame.pack(anchor="w", pady=(0, 14))
        ctk.CTkLabel(feat_frame, text="★  Featured tonight",
                     font=("Trebuchet MS", 12, "bold"),
                     text_color="white").pack(padx=12, pady=6)

        self.hero_title_label = ctk.CTkLabel(
            main, text="Cinephile Archive",
            font=("Georgia", 40, "bold"), text_color="white",
            wraplength=560, justify="left", anchor="w"
        )
        self.hero_title_label.pack(anchor="w", pady=(0, 10))

        self.meta_row_frame = ctk.CTkFrame(main, fg_color="transparent")
        self.meta_row_frame.pack(anchor="w", pady=(0, 14))

        self._genre_badges = []
        for tag in ["Genre", "Year", "Duration"]:
            badge_f = ctk.CTkFrame(self.meta_row_frame, fg_color="#2A2A2A",
                                   corner_radius=15, border_width=1,
                                   border_color="#555555")
            badge_f.pack(side="left", padx=(0, 8))
            lbl = ctk.CTkLabel(badge_f, text=tag,
                               font=("Trebuchet MS", 13, "bold"),
                               text_color="white")
            lbl.pack(padx=14, pady=5)
            self._genre_badges.append((badge_f, lbl))

        self.rating_label = ctk.CTkLabel(
            self.meta_row_frame, text="★ –",
            font=("Trebuchet MS", 15, "bold"), text_color="#F5C518"
        )
        self.rating_label.pack(side="left", padx=(8, 0))

        self.hero_synopsis_label = ctk.CTkLabel(
            main,
            text="Your ultimate cinematic database.\nDiscover, track, and explore movies.",
            font=("Trebuchet MS", 13), text_color="#BBBBBB",
            justify="left", anchor="w", wraplength=440
        )
        self.hero_synopsis_label.pack(anchor="w", pady=(0, 20))

        btn_row = ctk.CTkFrame(main, fg_color="transparent")
        btn_row.pack(anchor="w")

        btn_style = dict(
            corner_radius=20, height=42, width=155,
            fg_color="#1A1A1A", border_width=2, border_color="#AAAAAA",
            font=("Trebuchet MS", 13, "bold"), text_color="white",
            hover_color="#2E2E2E"
        )

        ctk.CTkButton(btn_row, text="+  Watchlist", **btn_style,
                      command=lambda: self.app.show_page("watchlist")
                      ).pack(side="left", padx=(0, 10))

        self.detail_btn = ctk.CTkButton(btn_row, text="ℹ  Details", **btn_style,
                                        command=self._go_to_detail)
        self.detail_btn.pack(side="left")

        self.hero_poster_frame = ctk.CTkFrame(c, fg_color="transparent")
        self.hero_poster_frame.place(relx=0.93, rely=0.5, anchor="e")

        shadow = ctk.CTkFrame(self.hero_poster_frame, fg_color="#2A2A2A",
                              corner_radius=14, width=194, height=284)
        shadow.pack(padx=4, pady=4)
        shadow.pack_propagate(False)

        self.hero_poster_label = ctk.CTkLabel(
            shadow, text="🎬", font=("Arial", 40), text_color="#555555",
            width=186, height=276
        )
        self.hero_poster_label.place(relx=0.5, rely=0.5, anchor="center")

        self._dots_frame = ctk.CTkFrame(c, fg_color="transparent")
        self._dots_frame.place(relx=0.5, rely=1.0, anchor="s", y=-15)

    def _go_to_detail(self):
        if self._featured_movie:
            self.app.show_page("moviedetail", data=self._featured_movie)

    # --------------------------------------------------------------- DOTS
    def _build_dots(self):
        for w in self._dots_frame.winfo_children():
            w.destroy()
        self._dot_widgets = []
        for i in range(len(self._movie_pool)):
            color = "#7A1C1C" if i == self._current_idx else "#555555"
            dot = ctk.CTkFrame(self._dots_frame, fg_color=color,
                               width=26, height=6, corner_radius=3)
            dot.pack(side="left", padx=4)
            dot.pack_propagate(False)
            self._dot_widgets.append(dot)

    def _update_dots(self):
        for i, dot in enumerate(self._dot_widgets):
            dot.configure(fg_color="#AD2B28" if i == self._current_idx else "#555555")

    # ----------------------------------------------------------- NAVIGATION
    def _next_movie(self):
        if not self._movie_pool:
            return
        self._current_idx = (self._current_idx + 1) % len(self._movie_pool)
        self._show_movie(self._current_idx)
        self._reset_auto_slide()

    def _prev_movie(self):
        if not self._movie_pool:
            return
        self._current_idx = (self._current_idx - 1) % len(self._movie_pool)
        self._show_movie(self._current_idx)
        self._reset_auto_slide()

    def _show_movie(self, idx):
        if not self._movie_pool:
            return
        self._update_hero_info(self._movie_pool[idx])
        self._update_dots()

    def _start_auto_slide(self, interval_ms=6000):
        self._stop_auto_slide()
        self._auto_slide_id = self.after(interval_ms, self._auto_slide_tick)

    def _auto_slide_tick(self):
        if not self.winfo_exists():
            return
        self._next_movie()
        self._auto_slide_id = self.after(6000, self._auto_slide_tick)

    def _stop_auto_slide(self):
        if self._auto_slide_id:
            try:
                self.after_cancel(self._auto_slide_id)
            except Exception:
                pass
            self._auto_slide_id = None

    def _reset_auto_slide(self):
        self._start_auto_slide()

    # --------------------------------------------------------------- SWIPE
    def _on_press(self, event):
        self._swipe_start_x = event.x_root

    def _on_release(self, event):
        if self._swipe_start_x is None:
            return
        delta = event.x_root - self._swipe_start_x
        self._swipe_start_x = None
        if delta < -50:
            self._next_movie()
        elif delta > 50:
            self._prev_movie()

    # -------------------------------------------------------- HERO INFO UPDATE
    def _update_hero_info(self, movie):
        self._featured_movie = movie

        title = movie.get("title", "Cinephile Archive")
        font_size = 30 if len(title) > 30 else (36 if len(title) > 20 else 40)
        self.hero_title_label.configure(text=title, font=("Georgia", font_size, "bold"))

        genres   = [g.strip() for g in movie.get("genre", "").split(",")][:2]
        year     = str(movie.get("year", ""))
        duration = movie.get("duration", movie.get("runtime", "–"))
        tags     = genres + [year, str(duration)]
        for i, (badge_f, lbl) in enumerate(self._genre_badges):
            if i < len(tags) and tags[i]:
                lbl.configure(text=tags[i])
                badge_f.pack(side="left", padx=(0, 8))
            else:
                badge_f.pack_forget()

        rating = movie.get("rating", movie.get("imdb_rating", ""))
        self.rating_label.configure(text=f"★ {rating}" if rating else "★ –")

        syn = movie.get("description", movie.get("synopsis", ""))
        if len(syn) > 180:
            syn = syn[:177] + "..."
        self.hero_synopsis_label.configure(text=syn if syn else "No synopsis available.")

        p_path = movie.get("poster_local", "")
        if p_path and os.path.exists(p_path):
            try:
                raw = Image.open(p_path).convert("RGB")
                ctk_img = ctk.CTkImage(raw, size=(186, 276))
                self._hero_poster_img = ctk_img
                self.hero_poster_label.configure(image=ctk_img, text="")
            except Exception:
                pass

    # ---------------------------------------------------- POSTER BACKGROUND LOADER
    def _load_hero_posters(self):
        movies = getattr(self.app, "movie_list", [])[:10]
        pool   = [m for m in movies
                  if m.get("poster_local") and os.path.exists(m["poster_local"])]
        selected = pool[:8]
        if not selected:
            self._load_fallback_hero()
            return
        t = threading.Thread(target=self._worker_load, args=(selected,), daemon=True)
        t.start()

    def _worker_load(self, selected):
        loaded = []
        for m in selected:
            try:
                img = Image.open(m["poster_local"]).convert("RGB")
                img = img.resize((320, 440), Image.LANCZOS)
                img = img.filter(ImageFilter.GaussianBlur(radius=3))
                img = ImageEnhance.Brightness(img).enhance(0.32)
                loaded.append((img, m))
            except Exception:
                pass
        if loaded:
            # ✅ FIX: jadwalkan di main thread via root window
            try:
                self.winfo_toplevel().after(0, lambda: self._place_poster_bg(loaded))
            except Exception:
                pass

    def _place_poster_bg(self, loaded_pairs):
        if not self.winfo_exists():
            return

        positions = [
            (-60, -30, 1.8), (230, -50, 1.5), (520, -20, 1.6),
            (800, -40, 1.4), (1050, 10, 1.7), (-20, 150, 1.3),
            (380, 180, 1.5), (720, 160, 1.4)
        ]

        for i, (pil_img, movie) in enumerate(loaded_pairs):
            if i >= len(positions):
                break
            bx, by, depth = positions[i]
            ctk_img = ctk.CTkImage(pil_img, size=(280, 400))
            self._images.append(ctk_img)
            lbl = ctk.CTkLabel(self.bg_canvas, image=ctk_img, text="")
            lbl.place(x=bx, y=by)
            self._poster_items.append({"label": lbl, "base_x": bx,
                                       "base_y": by, "depth": depth})

        if loaded_pairs:
            self._movie_pool  = [pair[1] for pair in loaded_pairs]
            self._current_idx = 0
            self._build_dots()
            self._update_hero_info(self._movie_pool[0])
            self._start_auto_slide()

        self.overlay.lift()
        self.content.lift()
        if hasattr(self, "btn_prev"):
            self.btn_prev.lift()
            self.btn_next.lift()
            self._dots_frame.lift()

    def _load_fallback_hero(self):
        hero_paths = [
            os.path.join(os.path.dirname(__file__), "assets", "heroes", "hero1.jpeg"),
            "hero1.jpeg"
        ]
        for p in hero_paths:
            if os.path.exists(p):
                try:
                    img = Image.open(p)
                    img = ImageOps.fit(img, (1300, 420), Image.LANCZOS)
                    ctk_img = ctk.CTkImage(img, size=(1300, 420))
                    self._images.append(ctk_img)
                    lbl = ctk.CTkLabel(self.bg_canvas, image=ctk_img, text="")
                    lbl.place(x=0, y=0)
                    self.overlay.lift()
                    self.content.lift()
                except Exception:
                    pass
                break

    # ------------------------------------------------------------ PARALLAX
    def _on_motion(self, event):
        try:
            rx = event.x_root - self.winfo_rootx()
            ry = event.y_root - self.winfo_rooty()
            self._target_mx = rx
            self._target_my = ry
        except Exception:
            pass

    def _parallax_loop(self):
        if not self.winfo_exists():
            return
        self._mx += (self._target_mx - self._mx) * 0.07
        self._my += (self._target_my - self._my) * 0.07
        w  = self.winfo_width()  or 1100
        h  = self.winfo_height() or 420
        cx, cy = w / 2, h / 2
        ox = (self._mx - cx) / (cx or 1)
        oy = (self._my - cy) / (cy or 1)
        for item in self._poster_items:
            lbl = item["label"]
            if not lbl.winfo_exists():
                continue
            d = item["depth"]
            lbl.place(x=item["base_x"] + ox * 25 * d,
                      y=item["base_y"] + oy * 15 * d)
        self.after(25, self._parallax_loop)


# ═══════════════════════════════════════════════════════════ DASHBOARD PAGE
class DashboardPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=BG_MAIN, corner_radius=0)
        self.app = app
        self._load_user_data()
        self.hero_images = ["hero1.jpeg", "hero2.jpeg", "hero3.jpeg"]
        self.h_idx = 0
        self._build_ui()
        self.after(60, self._entrance_animation)

    # --------------------------------------------------------- USER DATA
    def _load_user_data(self):
        self.username = "Guest"
        self.user_data = {}
        try:
            if os.path.exists("session.json"):
                with open("session.json", "r") as f:
                    self.username = json.load(f).get("active_user", "Guest")
            if os.path.exists("users.json"):
                with open("users.json", "r") as f:
                    self.user_data = json.load(f).get(self.username, {})
        except Exception:
            pass

    def _get_round_avatar(self, image_path, size=(40, 40)):
        try:
            mask = Image.new('L', size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + size, fill=255)
            img = Image.open(image_path).convert("RGBA")
            img = ImageOps.fit(img, size, centering=(0.5, 0.5))
            img.putalpha(mask)
            return ctk.CTkImage(img, size=size)
        except Exception:
            return None

    # ------------------------------------------------------- ENTRANCE ANIMATION
    def _entrance_animation(self):
        if not self.winfo_exists():
            return
        self._slide_nav(step=0, total=12)

    def _slide_nav(self, step, total):
        if not self.winfo_exists():
            return
        progress = step / total
        eased    = 1 - (1 - progress) ** 2
        offset_y = int(-75 * (1 - eased))
        try:
            self.nav.place(x=0, y=offset_y, relwidth=1.0, height=75)
        except Exception:
            pass
        if step < total:
            self.after(12, lambda: self._slide_nav(step + 1, total))
        else:
            try:
                self.nav.place_forget()
                self.nav.pack(fill="x", side="top")
            except Exception:
                pass

    # ------------------------------------------------------------ BUILD UI
    def _build_ui(self):
        self._build_nav()
        self.body = ctk.CTkScrollableFrame(
            self, fg_color=BG_MAIN,
            scrollbar_button_color="#444", corner_radius=0
        )
        self.body.pack(fill="both", expand=True)
        self._build_hero()
        self._build_insights_section()
        self._build_trending_now()
        self._build_top_10_list()
        self._build_tagline_section()
        self._build_watchlist_banner()
        self._build_footer()
        self._show_scroll_notification()

        self.drop_box = ctk.CTkFrame(
            self, fg_color="#1E1E1E",
            border_color="#444", border_width=1,
            corner_radius=10, width=280
        )

    # ------------------------------------------------------------- NAV BAR (PERFECTED)
    def _build_nav(self):
        # 1. Gunakan fg_color yang sama dengan background atau BG_NAV
        # Hilangkan border_width jika ada
        self.nav = ctk.CTkFrame(self, fg_color=BG_NAV, corner_radius=0, height=75, border_width=0)
        self.nav.pack(fill="x", side="top")
        self.nav.pack_propagate(False)

        # ── KIRI: Avatar + Username ──────────────────────────────────────
        left_frame = ctk.CTkFrame(self.nav, fg_color="transparent")
        left_frame.pack(side="left", padx=(20, 0))

        avatar_path = self.user_data.get("avatar_path", "")
        if avatar_path and os.path.exists(avatar_path):
            img_round = self._get_round_avatar(avatar_path)
            self.p_img = ctk.CTkLabel(left_frame, image=img_round, text="", cursor="hand2")
        else:
            self.p_img = ctk.CTkLabel(left_frame, text="👤",
                                      font=("Arial", 24), text_color="white", cursor="hand2")
        self.p_img.pack(side="left")

        self.p_name = ctk.CTkLabel(
            left_frame, text=f"  {self.username}",
            font=("Trebuchet MS", 15, "bold"), text_color="white", cursor="hand2"
        )
        self.p_name.pack(side="left")

        def go_to_profile(e=None):
            self.app.show_page("profile")

        self.p_img.bind("<Button-1>",  go_to_profile)
        self.p_name.bind("<Button-1>", go_to_profile)

        # ── KANAN: Search bar ────────────────────────────────────────────
        right_frame = ctk.CTkFrame(self.nav, fg_color="transparent")
        right_frame.pack(side="right", padx=(0, 20))

        self.entry_s = ctk.CTkEntry(
            right_frame,
            placeholder_text="🔍  Search movie...",
            width=210, height=38,
            fg_color="#222222", border_color="#333333", # Warna border lebih soft
            corner_radius=20,
            font=("Trebuchet MS", 12), text_color="white",
            border_width=1
        )
        self.entry_s.pack(side="left", padx=(0, 8))
        self.entry_s.bind("<KeyRelease>", self._on_search_typing)

        self.btn_s = ctk.CTkButton(
            right_frame, text="Search", width=80, height=38,
            fg_color=ACCENT, hover_color="#7A1C1C",
            corner_radius=20,
            font=("Trebuchet MS", 12, "bold"), text_color="white",
            command=lambda: (
                self.app.handle_local_search(self.entry_s.get())
                if hasattr(self.app, "handle_local_search") else None
            )
        )
        self.btn_s.pack(side="left")

        # ── TENGAH: Menu pill (SYMMETRICAL & COMPACT) ──────────
        menu_items = [
            ("Home",          None),
            ("Genre Analyze", "genreanalyze"),
            ("Movie Table",   "movietable"),
            ("Watchlist",     "watchlist"),
        ]
        
        # 1. Hapus width statis agar frame otomatis mengikuti isi
        pill = ctk.CTkFrame(
            self.nav, 
            fg_color=BG_TAB,      
            bg_color=BG_NAV,      
            corner_radius=25, 
            height=46,
            border_width=0
        )
        # 2. Pakai place tanpa width, biarkan otomatis
        pill.place(relx=0.5, rely=0.5, anchor="center")
        
        # 3. KUNCI: Jangan pakai pack_propagate(False) agar frame bisa menciut
        pill.pack_propagate(True) 

        for i, (txt, pg) in enumerate(menu_items):
            is_active = (txt == "Home")
            
            # Berikan padding kiri & kanan yang sama (10) agar simetris
            # Tombol pertama dan terakhir diberi jarak ekstra ke dinding lengkungan
            p_left = 15 if i == 0 else 5
            p_right = 15 if i == len(menu_items) - 1 else 5
            
            btn = ctk.CTkButton(
                pill, text=txt, 
                width=110, # Lebar tombol sedikit dikecilkan agar lebih rapat
                height=32,
                fg_color=ACCENT if is_active else "transparent",
                hover_color="#444444" if not is_active else "#902a2a",
                bg_color="transparent", 
                corner_radius=20,
                font=("Trebuchet MS", 12, "bold"),
                text_color="white",
                command=lambda p=pg: self.app.show_page(p) if p else None
            )
            btn.pack(side="left", padx=(p_left, p_right), pady=7)

    # ----------------------------------------------------- SEARCH DROPDOWN
    def _on_search_typing(self, event):
        query = self.entry_s.get().lower().strip()
        if not query:
            self.drop_box.place_forget()
            return
        all_movies = getattr(self.app, "movie_list", [])
        matches = [m for m in all_movies
                   if query in m.get("title", "").lower()][:5]
        for w in self.drop_box.winfo_children():
            w.destroy()
        if matches:
            self.drop_box.place(relx=1.0, x=-330, y=75)
            self.drop_box.lift()
            for m in matches:
                item_f = ctk.CTkFrame(self.drop_box, fg_color="transparent",
                                       cursor="hand2")
                item_f.pack(fill="x", padx=5, pady=2)
                p_path = m.get("poster_local", "")
                if p_path and os.path.exists(p_path):
                    try:
                        img_s = ctk.CTkImage(Image.open(p_path), size=(30, 45))
                        ctk.CTkLabel(item_f, image=img_s, text="").pack(
                            side="left", padx=5)
                    except Exception:
                        pass
                ctk.CTkLabel(
                    item_f, text=m.get("title", "Unknown"),
                    font=("Trebuchet MS", 12), text_color="white", anchor="w"
                ).pack(side="left", fill="x")
                item_f.bind("<Button-1>",
                            lambda e, item=m: self._go_to_detail(item))
        else:
            self.drop_box.place_forget()

    def _go_to_detail(self, movie):
        self.drop_box.place_forget()
        self.app.show_page("moviedetail", data=movie)

    # ------------------------------------------------------ HERO PARALLAX
    def _build_hero(self):
        self.hero_parallax = HeroParallaxFrame(self.body, self.app)
        self.hero_parallax.pack(fill="x", padx=30, pady=(20, 0))

    # ------------------------------------------------------- INSIGHTS CARDS
    def _build_insights_section(self):
        ins_frame = ctk.CTkFrame(self.body, fg_color="transparent")
        ins_frame.pack(fill="x", padx=40, pady=(30, 10))

        ctk.CTkLabel(ins_frame, text="Cinephile Insights",
                     font=("Helvetica", 24, "bold"),
                     text_color="white").pack(anchor="w")

        cards_f = ctk.CTkFrame(ins_frame, fg_color="transparent")
        cards_f.pack(fill="x", pady=15)

        stats = [
            ("Total Movies",   "250 Titles",   "🎬", "#2d5a27"),
            ("Trending Genre", "Action/Sci-Fi", "🔥", "#2A368F"),
            ("Global Rating",  "4.9/5.0",       "⭐", "#8A4B1A"),
        ]
        for tit, val, ico, col in stats:
            card = ctk.CTkFrame(cards_f, fg_color=col, corner_radius=15, height=100)
            card.pack(side="left", fill="x", expand=True, padx=10)
            card.pack_propagate(False)
            ctk.CTkLabel(card, text=ico, font=("Arial", 35)).pack(side="left", padx=20)
            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", fill="y", pady=20)
            ctk.CTkLabel(info, text=tit, font=("Trebuchet MS", 13),
                         text_color="#DDD").pack(anchor="w")
            ctk.CTkLabel(info, text=val, font=("Arial Black", 20, "bold"),
                         text_color="white").pack(anchor="w")

    # ----------------------------------------------------------- TRENDING
    def _build_trending_now(self):
        ctk.CTkLabel(self.body, text="Trending Now",
                     font=("Helvetica", 24, "bold"),
                     text_color="white").pack(anchor="w", padx=40, pady=(20, 5))

        self.scroll_h = ctk.CTkScrollableFrame(
            self.body, orientation="horizontal",
            height=280, fg_color="transparent"
        )
        self.scroll_h.pack(fill="x", padx=30)

        movies = getattr(self.app, "movie_list", [])
        if not movies:
            return

        extended    = movies[:15] * 4
        image_cache = {}

        for m in extended:
            card = ctk.CTkFrame(self.scroll_h, fg_color="transparent",
                                width=160, cursor="hand2")
            card.pack(side="left", padx=10)
            click_cmd = lambda e, d=m: self._go_to_detail(d)

            p_path    = m.get("poster_local", "")
            img_label = ctk.CTkLabel(card, text="", width=150, height=220)

            if p_path and os.path.exists(p_path):
                if p_path not in image_cache:
                    try:
                        image_cache[p_path] = ctk.CTkImage(
                            Image.open(p_path), size=(150, 220))
                    except Exception:
                        pass
                if p_path in image_cache:
                    img_label.configure(image=image_cache[p_path])

            img_label.pack()

            t_text = m.get("title", "Unknown")
            if len(t_text) > 18:
                t_text = t_text[:15] + "..."
            ctk.CTkLabel(card, text=t_text, font=("Trebuchet MS", 12, "bold"),
                         text_color="white").pack(pady=8)

            for w in [card, img_label]:
                w.bind("<Button-1>", click_cmd)

        self._current_scroll_pos = 0.0
        self._auto_scroll_trending()

    def _auto_scroll_trending(self):
        if not hasattr(self, "scroll_h") or not self.scroll_h.winfo_exists():
            return
        self._current_scroll_pos += 0.0003
        if self._current_scroll_pos >= 1.0:
            self._current_scroll_pos = 0.0
        try:
            self.scroll_h._parent_canvas.xview_moveto(self._current_scroll_pos)
        except Exception:
            pass
        self.after(40, self._auto_scroll_trending)

    # ---------------------------------------------------------- TOP 10 LIST
    def _build_top_10_list(self):
        self._top10_images = []

        cont = ctk.CTkFrame(self.body, fg_color="#F8F9FA", corner_radius=20)
        cont.pack(fill="x", padx=30, pady=20)

        ctk.CTkLabel(cont, text="Top 10 Movies",
                     font=("Helvetica", 32, "bold"),
                     text_color="#1A1A1A").pack(anchor="w", padx=40, pady=(25, 15))

        h_frame = ctk.CTkFrame(cont, fg_color="transparent")
        h_frame.pack(fill="x", padx=40, pady=(0, 10))

        w_poster = 80; w_title = 280; w_year = 90
        w_mood   = 150; w_platform = 200; w_synopsis = 500

        for text, width in [("", w_poster), ("Film", w_title), ("Year", w_year),
                             ("Mood", w_mood), ("Platform", w_platform),
                             ("Synopsis", w_synopsis)]:
            ctk.CTkLabel(h_frame, text=text,
                         font=("Trebuchet MS", 14, "bold"),
                         text_color="#555", anchor="w",
                         width=width).pack(side="left")

        movies = getattr(self.app, "movie_list", [])[:10]
        for m in movies:
            row = ctk.CTkFrame(cont, fg_color="transparent", cursor="hand2")
            row.pack(fill="x", padx=40, pady=12)
            click_cmd = lambda e, data=m: self._go_to_detail(data)
            row.bind("<Button-1>", click_cmd)

            p_lbl = ctk.CTkLabel(row, text="🎬", width=w_poster,
                                  font=("Arial", 28), text_color="#AAAAAA")
            p_path = m.get("poster_local", "")
            if p_path and os.path.exists(p_path):
                try:
                    ctk_img = ctk.CTkImage(Image.open(p_path).convert("RGB"),
                                           size=(55, 80))
                    self._top10_images.append(ctk_img)
                    p_lbl.configure(image=ctk_img, text="")
                except Exception:
                    pass
            p_lbl.pack(side="left")
            p_lbl.bind("<Button-1>", click_cmd)

            # Title
            t_lbl = ctk.CTkLabel(row, text=m.get("title", "N/A"),
                                  width=w_title, anchor="w",
                                  font=("Trebuchet MS", 15, "bold"),
                                  text_color="#800000", wraplength=260, justify="left")
            t_lbl.pack(side="left"); t_lbl.bind("<Button-1>", click_cmd)

            # Year
            y_lbl = ctk.CTkLabel(row, text=str(m.get("year", "N/A")),
                                  width=w_year, anchor="w",
                                  font=("Trebuchet MS", 14, "bold"), text_color="#1A1A1A")
            y_lbl.pack(side="left"); y_lbl.bind("<Button-1>", click_cmd)

            # Genre/Mood
            g_lbl = ctk.CTkLabel(row, text=m.get("genre", "N/A").split(',')[0],
                                  width=w_mood, anchor="w",
                                  font=("Trebuchet MS", 14, "bold"), text_color="#2A52BE")
            g_lbl.pack(side="left"); g_lbl.bind("<Button-1>", click_cmd)

            # Platform
            raw_plat = m.get("platform_string", "N/A")
            display_plat = raw_plat.split(',')[0].strip() if raw_plat else "N/A"
            pl_lbl = ctk.CTkLabel(row, text=f"📺 {display_plat}",
                                   width=w_platform, anchor="w",
                                   font=("Trebuchet MS", 13, "bold"), text_color="#2D5A27")
            pl_lbl.pack(side="left"); pl_lbl.bind("<Button-1>", click_cmd)

            # Synopsis
            syn = m.get("description", "No synopsis available.")
            s_lbl = ctk.CTkLabel(row,
                                  text=(syn[:180] + "..") if len(syn) > 180 else syn,
                                  width=w_synopsis, anchor="w",
                                  font=("Trebuchet MS", 12), text_color="#444",
                                  wraplength=480, justify="left")
            s_lbl.pack(side="left"); s_lbl.bind("<Button-1>", click_cmd)

            ctk.CTkFrame(cont, fg_color="#E0E0E0", height=1).pack(fill="x", padx=40)

    # ------------------------------------------------------------ TAGLINE
    def _build_tagline_section(self):
        self.tagline_frame = ctk.CTkFrame(
            self.body, fg_color="#1C1C1C",
            corner_radius=20, border_width=1, border_color="#2A2A2A",
            height=200
        )
        self.tagline_frame.pack(fill="x", padx=30, pady=10)
        self.tagline_frame.pack_propagate(False)

        # Spacer atas
        ctk.CTkFrame(self.tagline_frame, fg_color="transparent", height=60).pack()

        # Garis merah pendek
        ctk.CTkFrame(
            self.tagline_frame, fg_color="#7A1C1C",
            width=48, height=2, corner_radius=2
        ).pack()

        # Quote utama
        ctk.CTkLabel(
            self.tagline_frame,
            text='"Every story has a beginning."',
            font=("Georgia", 22, "italic"),
            text_color="#CCCCCC"
        ).pack(pady=(22, 8))

        # Subtitle spasi manual
        ctk.CTkLabel(
            self.tagline_frame,
            text="S T A R T   Y O U R   C I N E P H I L E   J O U R N E Y",
            font=("Trebuchet MS", 10, "bold"),
            text_color="#555555"
        ).pack()

        # Garis bawah
        ctk.CTkFrame(
            self.tagline_frame, fg_color="#333333",
            width=40, height=1, corner_radius=1
        ).pack(pady=(22, 0))
    # ------------------------------------------------------- WATCHLIST BANNER
    def _build_watchlist_banner(self):
        banner = ctk.CTkFrame(self.body, fg_color="#FF8C00",
                              corner_radius=20, height=200)
        banner.pack(fill="x", padx=30, pady=(20, 30))
        banner.pack_propagate(False)
        ctx = ctk.CTkFrame(banner, fg_color="transparent")
        ctx.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(ctx, text="Manage your watchlist now!",
                     font=("Trebuchet MS", 24, "bold"),
                     text_color="#111").pack()
        ctk.CTkButton(ctx, text="GO TO WATCHLIST",
                      fg_color="#111", text_color="white",
                      font=("Trebuchet MS", 14, "bold"),
                      width=240, height=48, corner_radius=10,
                      command=lambda: self.app.show_page("watchlist")
                      ).pack(pady=18)

    # ------------------------------------------------------------ FOOTER
    def _build_footer(self):
        footer = ctk.CTkFrame(self.body, fg_color="#0A0A0A", corner_radius=0, height=180)
        footer.pack(fill="x", pady=(20, 0))
        footer.pack_propagate(False)
        ctk.CTkLabel(
            footer, text="CINEPHILE",
            font=("Trebuchet MS", 55, "bold"),
            text_color=TEXT_WHITE
        ).place(relx=0.05, rely=0.5, anchor="w")
        ctk.CTkLabel(
            footer,
            text="©2026 Cinephile Archive\nCurating cinematic excellence for your personal collection.",
            font=("Trebuchet MS", 12),
            text_color="#AAAAAA",
            justify="right"
        ).place(relx=0.95, rely=0.5, anchor="e")
    # ----------------------------------------------------- SCROLL NOTIFICATION
    def _show_scroll_notification(self):
        self.notif_frame = ctk.CTkFrame(
            self, fg_color="#2A2A2A", corner_radius=20, width=320, height=50)
        self._current_rely = 1.1
        self.notif_frame.place(relx=0.5, rely=self._current_rely, anchor="center")
        ctk.CTkLabel(self.notif_frame,
                     text="↓  Scroll down to explore more",
                     font=("Trebuchet MS", 13, "bold"),
                     text_color="#E0E0E0").pack(padx=30, pady=10)
        self._target_rely_up = 0.92
        self._slide_notif_up()
        self.after(5000, self._start_slide_notif_down)

    def _slide_notif_up(self):
        if not hasattr(self, "notif_frame") or not self.notif_frame.winfo_exists():
            return
        if self._current_rely > self._target_rely_up:
            self._current_rely -= 0.008
            self.notif_frame.place(relx=0.5, rely=self._current_rely, anchor="center")
            self.after(15, self._slide_notif_up)

    def _start_slide_notif_down(self):
        self._target_rely_down = 1.1
        self._slide_notif_down()

    def _slide_notif_down(self):
        if not hasattr(self, "notif_frame") or not self.notif_frame.winfo_exists():
            return
        if self._current_rely < self._target_rely_down:
            self._current_rely += 0.008
            self.notif_frame.place(relx=0.5, rely=self._current_rely, anchor="center")
            self.after(15, self._slide_notif_down)
        else:
            try:
                self.notif_frame.destroy()
            except Exception:
                pass
