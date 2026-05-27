import tkinter as tk
import math
import random
import time

BG_DARK     = "#1a1a1a"
ACCENT      = "#7A1C1C"
ACCENT2     = "#8d2827"
TEXT_WHITE  = "#ffffff"
TEXT_MUTED  = "#888899"
PROGRESS_BG = "#2a2a2a"

LOADING_TEXTS = [
    "Finding your perfect movie...",
    "Matching genres to your vibe...",
    "Adding to your watchlist...",
    "Rate your movie experience...",
    "Leave a quick note...",
]


class CinephileLoadingScreen(tk.Tk):
    def __init__(self, duration_ms=5000, on_done=None):
        super().__init__()
        self.duration_ms = duration_ms
        self.on_done     = on_done
        self._running    = True
        self._t          = 0.0

        self.title("Cinephile")
        self.configure(bg=BG_DARK)
        self.overrideredirect(True)

        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{sw}x{sh}+0+0")
        self.attributes("-topmost", True)
        self.lift()

        self._sw = sw
        self._sh = sh

        self._c = tk.Canvas(self, bg=BG_DARK, highlightthickness=0)
        self._c.place(x=0, y=0, width=sw, height=sh)

        self._stars   = self._make_stars(120)
        self._meteors = []
        self._star_t  = 0.0

        # Clapper state — cartoon style, arm buka tutup
        self._clap_angle = 0.0
        self._clap_open  = False
        self._clap_dir   = 1
        self._clap_timer = 4.0
        self._clap_max   = 38.0
        self._snap_speed = 5.0

        # Star sparkle (bintang oranye seperti referensi)
        self._star_scale  = 0.0
        self._star_vis    = False

        self._progress = 0.0
        self._tip_text = LOADING_TEXTS[0]
        self._start_ms = int(time.time() * 1000)

        self._auto_meteor()
        self._animate()
        self.after(self.duration_ms, self._finish)

    def _get_size(self):
        w = self.winfo_width()
        h = self.winfo_height()
        return (w if w > 10 else self._sw), (h if h > 10 else self._sh)

    # ── Stars background ──────────────────────────────────────────────────────
    def _make_stars(self, n):
        return [
            {
                "x"    : random.random() * self._sw,
                "y"    : random.random() * self._sh,
                "r"    : random.uniform(0.3, 1.3),
                "alpha": random.uniform(0.1, 0.55),
                "phase": random.uniform(0, math.pi * 2),
                "speed": random.uniform(0.005, 0.022),
            }
            for _ in range(n)
        ]

    def _auto_meteor(self):
        if not self._running:
            return
        sw, sh = self._get_size()
        self._meteors.append({
            "x"   : random.random() * sw * 0.8,
            "y"   : random.random() * sh * 0.4,
            "vx"  : random.uniform(4, 7),
            "vy"  : random.uniform(2, 4),
            "len" : random.randint(50, 110),
            "life": 0.0,
        })
        self.after(2800, self._auto_meteor)

    @staticmethod
    def _rgba(r, g, b, a):
        bg = 26
        return f"#{int(r*a+bg*(1-a)):02x}{int(g*a+bg*(1-a)):02x}{int(b*a+bg*(1-a)):02x}"

    # ── Clapper logic ─────────────────────────────────────────────────────────
    def _update_clapper(self):
        self._clap_timer -= 0.016
        if not self._clap_open and self._clap_timer <= 0:
            self._clap_open = True
            self._clap_dir  = 1
            self._star_vis  = False

        if self._clap_open:
            if self._clap_dir == 1:
                self._clap_angle += self._snap_speed * 0.3
                if self._clap_angle >= self._clap_max:
                    self._clap_angle = self._clap_max
                    self._clap_dir   = -1
            else:
                self._clap_angle -= self._snap_speed
                if self._clap_angle <= 0:
                    self._clap_angle = 0.0
                    self._clap_open  = False
                    self._clap_timer = random.uniform(5.0, 8.0)
                    # Munculkan bintang oranye saat snap
                    self._star_vis   = True
                    self._star_scale = 0.0

        # Animasi bintang oranye muncul lalu menghilang
        if self._star_vis:
            self._star_scale += 0.06
            if self._star_scale > 2.5:
                self._star_vis = False

    def _animate(self):
        if not self._running:
            return
        self._t      += 0.016
        self._star_t += 0.016

        now_ms = int(time.time() * 1000)
        self._progress = min(1.0, (now_ms - self._start_ms) / self.duration_ms)
        idx = int(self._progress * len(LOADING_TEXTS))
        self._tip_text = LOADING_TEXTS[min(idx, len(LOADING_TEXTS) - 1)]

        self._update_clapper()
        self._redraw()
        self.after(16, self._animate)

    # ── Full redraw ───────────────────────────────────────────────────────────
    def _redraw(self):
        c = self._c
        c.delete("all")
        sw, sh = self._get_size()
        cx = sw // 2

        c.create_rectangle(0, 0, sw, sh, fill=BG_DARK, outline="")

        # Starfield
        for s in self._stars:
            tw  = math.sin(self._star_t * s["speed"] * 60 + s["phase"])
            a   = s["alpha"] * (0.4 + 0.6 * ((tw + 1) / 2))
            col = self._rgba(255, 255, 255, a)
            r   = s["r"]
            c.create_oval(s["x"]-r, s["y"]-r, s["x"]+r, s["y"]+r,
                          fill=col, outline="")

        # Meteors
        dead = []
        for m in self._meteors:
            m["life"] += 0.05
            m["x"]   += m["vx"]
            m["y"]   += m["vy"]
            alpha = max(0.0, 1.0 - m["life"])
            if alpha <= 0:
                dead.append(m); continue
            tail = m["len"] / 4
            col  = self._rgba(255, 210, 210, alpha * 0.85)
            c.create_line(m["x"]-m["vx"]*tail, m["y"]-m["vy"]*tail,
                          m["x"], m["y"], fill=col, width=1.5)
        for m in dead:
            self._meteors.remove(m)

        self._draw_filmstrip(c, y=0, sw=sw)
        self._draw_filmstrip(c, y=sh-24, sw=sw)
        self._draw_title(c, cx, sh)
        self._draw_clapperboard(c, cx, sh)
        self._draw_tip(c, cx, sh)
        self._draw_progress(c, cx, sh, sw)
        self._draw_dots(c, cx, sh)

    # ── Film strip ────────────────────────────────────────────────────────────
    def _draw_filmstrip(self, c, y, sw):
        h = 24
        c.create_rectangle(0, y, sw, y+h, fill="#111111", outline="")
        hole_w, hole_h = 16, 11
        gap    = 30
        offset = (self._t * 65) % (gap + hole_w)
        x = -hole_w + offset - (gap + hole_w)
        while x < sw + gap:
            c.create_rectangle(x, y+(h-hole_h)//2, x+hole_w, y+(h+hole_h)//2,
                               fill="#2a2a2a", outline="")
            x += hole_w + gap

    # ── Clapperboard cartoon ──────────────────────────────────────────────────
    def _draw_clapperboard(self, c, cx, sh):
        bounce = math.sin(self._t * 2.2) * 5
        cy     = int(sh * 0.42 + bounce)

        bw, bh = 230, 160
        bx = cx - bw // 2
        by = cy - bh // 2

        OL   = "#1a1010"   # outline tebal cartoon
        OLW  = 3           # outline width
        WHITE = "#f5f5f0"
        BLACK = "#1e1a1a"

        # ── Body shadow ───────────────────────────────────────────────────
        c.create_rectangle(bx+5, by+7, bx+bw+5, by+bh+7,
                           fill="#000000", outline="")

        # ── Body utama ────────────────────────────────────────────────────
        c.create_rectangle(bx, by, bx+bw, by+bh,
                           fill=WHITE, outline=OL, width=OLW)

        # ── Info rows di body ─────────────────────────────────────────────
        row1_y = by + bh * 0.32
        row2_y = by + bh * 0.62
        c.create_line(bx, row1_y, bx+bw, row1_y, fill=OL, width=2)
        c.create_line(bx, row2_y, bx+bw, row2_y, fill=OL, width=2)
        mid_x = bx + bw * 0.5
        c.create_line(mid_x, by, mid_x, row1_y, fill=OL, width=2)

        # Label SCENE: TAKE:
        c.create_text(bx + bw*0.25, by + bh*0.12,
                      text="SCENE:", fill=OL, font=("Arial", 9, "bold"), anchor="center")
        c.create_text(bx + bw*0.75, by + bh*0.12,
                      text="TAKE :", fill=OL, font=("Arial", 9, "bold"), anchor="center")

        # ── Display angka merah (timecode style) ──────────────────────────
        disp_x = bx + 14
        disp_y = int(row1_y + 6)
        disp_w = bw - 28
        disp_h = int(row2_y - row1_y - 12)
        c.create_rectangle(disp_x, disp_y, disp_x+disp_w, disp_y+disp_h,
                           fill=BLACK, outline=OL, width=2)

        # Timecode: MM.SS.FF berdasarkan progress
        total_sec = int(self._progress * 99)
        mm = total_sec // 60
        ss = total_sec % 60
        ff = int((self._t * 24) % 100)
        timecode = f"{mm:02d}.{ss:02d}.{ff:02d}."
        c.create_text(disp_x + disp_w//2, disp_y + disp_h//2,
                      text=timecode,
                      fill="#bc2c2c",
                      font=("Courier", int(disp_h * 0.65), "bold"),
                      anchor="center")

        # ── DATE row ──────────────────────────────────────────────────────
        c.create_text(bx + bw*0.65, by + bh*0.82,
                      text='          ©2026 CINEPHILE Archive',
                      fill=OL, font=("Arial", 8), anchor="center")

        # ── Outline body ──────────────────────────────────────────────────
        c.create_rectangle(bx, by, bx+bw, by+bh,
                           fill="", outline=OL, width=OLW)

        # ── Clapper arm (stripes hitam putih, outline tebal) ──────────────
        arm_w = bw
        arm_h = 36
        rad   = math.radians(-self._clap_angle)
        px    = float(bx)
        py    = float(by)

        def rot(ppx, ppy):
            dx, dy = ppx - px, ppy - py
            return (dx*math.cos(rad) - dy*math.sin(rad) + px,
                    dx*math.sin(rad) + dy*math.cos(rad) + py)

        # Stripe pairs
        n_stripes = 7
        for i in range(n_stripes):
            col = BLACK if i % 2 == 0 else WHITE
            sl  = px + i * (arm_w / n_stripes)
            sr  = sl + arm_w / n_stripes
            pts = [rot(sl, py), rot(sr, py),
                   rot(sr, py+arm_h), rot(sl, py+arm_h)]
            flat = [v for pt in pts for v in pt]
            c.create_polygon(flat, fill=col, outline="")

        # Outline tebal arm
        corners = [rot(px,py), rot(px+arm_w,py),
                   rot(px+arm_w,py+arm_h), rot(px,py+arm_h)]
        c.create_polygon([v for pt in corners for v in pt],
                         fill="", outline=OL, width=OLW)

        # Hinge circle
        c.create_oval(px-7, py-7, px+7, py+7,
                      fill="#888", outline=OL, width=2)

        # ── Bintang oranye muncul saat snap ──────────────────────────────
        if self._star_vis and self._star_scale > 0:
            sx   = bx - 38
            sy   = int(py - 10)
            fade = max(0.0, 1.0 - (self._star_scale / 2.5))
            size = int(18 * min(self._star_scale, 1.0))
            if size > 2:
                r, g, b = 255, 165, 0
                a = fade
                col  = self._rgba(r, g, b, a)
                col2 = self._rgba(255, 200, 50, a * 0.7)
                # Bintang 5 sudut sederhana pakai polygon
                pts5 = []
                for i in range(10):
                    angle = math.pi/2 + i * math.pi/5 * (-1 if i % 2 == 0 else 1)
                    # outer / inner radius bergantian
                    dist = size if i % 2 == 0 else size * 0.45
                    angle_rad = -math.pi/2 + i * (2*math.pi/10)
                    pts5.append(sx + dist * math.cos(angle_rad))
                    pts5.append(sy + dist * math.sin(angle_rad))
                c.create_polygon(pts5, fill=col, outline=col2, width=2)

                # Garis kecil di samping bintang
                lc = self._rgba(255, 180, 0, fade * 0.7)
                c.create_line(sx+size+4, sy-3, sx+size+14, sy-3,
                              fill=lc, width=2)
                c.create_line(sx+size+4, sy+4, sx+size+14, sy+4,
                              fill=lc, width=2)

        # Bounce shadow
        shadow_y = by + bh + 12
        c.create_oval(cx-90, shadow_y-5, cx+90, shadow_y+5,
                      fill="#0d0d0d", outline="")

    # ── Title ─────────────────────────────────────────────────────────────────
    def _draw_title(self, c, cx, sh):
        c.create_text(cx, sh*0.15,
                      text="CINEPHILE",
                      fill=TEXT_WHITE,
                      font=("Trebuchet MS", 50, "bold"),
                      anchor="center")
        c.create_text(cx, sh*0.15 + 46,
                      text="Curating cinema excellence for your personal collection",
                      fill="#AAAAAA",
                      font=("Trebuchet MS", 14),
                      anchor="center")

    # ── Tip ───────────────────────────────────────────────────────────────────
    def _draw_tip(self, c, cx, sh):
        c.create_text(cx, sh*0.74,
                      text=self._tip_text,
                      fill="#AAAAAA",
                      font=("Trebuchet MS", 12),
                      anchor="center")

    # ── Progress bar pill ─────────────────────────────────────────────────────
    def _draw_progress(self, c, cx, sh, sw):
        pct   = self._progress
        bar_w = int(sw * 0.52)
        bar_h = 18
        r     = bar_h // 2
        bx    = cx - bar_w // 2
        by    = int(sh * 0.79)

        self._pill(c, bx, by, bar_w, bar_h, PROGRESS_BG)
        fill_w = max(bar_h, int(bar_w * pct))
        self._pill(c, bx, by, fill_w, bar_h, ACCENT)
        if fill_w > bar_h:
            c.create_rectangle(bx+r, by+2, bx+fill_w-r, by+5,
                               fill=ACCENT2, outline="")

        c.create_text(cx, by + bar_h + 16,
                      text=f"{int(pct*100)}%",
                      fill="#AAAAAA",
                      font=("Courier", 12, "bold"),
                      anchor="center")

    def _pill(self, c, x, y, w, h, color):
        r = h // 2
        c.create_oval(x, y, x+h, y+h, fill=color, outline="")
        c.create_oval(x+w-h, y, x+w, y+h, fill=color, outline="")
        c.create_rectangle(x+r, y, x+w-r, y+h, fill=color, outline="")

    # ── 3 dots bulat ─────────────────────────────────────────────────────────
    def _draw_dots(self, c, cx, sh):
        by    = int(sh * 0.79)
        dot_y = by + 18 + 38
        for dx, dr, phase in [(cx-22, 5, 0.0), (cx, 7, 0.7), (cx+22, 5, 1.4)]:
            pulse  = (math.sin(self._t * 3 - phase) + 1) / 2
            bright = 0.2 + 0.8 * pulse
            rv = int(141 * bright + 26 * (1-bright))
            gv = int(40  * bright + 26 * (1-bright))
            bv = int(40  * bright + 26 * (1-bright))
            c.create_oval(dx-dr, dot_y-dr, dx+dr, dot_y+dr,
                          fill=f"#{rv:02x}{gv:02x}{bv:02x}", outline="")

    # ── Finish ────────────────────────────────────────────────────────────────
    def _finish(self):
        self._running = False
        self.destroy()
        if self.on_done:
            self.on_done()


def show_loading(duration_ms=4000, on_done=None):
    app = CinephileLoadingScreen(duration_ms=duration_ms, on_done=on_done)
    app.mainloop()


if __name__ == "__main__":
    show_loading(duration_ms=5000, on_done=lambda: print("Done!"))
