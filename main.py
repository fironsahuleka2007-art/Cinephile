import customtkinter as ctk
import tkinter as tk
import json
import os
import threading
import random

from loginPage import AuthPages
from movieTable import MovietablePage
from dashboardCinephile import DashboardPage
from profilePage import ProfilePage
from genreAnalyze import GenreAnalyzePage
from movieDetail import MovieDetailPage
from watchlist import WatchlistPage
from scraper import MovieScraper
from styles import *

try:
    from PIL import Image, ImageFilter, ImageEnhance, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


_POSTER_W = 130
_POSTER_H = 195
_STRIP_W  = 44
_N = 24

_GRID = [
    (0.00, 0.00, 0.6),  (0.00, 0.25, 0.9),  (0.00, 0.50, 0.7),  (0.00, 0.75, 1.0),
    (0.17, 0.12, 1.0),  (0.17, 0.37, 0.55), (0.17, 0.62, 1.05), (0.17, 0.87, 0.8),
    (0.34, 0.00, 0.85), (0.34, 0.25, 1.1),  (0.34, 0.50, 0.65), (0.34, 0.75, 0.9),
    (0.51, 0.12, 1.2),  (0.51, 0.37, 0.8),  (0.51, 0.62, 1.0),  (0.51, 0.87, 0.7),
    (0.68, 0.00, 0.9),  (0.68, 0.25, 1.1),  (0.68, 0.50, 0.75), (0.68, 0.75, 1.0),
    (0.85, 0.12, 0.7),  (0.85, 0.37, 1.0),  (0.85, 0.62, 0.85), (0.85, 0.87, 0.95),
]
_POSTER_CACHE = []


def _precache_posters(movie_list):
    global _POSTER_CACHE
    if not PIL_AVAILABLE:
        return
    pool = [m for m in movie_list if m.get("poster_local") and os.path.exists(m["poster_local"])]
    if not pool:
        return
    random.shuffle(pool)
    while len(pool) < _N:
        pool = pool * 2
    pool = pool[:_N]
    imgs = []
    for m in pool:
        try:
            img = Image.open(m["poster_local"]).convert("RGB")
            img = img.resize((_POSTER_W, _POSTER_H), Image.LANCZOS)
            img = img.filter(ImageFilter.GaussianBlur(1.5))
            img = ImageEnhance.Brightness(img).enhance(0.25)
        except Exception:
            img = Image.new("RGB", (_POSTER_W, _POSTER_H), (20, 20, 20))
        imgs.append(img)
    _POSTER_CACHE = imgs


# ══════════════════════════════════════════════════════════════ WELCOME SCREEN
class WelcomeScreen(tk.Frame):

    def __init__(self, master, app, username):
        super().__init__(master, bg="#0D0D0D")
        self.app      = app
        self.username = username

        self._cx = 550.0; self._cy = 425.0
        self._mx = 550.0; self._my = 425.0
        self._tx = 550.0; self._ty = 425.0

        self._poster_items = []
        self._tk_images    = []
        self._drawn        = False
        self._loop_id      = None
        self._exit_id      = None
        self._fade_overlay = None

        self._btn_bbox = (435, 510, 665, 558)

        self._build()
        self._load_posters()
        self._parallax_loop()

    # ------------------------------------------------------------------ BUILD
    def _build(self):
        self.canvas = tk.Canvas(self, bg="#0D0D0D", highlightthickness=0)
        self.canvas.place(x=0, y=0, relwidth=1.0, relheight=1.0)
        self.canvas.bind("<Motion>",    self._on_motion)
        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<Button-1>",  self._on_click)

        self._strip_l = self._make_strip()
        self._strip_l.place(x=0, y=0, width=_STRIP_W, relheight=1.0)

        self._strip_r = self._make_strip()
        self._strip_r.place(relx=1.0, x=-_STRIP_W, y=0, width=_STRIP_W, relheight=1.0)

        self._build_content()

    def _make_strip(self):
        f = tk.Frame(self, bg="#1C1C1C")
        for i in range(120):
            hole = tk.Frame(f, bg="#0D0D0D", width=14, height=9)
            hole.place(x=15, y=10 + i * 36)
        return f

    def _build_content(self):
        self._id_tag = self.canvas.create_text(
            550, 280,
            text="✦  CINEPHILE  ·  YOUR CINEMA UNIVERSE",
            font=("Trebuchet MS", 11, "bold"),
            fill="#666666", tags="content",
        )
        self._id_wb = self.canvas.create_text(
            550, 340, text="Welcome back,",
            font=("Georgia", 42, "bold"), fill="#FFFFFF", tags="content",
        )
        self._id_user = self.canvas.create_text(
            550, 408, text=self.username,
            font=("Georgia", 50, "bold"), fill="#E8A020", tags="content",
        )

        stats = self._get_stats()
        self._stats_id = self.canvas.create_text(
            550, 466,
            text=f"{stats['films']} films  ·  {stats['watchlist']} watchlists  ·  {stats['rating']} avg rating",
            font=("Trebuchet MS", 13), fill="#BBBBBB",
            tags="content",
        )

        bx, by = 550, 534
        bw, bh, r = 230, 48, 24
        x1, y1 = bx - bw // 2, by - bh // 2
        x2, y2 = bx + bw // 2, by + bh // 2
        self._btn_bbox = (x1, y1, x2, y2)

        self._btn_rect = self._rounded_rect(x1, y1, x2, y2, r, fill="#b03535", outline="")
        self._btn_text = self.canvas.create_text(
            bx, by, text="▶   Lanjutkan menonton",
            font=("Trebuchet MS", 14, "bold"), fill="white",
            tags="content",
        )
        for item in (self._btn_rect, self._btn_text):
            self.canvas.tag_bind(item, "<Enter>",    self._btn_enter)
            self.canvas.tag_bind(item, "<Leave>",    self._btn_leave)
            self.canvas.tag_bind(item, "<Button-1>", self._btn_click)

    def _rounded_rect(self, x1, y1, x2, y2, r, **kw):
        points = [
            x1+r, y1,  x2-r, y1,
            x2,   y1,  x2,   y1+r,
            x2,   y2-r, x2,  y2,
            x2-r, y2,  x1+r, y2,
            x1,   y2,  x1,   y2-r,
            x1,   y1+r, x1,  y1,
        ]
        return self.canvas.create_polygon(points, smooth=True, tags="content", **kw)

    def _btn_enter(self, event):
        self.canvas.itemconfig(self._btn_rect, fill="#C62828")
        self.canvas.config(cursor="hand2")

    def _btn_leave(self, event):
        self.canvas.itemconfig(self._btn_rect, fill="#b03535")
        self.canvas.config(cursor="")

    def _btn_click(self, event):
        self._go()

    def _on_click(self, event):
        x1, y1, x2, y2 = self._btn_bbox
        if x1 <= event.x <= x2 and y1 <= event.y <= y2:
            self._go()

    def _on_resize(self, event):
        w, h = event.width, event.height
        if w < 10 or h < 10:
            return
        self._cx = w / 2; self._cy = h / 2
        self._tx = self._mx = self._cx
        self._ty = self._my = self._cy
        cx = int(self._cx)

        self.canvas.coords(self._id_tag,   cx, h * 0.33)
        self.canvas.coords(self._id_wb,    cx, h * 0.40)
        self.canvas.coords(self._id_user,  cx, h * 0.49)
        self.canvas.coords(self._stats_id, cx, h * 0.56)

        bx, by = cx, int(h * 0.64)
        bw, bh, r = 230, 48, 24
        x1, y1 = bx - bw // 2, by - bh // 2
        x2, y2 = bx + bw // 2, by + bh // 2
        self._btn_bbox = (x1, y1, x2, y2)
        points = [
            x1+r, y1,  x2-r, y1,
            x2,   y1,  x2,   y1+r,
            x2,   y2-r, x2,  y2,
            x2-r, y2,  x1+r, y2,
            x1,   y2,  x1,   y2-r,
            x1,   y1+r, x1,  y1,
        ]
        self.canvas.coords(self._btn_rect, *points)
        self.canvas.coords(self._btn_text, bx, by)

        for item in self._poster_items:
            item["bx"] = item["rx"] * w + item["jx"]
            item["by"] = item["ry"] * h + item["jy"]

    def _get_stats(self):
        films = len(getattr(self.app, "movie_list", []))
        wl = 0
        try:
            if os.path.exists("watchlist.json"):
                with open("watchlist.json") as f:
                    wl = len(json.load(f).get(self.username, []))
        except Exception:
            pass
        return {"films": films or 250, "watchlist": wl or 12, "rating": "4.9"}

    # ------------------------------------------------------------------ POSTER LOADING
    def _load_posters(self):
        if not PIL_AVAILABLE:
            return
        if _POSTER_CACHE:
            self.after(50, lambda: self._draw_when_ready(_POSTER_CACHE[:]))
        else:
            threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        movies = getattr(self.app, "movie_list", [])
        pool = [m for m in movies if m.get("poster_local") and os.path.exists(m["poster_local"])]
        if not pool:
            return
        random.shuffle(pool)
        while len(pool) < _N:
            pool = pool * 2
        pool = pool[:_N]

        imgs = []
        for m in pool:
            try:
                img = Image.open(m["poster_local"]).convert("RGB")
                img = img.resize((_POSTER_W, _POSTER_H), Image.LANCZOS)
                img = img.filter(ImageFilter.GaussianBlur(1.5))
                img = ImageEnhance.Brightness(img).enhance(0.25)
            except Exception:
                img = Image.new("RGB", (_POSTER_W, _POSTER_H), (20, 20, 20))
            imgs.append(img)

        self.after(0, lambda i=imgs: self._draw_when_ready(i))

    def _draw_when_ready(self, imgs, attempt=0):
        if not self.winfo_exists() or self._drawn:
            return
        w, h = self.winfo_width(), self.winfo_height()
        if (w < 10 or h < 10) and attempt < 30:
            self.after(80, lambda: self._draw_when_ready(imgs, attempt + 1))
            return
        self._drawn = True
        self._do_draw(imgs, w or 1100, h or 850)

    def _do_draw(self, imgs, w, h):
        for i, pil_img in enumerate(imgs[:_N]):
            rx, ry, depth = _GRID[i]
            jx = random.randint(-4, 4)
            jy = random.randint(-4, 4)
            bx = rx * w + jx
            by = ry * h + jy

            tk_img = ImageTk.PhotoImage(pil_img)
            self._tk_images.append(tk_img)
            cid = self.canvas.create_image(bx, by, image=tk_img, anchor="nw")
            self.canvas.tag_lower(cid)

            self._poster_items.append({
                "id": cid, "bx": bx, "by": by,
                "rx": rx, "ry": ry, "jx": jx, "jy": jy, "depth": depth,
            })

        self.canvas.tag_raise("content")
        self.canvas.tag_raise(self._btn_rect)
        self.canvas.tag_raise(self._btn_text)

    # ------------------------------------------------------------------ PARALLAX
    def _on_motion(self, event):
        try:
            self._tx = event.x_root - self.canvas.winfo_rootx()
            self._ty = event.y_root - self.canvas.winfo_rooty()
        except Exception:
            pass

    def _parallax_loop(self):
        if not self.winfo_exists():
            return
        ease = 0.07
        self._mx += (self._tx - self._mx) * ease
        self._my += (self._ty - self._my) * ease
        cx = max(self._cx, 1); cy = max(self._cy, 1)
        ox = max(-1.0, min(1.0, (self._mx - cx) / cx))
        oy = max(-1.0, min(1.0, (self._my - cy) / cy))
        for item in self._poster_items:
            try:
                self.canvas.coords(
                    item["id"],
                    item["bx"] + ox * 30 * item["depth"],
                    item["by"] + oy * 20 * item["depth"],
                )
            except Exception:
                pass
        self._loop_id = self.after(16, self._parallax_loop)

    # ------------------------------------------------------------------ EXIT TRANSITION
    def _go(self):
        """Tombol diklik — mulai animasi fade-out."""
        if not self.winfo_exists():
            return
        # Hentikan parallax loop
        if self._loop_id:
            try:
                self.after_cancel(self._loop_id)
            except Exception:
                pass
        self._loop_id = None

        # Nonaktifkan tombol agar tidak double-click
        self.canvas.unbind("<Button-1>")

        # Buat overlay hitam di atas semua konten
        w = self.winfo_width() or 1100
        h = self.winfo_height() or 850
        self._fade_overlay = self.canvas.create_rectangle(
            0, 0, w, h,
            fill="#000000",
            stipple="gray12",
            outline="",
            tags="fade_overlay"
        )
        self.canvas.tag_raise("fade_overlay")

        # Mulai animasi fade-out (step 0 dari 20)
        self._run_fadeout(step=0, total=20)

    def _run_fadeout(self, step, total):
        """Animasi fade-out WelcomeScreen ke hitam, lalu pindah ke dashboard."""
        if not self.winfo_exists():
            return

        # Stipple map: makin banyak step, makin gelap
        stipple_stages = [
            "",         # step 0-2:  hampir tidak terlihat
            "gray12",   # step 3-5
            "gray25",   # step 6-8
            "gray50",   # step 9-11
            "gray75",   # step 12-14
            "",         # step 15+: overlay penuh (fill solid)
        ]
        # Pilih stipple sesuai progress
        progress = step / total
        if progress < 0.15:
            stipple = ""
            fill = "#000000"
            # Naikkan opacity window sedikit untuk efek awal
            try:
                self.app.wm_attributes("-alpha", 1.0)
            except Exception:
                pass
        elif progress < 0.30:
            stipple = "gray12"
            fill = "#000000"
        elif progress < 0.45:
            stipple = "gray25"
            fill = "#000000"
        elif progress < 0.60:
            stipple = "gray50"
            fill = "#000000"
        elif progress < 0.75:
            stipple = "gray75"
            fill = "#000000"
        else:
            stipple = ""
            fill = "#000000"

        try:
            self.canvas.itemconfig(
                self._fade_overlay,
                fill=fill,
                stipple=stipple
            )
            # Resize overlay mengikuti canvas
            cw = self.canvas.winfo_width()
            ch = self.canvas.winfo_height()
            self.canvas.coords(self._fade_overlay, 0, 0, cw, ch)
        except Exception:
            pass

        if step < total:
            self._exit_id = self.after(18, lambda: self._run_fadeout(step + 1, total))
        else:
            # Fade out selesai → pindah ke dashboard
            self.after(60, lambda: self.app._do_welcome_to_dashboard(self))

    # ------------------------------------------------------------------ DESTROY
    def destroy(self):
        if self._loop_id:
            try:
                self.after_cancel(self._loop_id)
            except Exception:
                pass
        if self._exit_id:
            try:
                self.after_cancel(self._exit_id)
            except Exception:
                pass
        super().destroy()


# ══════════════════════════════════════════════════════════════════ MAIN APP
class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Cinephile App")
        self.geometry("1100x850")
        self.configure(fg_color=BG_MAIN)

        self.db_path = "data_film.json"
        self.scraper = MovieScraper()
        self.current_page_instance = None
        self.is_admin  = False
        self.username  = "guest"
        self._welcome  = None

        self._load_local_data()

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)
        self.auth = AuthPages(self.container, self)
        
        active_user = None
        if os.path.exists("session.json"):
            try:
                with open("session.json", "r", encoding="utf-8") as f:
                    active_user = json.load(f).get("active_user")
            except: pass

        active_user = None
        if os.path.exists("session.json"):
            try:
                with open("session.json", "r", encoding="utf-8") as f:
                    active_user = json.load(f).get("active_user")
            except Exception:
                pass

        if active_user:
            self.username = active_user
            self.show_page("dashboard")
        else:
            self.show_page("login")

    def _load_local_data(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    self.movie_list = json.load(f)
            except Exception:
                self.movie_list = []
        else:
            self.movie_list = []
        if self.movie_list:
            threading.Thread(target=_precache_posters,
                             args=(self.movie_list,), daemon=True).start()
        else:
            threading.Thread(target=self._initialize_data, daemon=True).start()

    def _initialize_data(self):
        hasil = self.scraper.scrape_top_movies()
        if hasil:
            self.movie_list = hasil
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(self.movie_list, f, indent=4)
            print("✅ Database Ready!")
            _precache_posters(self.movie_list)

    def show_page(self, page_name, data=None):
        if self._welcome and self._welcome.winfo_exists():
            self._welcome.destroy()
        self._welcome = None

        for w in self.container.winfo_children():
            w.destroy()
        self.current_page_instance = None

        if page_name == "login":
            self.geometry("1100x850")
            self.auth.render_login()
        elif page_name == "register":
            self.auth.render_register()
        elif page_name == "dashboard":
            self.geometry("1100x850")
            self.current_page_instance = DashboardPage(self.container, self)
        elif page_name == "profile":
            self.geometry("1100x850")
            self.current_page_instance = ProfilePage(self.container, self)
        elif page_name == "movietable":
            self.current_page_instance = MovietablePage(self.container, self)
        elif page_name == "genreanalyze":
            self.current_page_instance = GenreAnalyzePage(self.container, self)
        elif page_name == "moviedetail":
            self.current_page_instance = MovieDetailPage(self.container, self, movie_data=data)
        elif page_name == "watchlist":
            # FIX UTAMA: Kembalikan ke format original agar tidak crash positional argument!
            # Halaman WatchlistPage di dalam filenya nanti tinggal baca 'self.app.username'
            self.current_page_instance = WatchlistPage(self.container, self)

        if self.current_page_instance and hasattr(self.current_page_instance, "pack"):
            self.current_page_instance.pack(fill="both", expand=True)

    def show_welcome_transition(self, username):
        """Tampilkan WelcomeScreen dengan fade-in dari login."""
        self.username = username
        self.container.pack_forget()

        if self._welcome and self._welcome.winfo_exists():
            self._welcome.destroy()

        # Mulai dari transparan
        try:
            self.wm_attributes("-alpha", 0.0)
        except Exception:
            pass

        self._welcome = WelcomeScreen(self, self, username)
        self._welcome.place(x=0, y=0, relwidth=1.0, relheight=1.0)
        self._welcome.lift()

        # Jalankan fade-in WelcomeScreen
        self.after(80, lambda: self._fadein_welcome(step=0, total=15))

    def _fadein_welcome(self, step, total):
        """Fade-in halus saat WelcomeScreen pertama kali muncul."""
        if not self._welcome or not self._welcome.winfo_exists():
            return
        progress = step / total
        # Ease-in-out cubic
        if progress < 0.5:
            alpha = 4 * progress ** 3
        else:
            alpha = 1 - (-2 * progress + 2) ** 3 / 2
        alpha = max(0.0, min(1.0, alpha))
        try:
            self.wm_attributes("-alpha", alpha)
        except Exception:
            pass
        if step < total:
            self.after(16, lambda: self._fadein_welcome(step + 1, total))
        else:
            try:
                self.wm_attributes("-alpha", 1.0)
            except Exception:
                pass

    def _do_welcome_to_dashboard(self, welcome_widget):
        """Selesai fade-out WelcomeScreen → fade-in Dashboard."""
        # Hancurkan welcome screen
        try:
            welcome_widget.place_forget()
        except Exception:
            pass
        try:
            welcome_widget.destroy()
        except Exception:
            pass
        self._welcome = None

        # Reset alpha ke 0 untuk fade-in dashboard
        try:
            self.wm_attributes("-alpha", 0.0)
        except Exception:
            pass

        # Pasang container dan render dashboard
        try:
            self.container.pack_forget()
        except Exception:
            pass
        self.container.pack(fill="both", expand=True)
        self.update_idletasks()
        self.show_page("dashboard")

        # Jalankan fade-in dashboard
        self.after(40, lambda: self._fadein_dashboard(step=0, total=22))

    def _fadein_dashboard(self, step, total):
        """Fade-in dashboard dengan easing ease-out cubic."""
        progress = step / total
        # Ease-out cubic: starts fast, slows down at end
        alpha = 1 - (1 - progress) ** 3
        alpha = max(0.0, min(1.0, alpha))
        try:
            self.wm_attributes("-alpha", alpha)
        except Exception:
            pass
        if step < total:
            self.after(14, lambda: self._fadein_dashboard(step + 1, total))
        else:
            try:
                self.wm_attributes("-alpha", 1.0)
            except Exception:
                pass

    def show_toast(self, message, target=None):
        print(f"Toast: {message}")
        if target:
            self.show_page(target)

    def show_welcome_transition(self, username):
        # Kunci username yang sukses login ke Core Application
        self.username = username
        self._check_admin_status()  # ← CEK ADMIN STATUS SETELAH LOGIN

        self.username = username 
        
        for widget in self.container.winfo_children():
            widget.destroy()
            
        welcome_frame = ctk.CTkFrame(self.container, fg_color=BG_MAIN)
        welcome_frame.place(relwidth=1, relheight=1)
        
        self.welcome_lbl = ctk.CTkLabel(welcome_frame, text=f"Welcome back,\n{username}", font=("Arial Black", 46, "bold"), text_color="white", justify="center")
        self.welcome_lbl.place(relx=0.5, rely=0.55, anchor="center") 
        
        self.text_y = 0.55
        self._animate_text_up()
        
        self.after(2000, lambda: self._slide_up_dashboard(welcome_frame))

    def _animate_text_up(self):
        if hasattr(self, 'welcome_lbl') and self.welcome_lbl.winfo_exists():
            if self.text_y > 0.48:
                self.text_y -= 0.001
                self.welcome_lbl.place(rely=self.text_y)
                self.after(16, self._animate_text_up)

    def _slide_up_dashboard(self, welcome_frame):
        self.current_page_instance = DashboardPage(self.container, self)
        self.current_page_instance.place(relwidth=1, relheight=1, rely=1.0, relx=0)
        self.slide_y = 1.0
        self._animate_slide(welcome_frame)

    def _animate_slide(self, welcome_frame):
        if self.slide_y > 0.005: 
            self.slide_y += (0.0 - self.slide_y) * 0.08 
            self.current_page_instance.place(rely=self.slide_y)
            self.after(16, lambda: self._animate_slide(welcome_frame))
        else:
            self.current_page_instance.place(rely=0)
            welcome_frame.destroy()
            self.current_page_instance.place_forget()
            self.current_page_instance.pack(fill="both", expand=True)

    def handle_local_search(self, query):
        if not query:
            return
        self.search_query_pending = query.lower().strip()
        self.show_page("movietable")

    def logout_user(self):
        if os.path.exists("session.json"):
            try:
                os.remove("session.json")
            except Exception:
                pass
        self.username = "guest"
        self.show_page("login")

    def on_closing(self):
        try:
            self.scraper.close()
        except Exception:
            pass
        self.destroy()


if __name__ == "__main__":
    app = MainApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()