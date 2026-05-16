import customtkinter as ctk
import os
import json
import re
import math
import random
import time
from tkinter import messagebox, Canvas
from PIL import Image, ImageDraw, ImageOps

# ─── DESIGN TOKENS (matching HTML) ────────────────────────────────────────────
ACCENT       = "#8d2827"
ACCENT_HOVER = "#b03535"
BG_DARK      = "#1a1a1a"
BG_CARD      = "#0d0d0d"
BORDER_COLOR = "#1a1a1a"
TEXT_PRIMARY = "#ffffff"
TEXT_MUTED   = "#888899"   # was #ffffff66 — tkinter no alpha hex
TEXT_LINK    = "#c45050"
COLOR_VALID  = "#4ade80"
COLOR_INVALID= "#f87171"

ENTRY_STYLE = {
    "fg_color"         : "#111111",
    "border_color"     : "#1a1a1a",
    "border_width"     : 1,
    "text_color"       : TEXT_PRIMARY,
    "placeholder_text_color": TEXT_MUTED,
    "corner_radius"    : 12,
}

FONT_TITLE  = ("Montserrat", 30, "bold")
FONT_BODY   = ("Montserrat", 13)
FONT_SMALL  = ("Montserrat", 11)
FONT_LABEL  = ("Montserrat", 12)
FONT_BTN    = ("Montserrat", 14, "bold")

# ─── STAR CANVAS WIDGET ───────────────────────────────────────────────────────
class StarCanvas(Canvas):
    """Animated starfield + meteor shower background."""

    def __init__(self, master, **kw):
        super().__init__(master, bg=BG_DARK, highlightthickness=0, **kw)
        self._stars   = []
        self._meteors = []
        self._t       = 0
        self._running = True
        self.bind("<Configure>", self._on_resize)
        self.after(50, self._init_stars)

    def _on_resize(self, e=None):
        self._init_stars()

    def _init_stars(self):
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 2 or h < 2:
            return
        count = max(30, (w * h) // 5500)
        self._stars = [
            {
                "x"    : random.random() * w,
                "y"    : random.random() * h,
                "r"    : random.uniform(0.3, 1.3),
                "alpha": random.uniform(0.1, 0.55),
                "phase": random.uniform(0, math.pi * 2),
                "speed": random.uniform(0.005, 0.022),
            }
            for _ in range(count)
        ]

    def spawn_meteors(self, n=3):
        w = self.winfo_width()
        h = self.winfo_height()
        for _ in range(n):
            self._meteors.append({
                "x"   : random.random() * w * 0.8,
                "y"   : random.random() * h * 0.4,
                "vx"  : random.uniform(4, 7),
                "vy"  : random.uniform(2, 4),
                "len" : random.randint(50, 110),
                "life": 0.0,
            })

    def _loop(self):
        if not self._running:
            return
        self.delete("star")
        self._t += 0.016
        w = self.winfo_width()
        h = self.winfo_height()

        # Stars
        for s in self._stars:
            tw  = math.sin(self._t * s["speed"] * 60 + s["phase"])
            a   = s["alpha"] * (0.4 + 0.6 * ((tw + 1) / 2))
            col = self._rgba(255, 255, 255, a)
            r   = s["r"]
            self.create_oval(
                s["x"] - r, s["y"] - r, s["x"] + r, s["y"] + r,
                fill=col, outline="", tags="star"
            )

        # Meteors
        dead = []
        for m in self._meteors:
            m["life"] += 0.05
            m["x"] += m["vx"]
            m["y"] += m["vy"]
            alpha = max(0.0, 1.0 - m["life"])
            if alpha <= 0:
                dead.append(m)
                continue
            tail = m["len"] / 4
            x1   = m["x"] - m["vx"] * tail
            y1   = m["y"] - m["vy"] * tail
            col  = self._rgba(255, 210, 210, alpha * 0.85)
            self.create_line(x1, y1, m["x"], m["y"],
                             fill=col, width=1.5, tags="star")
        for m in dead:
            self._meteors.remove(m)

        self.after(16, self._loop)

    def _draw_orb(self, cx, cy, r, hex_col, alpha):
        steps = 12
        for i in range(steps, 0, -1):
            frac = i / steps
            a    = alpha * frac * frac
            col  = self._blend_hex(hex_col, a)
            rr   = r * frac
            self.create_oval(cx - rr, cy - rr, cx + rr, cy + rr,
                             fill=col, outline="", tags="star")

    @staticmethod
    def _blend_hex(hex_color, alpha):
        hex_color = hex_color.lstrip("#")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        br = int(r * alpha + 26 * (1 - alpha))
        bg = int(g * alpha + 26 * (1 - alpha))
        bb = int(b * alpha + 26 * (1 - alpha))
        return f"#{br:02x}{bg:02x}{bb:02x}"

    @staticmethod
    def _rgba(r, g, b, a):
        rr = int(r * a + 26 * (1 - a))
        gg = int(g * a + 26 * (1 - a))
        bb = int(b * a + 26 * (1 - a))
        return f"#{rr:02x}{gg:02x}{bb:02x}"

    def start(self):
        self._running = True
        self.after(100, self._loop)
        self._auto_spawn()

    def _auto_spawn(self):
        """Auto-spawn meteors every ~2.8s like the HTML version."""
        if not self._running:
            return
        self.spawn_meteors(1)
        self.after(2800, self._auto_spawn)

    def stop(self):
        self._running = False


# ─── USER DATABASE ─────────────────────────────────────────────────────────────
class UserDB:
    def __init__(self, db_file="users.json", session_file="session.json"):
        self.db_file      = db_file
        self.session_file = session_file
        if not os.path.exists(self.db_file):
            with open(self.db_file, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def _load(self):
        with open(self.db_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data):
        with open(self.db_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def register_user(self, full_name, username, email, password, gender, dob):
        data = self._load()
        if username in data:
            return False, "Username already taken!"
        data[username] = {
            "full_name": full_name, "email": email, "password": password,
            "gender": gender, "dob": dob, "bio": "", "avatar_path": None
        }
        self._save(data)
        return True, "Account created successfully!"

    def login_user(self, username, password):
        data = self._load()
        if username in data and data[username]["password"] == password:
            self.save_session(username)
            return True, "Login successful!"
        return False, "Incorrect username or password."

    def get_user_info(self, username):
        return self._load().get(username)

    def update_profile_info(self, username, full_name, email, bio, gender, dob):
        data = self._load()
        if username in data:
            data[username].update({"full_name": full_name, "email": email,
                                   "bio": bio, "gender": gender, "dob": dob})
            self._save(data)
            return True, "Profile updated!"
        return False, "Failed to update profile."

    def update_avatar_path(self, username, file_path):
        data = self._load()
        if username in data:
            data[username]["avatar_path"] = file_path
            self._save(data)
            return True
        return False

    def change_password_secure(self, username, old_pw, new_pw):
        data = self._load()
        if username in data:
            if data[username]["password"] == old_pw:
                data[username]["password"] = new_pw
                self._save(data)
                return True, "Password changed successfully!"
            return False, "Old password is incorrect."
        return False, "User not found."

    def delete_user(self, username):
        data = self._load()
        if username in data:
            del data[username]
            self._save(data)
            return True
        return False

    def save_session(self, username):
        with open(self.session_file, "w") as f:
            json.dump({"active_user": username}, f)


# ─── SHARED HELPERS ────────────────────────────────────────────────────────────
def _get_logo(size=(80, 80)):
    """Load Cinephile.png as circular CTkImage, fallback to text label data."""
    path = "Cinephile.png"
    try:
        if os.path.exists(path):
            img  = Image.open(path).convert("RGBA")
            img  = ImageOps.fit(img, size, centering=(0.5, 0.5))
            mask = Image.new("L", size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + size, fill=255)
            out  = Image.new("RGBA", size, (0, 0, 0, 0))
            out.paste(img, (0, 0), mask)
            return ctk.CTkImage(out, size=size)
    except Exception as e:
        print(f"Logo error: {e}")
    return None


def _logo_header(parent, size=(80, 80)):
    img = _get_logo(size)
    if img:
        ctk.CTkLabel(parent, image=img, text="").pack(pady=(4, 12))
    else:
        # Fallback: white circle with "C"
        ctk.CTkLabel(parent, text="C",
                     width=size[0], height=size[1],
                     corner_radius=size[0] // 2,
                     fg_color="#ffffff",
                     text_color="#1a1a1a",
                     font=("Georgia", 36, "bold")).pack(pady=(4, 12))


def _star_btn(parent, text, command, width=300, height=46):
    """Primary crimson action button."""
    return ctk.CTkButton(
        parent, text=text, command=command,
        fg_color=ACCENT, hover_color=ACCENT_HOVER,
        width=width, height=height,
        corner_radius=12, font=FONT_BTN,
        text_color=TEXT_PRIMARY,
    )


def _ghost_btn(parent, text, command, width=220, height=36):
    """Secondary ghost button."""
    return ctk.CTkButton(
        parent, text=text, command=command,
        fg_color="transparent",
        border_color=BORDER_COLOR, border_width=1,
        hover_color="#1e1e26",
        width=width, height=height,
        corner_radius=12, font=FONT_SMALL,
        text_color=TEXT_MUTED,
    )


def _entry(parent, placeholder, show=None, width=300, height=44):
    kw = ENTRY_STYLE.copy()
    kw["width"]  = width
    kw["height"] = height
    if show:
        kw["show"] = show
    return ctk.CTkEntry(parent, placeholder_text=placeholder, **kw)


def _error_label(parent):
    return ctk.CTkLabel(parent, text="", text_color=COLOR_INVALID,
                        font=FONT_SMALL)


def _validate_password(pw):
    return (len(pw) >= 8,
            bool(re.search(r'[A-Z]', pw)),
            bool(re.search(r'\d', pw)))


# ─── SCENE BUILDER ─────────────────────────────────────────────────────────────
def _build_scene(master, card_w, card_h):
    """Clear master, place animated starfield + centred card. Returns (star_canvas, card_inner)."""
    for w in master.winfo_children():
        w.destroy()

    # Make master fill its parent via pack (compatible with main.py container)
    master.pack(fill="both", expand=True)
    master.update_idletasks()

    star = StarCanvas(master)
    star.place(x=0, y=0, relwidth=1, relheight=1)
    star.start()

    card = ctk.CTkFrame(master,
                        fg_color=BG_CARD,
                        corner_radius=24,
                        border_width=1,
                        border_color=BORDER_COLOR,
                        width=card_w, height=card_h)
    card.place(relx=0.5, rely=0.5, anchor="center")
    card.pack_propagate(False)

    inner = ctk.CTkFrame(card, fg_color="transparent")
    inner.pack(fill="both", expand=True, padx=32, pady=24)
    return star, inner


# ─── AUTH PAGES ────────────────────────────────────────────────────────────────
class AuthPages:
    def __init__(self, master, app):
        self.master      = master
        self.app         = app
        self.db          = UserDB()
        self._star_canvas = None

    def _stop_stars(self):
        if self._star_canvas:
            try:
                self._star_canvas.stop()
            except Exception:
                pass

    # ── Welcome ──────────────────────────────────────────────────────────────
    def render_welcome_page(self):
        self._stop_stars()
        self.master.master.geometry("1100x850")
        star, inner = _build_scene(self.master, 420, 520)
        self._star_canvas = star

        _logo_header(inner, (90, 90))

        ctk.CTkLabel(inner, text="Welcome To Cinephile",
                     font=("Georgia", 26, "bold"),
                     text_color=TEXT_PRIMARY).pack(pady=(0, 6))
        ctk.CTkLabel(inner, text="Discover Movies Beyond the Surface",
                     font=FONT_BODY, text_color=TEXT_MUTED).pack(pady=(0, 28))

        _star_btn(inner, "Log In", self.render_login, width=320).pack(pady=(0, 14))

        row = ctk.CTkFrame(inner, fg_color="transparent")
        row.pack()
        ctk.CTkLabel(row, text="Don't have an account?  ",
                     font=FONT_SMALL, text_color=TEXT_MUTED).pack(side="left")
        lnk = ctk.CTkLabel(row, text="Create one",
                            font=(FONT_SMALL[0], FONT_SMALL[1], "bold"),
                            text_color=TEXT_PRIMARY, cursor="hand2")
        lnk.pack(side="left")
        lnk.bind("<Button-1>", lambda e: self.render_register())

    # ── Login ─────────────────────────────────────────────────────────────────
    def render_login(self):
        self._stop_stars()
        self.master.master.geometry("1100x850")
        star, inner = _build_scene(self.master, 400, 620)
        self._star_canvas = star

        _logo_header(inner)

        ctk.CTkLabel(inner, text="Log In Cinephile",
                     font=FONT_TITLE, text_color=TEXT_PRIMARY).pack(pady=(0, 18))

        self._err = _error_label(inner)
        self._err.pack(pady=(0, 6))

        self.l_user = _entry(inner, "Username")
        self.l_user.pack(pady=8)

        self.l_pass = _entry(inner, "Password", show="*")
        self.l_pass.pack(pady=8)

        # Show-password row
        sp_var = ctk.BooleanVar(value=False)
        cb_row = ctk.CTkFrame(inner, fg_color="transparent")
        cb_row.pack(fill="x", padx=4, pady=(2, 0))
        ctk.CTkCheckBox(cb_row, text="Show Password",
                        variable=sp_var, font=FONT_SMALL,
                        text_color=TEXT_MUTED,
                        checkbox_width=15, checkbox_height=15,
                        checkmark_color=TEXT_PRIMARY,
                        fg_color=ACCENT, hover_color=ACCENT_HOVER,
                        command=lambda: self._toggle(self.l_pass, sp_var)
                        ).pack(side="left")

        rm_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(inner, text="Remember Me",
                        variable=rm_var, font=FONT_SMALL,
                        text_color=TEXT_MUTED,
                        checkbox_width=15, checkbox_height=15,
                        checkmark_color=TEXT_PRIMARY,
                        fg_color=ACCENT, hover_color=ACCENT_HOVER,
                        ).pack(pady=10)

        btn = _star_btn(inner, "Log in", self._handle_login, width=320)
        btn.pack(pady=(8, 14))

        # Divider
        div = ctk.CTkFrame(inner, height=1, fg_color=BORDER_COLOR)
        div.pack(fill="x", pady=4)

        links = ctk.CTkFrame(inner, fg_color="transparent")
        links.pack(pady=8)

        self._link(links, "Don't have an account?  ", "Create one",
                   self.render_register)
        self._link(links, "", "Forgot your password?",
                   self.render_forgot_password)

    def _handle_login(self):
        un = self.l_user.get().strip()
        pw = self.l_pass.get().strip()
        ok, msg = self.db.login_user(un, pw)
        if ok:
            self._star_canvas.spawn_meteors(6)
            self.master.after(400, lambda: self._on_login_success(un))
        else:
            self._err.configure(text=msg)

    def _on_login_success(self, un):
        self.app.username = un
        self.app.show_welcome_transition(un)

    # ── Register ──────────────────────────────────────────────────────────────
    def render_register(self):
        self._stop_stars()
        self.master.master.geometry("1200x1020")
        star, inner = _build_scene(self.master, 520, 800)
        self._star_canvas = star

        _logo_header(inner)
        ctk.CTkLabel(inner, text="Create Account",
                     font=FONT_TITLE, text_color=TEXT_PRIMARY).pack(pady=(0, 14))

        self._reg_err = _error_label(inner)
        self._reg_err.pack(pady=(0, 4))

        self.r_name  = _entry(inner, "Full Name", width=360)
        self.r_name.pack(pady=5)

        self.r_user  = _entry(inner, "Username", width=360)
        self.r_user.pack(pady=5)

        self.r_email = _entry(inner, "Email", width=360)
        self.r_email.pack(pady=5)

        # Gender row
        gen_row = ctk.CTkFrame(inner, fg_color="transparent")
        gen_row.pack(pady=5, fill="x")
        ctk.CTkLabel(gen_row, text="Gender:", font=FONT_LABEL,
                     text_color=TEXT_MUTED).pack(side="left", padx=(0, 10))
        self.r_gender = ctk.CTkSegmentedButton(
            gen_row, values=["Male", "Female", "Other"],
            selected_color=ACCENT, selected_hover_color=ACCENT_HOVER,
            unselected_color="#1a1a1a", unselected_hover_color="#222222",
            text_color=TEXT_PRIMARY, font=FONT_SMALL,
        )
        self.r_gender.pack(side="left")
        self.r_gender.set("Male")

        self.r_dob  = _entry(inner, "Date of Birth (DD-MM-YYYY)", width=360)
        self.r_dob.pack(pady=5)

        self.r_pass = _entry(inner, "Password", show="*", width=360)
        self.r_pass.pack(pady=5)
        self.r_pass.bind("<KeyRelease>", self._validate_reg_pw)

        sp_var = ctk.BooleanVar()
        ctk.CTkCheckBox(inner, text="Show Password",
                        variable=sp_var, font=FONT_SMALL,
                        text_color=TEXT_MUTED,
                        checkbox_width=10, checkbox_height=10,
                        fg_color=ACCENT, hover_color=ACCENT_HOVER,
                        command=lambda: self._toggle(self.r_pass, sp_var)
                        ).pack(anchor="w", padx=4, pady=(0, 4))

        # Password criteria
        crit = ctk.CTkFrame(inner, fg_color="transparent")
        crit.pack(pady=2, anchor="w")
        self._c_len   = ctk.CTkLabel(crit, text="• Minimum 8 characters",         font=FONT_SMALL, text_color=TEXT_MUTED)
        self._c_upper = ctk.CTkLabel(crit, text="• At least 1 uppercase (A-Z)",    font=FONT_SMALL, text_color=TEXT_MUTED)
        self._c_num   = ctk.CTkLabel(crit, text="• At least 1 number (0-9)",       font=FONT_SMALL, text_color=TEXT_MUTED)
        for lbl in (self._c_len, self._c_upper, self._c_num):
            lbl.pack(anchor="w")

        self._reg_pw_ok = False
        self._reg_btn = _star_btn(inner, "Create Account", self._handle_register, width=320)
        self._reg_btn.configure(state="disabled", fg_color="#3d1212")
        self._reg_btn.pack(pady=14)


       # Divider
        ctk.CTkFrame(inner, height=1, fg_color=BORDER_COLOR).pack(fill="x", pady=6)

        _ghost_btn(inner, "Back to Login", self._go_login).pack()

    def _validate_reg_pw(self, _=None):
        v = _validate_password(self.r_pass.get())
        self._c_len.configure(text_color=COLOR_VALID if v[0] else TEXT_MUTED)
        self._c_upper.configure(text_color=COLOR_VALID if v[1] else TEXT_MUTED)
        self._c_num.configure(text_color=COLOR_VALID if v[2] else TEXT_MUTED)
        self._reg_pw_ok = all(v)
        self._reg_btn.configure(
            state="normal" if self._reg_pw_ok else "disabled",
            fg_color=ACCENT if self._reg_pw_ok else "#3d1212"
        )

    def _handle_register(self):
        fn  = self.r_name.get().strip()
        un  = self.r_user.get().strip()
        em  = self.r_email.get().strip()
        pw  = self.r_pass.get()
        gen = self.r_gender.get()
        dob = self.r_dob.get().strip()

        if not all([fn, un, em, pw, gen, dob]):
            return self._reg_err.configure(text="Please fill in all fields.")
        if not self._reg_pw_ok:
            return
        if not re.match(r'^\d{2}-\d{2}-\d{4}$', dob):
            return self._reg_err.configure(text="Invalid date format. Use DD-MM-YYYY.")

        ok, msg = self.db.register_user(fn, un, em, pw, gen, dob)
        if ok:
            self._star_canvas.spawn_meteors(5)
            self.master.after(400, self._go_login)
        else:
            self._reg_err.configure(text=msg)

    # ── Forgot Password ───────────────────────────────────────────────────────
    def render_forgot_password(self):
        self._stop_stars()
        self.master.master.geometry("1100x900")
        star, inner = _build_scene(self.master, 440, 740)
        self._star_canvas = star

        _logo_header(inner)
        ctk.CTkLabel(inner, text="Forgot Password",
                     font=FONT_TITLE, text_color=TEXT_PRIMARY).pack(pady=(0, 6))
        ctk.CTkLabel(inner, text="Reset your password below",
                     font=FONT_SMALL, text_color=TEXT_MUTED).pack(pady=(0, 14))

        self._fp_err = _error_label(inner)
        self._fp_err.pack(pady=(0, 6))

        self.f_user    = _entry(inner, "Registered Username", width=340)
        self.f_user.pack(pady=8)

        self.f_new_pw  = _entry(inner, "New Password", show="*", width=340)
        self.f_new_pw.pack(pady=8)
        self.f_new_pw.bind("<KeyRelease>", self._validate_fp_pw)

        # Criteria
        crit = ctk.CTkFrame(inner, fg_color="transparent")
        crit.pack(pady=2, anchor="w")
        self._fp_len   = ctk.CTkLabel(crit, text="• Minimum 8 characters",         font=FONT_SMALL, text_color=TEXT_MUTED)
        self._fp_upper = ctk.CTkLabel(crit, text="• At least 1 uppercase (A-Z)",    font=FONT_SMALL, text_color=TEXT_MUTED)
        self._fp_num   = ctk.CTkLabel(crit, text="• At least 1 number (0-9)",       font=FONT_SMALL, text_color=TEXT_MUTED)
        for lbl in (self._fp_len, self._fp_upper, self._fp_num):
            lbl.pack(anchor="w")

        self.f_conf_pw = _entry(inner, "Confirm New Password", show="*", width=340)
        self.f_conf_pw.pack(pady=8)

        sp_var = ctk.BooleanVar()
        def _toggle_fp():
            show = "" if sp_var.get() else "*"
            self.f_new_pw.configure(show=show)
            self.f_conf_pw.configure(show=show)

        ctk.CTkCheckBox(inner, text="Show Passwords",
                        variable=sp_var, font=FONT_SMALL,
                        text_color=TEXT_MUTED,
                        checkbox_width=15, checkbox_height=15,
                        fg_color=ACCENT, hover_color=ACCENT_HOVER,
                        command=_toggle_fp
                        ).pack(anchor="w", padx=4, pady=(0, 8))

        self._fp_pw_ok = False
        self._fp_btn   = _star_btn(inner, "Recover & Save Password",
                                   self._execute_forgot_pw, width=340)
        self._fp_btn.configure(state="disabled", fg_color="#3d1212")
        self._fp_btn.pack(pady=12)

        # Divider
        ctk.CTkFrame(inner, height=1, fg_color=BORDER_COLOR).pack(fill="x", pady=6)

        _ghost_btn(inner, "Back to Login", self._go_login).pack()

    def _validate_fp_pw(self, _=None):
        v = _validate_password(self.f_new_pw.get())
        self._fp_len.configure(text_color=COLOR_VALID if v[0] else TEXT_MUTED)
        self._fp_upper.configure(text_color=COLOR_VALID if v[1] else TEXT_MUTED)
        self._fp_num.configure(text_color=COLOR_VALID if v[2] else TEXT_MUTED)
        self._fp_pw_ok = all(v)
        self._fp_btn.configure(
            state="normal" if self._fp_pw_ok else "disabled",
            fg_color=ACCENT if self._fp_pw_ok else "#3d1212"
        )

    def _execute_forgot_pw(self):
        un      = self.f_user.get().strip()
        new_pw  = self.f_new_pw.get()
        conf_pw = self.f_conf_pw.get()

        if not un:
            return self._fp_err.configure(text="Username cannot be empty!")
        if new_pw != conf_pw:
            return self._fp_err.configure(text="Passwords do not match!")

        users = self.db._load()
        if un not in users:
            return self._fp_err.configure(text="Username not found in the system!")

        users[un]["password"] = new_pw
        self.db._save(users)

        self._star_canvas.spawn_meteors(6)
        self.master.after(600, lambda: (
            messagebox.showinfo("Success", f"Password for @{un} has been updated!\nYou can now log in."),
            self._go_login()
        ))

    # ── Shared helpers ────────────────────────────────────────────────────────
    @staticmethod
    def _toggle(entry, var):
        entry.configure(show="" if var.get() else "*")

    def _go_login(self):
        self.master.master.geometry("1100x850")
        self.render_login()

    @staticmethod
    def _link(parent, prefix, link_text, command):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(pady=3)
        if prefix:
            ctk.CTkLabel(row, text=prefix, font=FONT_SMALL,
                         text_color=TEXT_MUTED).pack(side="left")
        lbl = ctk.CTkLabel(row, text=link_text, font=FONT_SMALL,
                           text_color="#c45050", cursor="hand2")
        lbl.pack(side="left")
        lbl.bind("<Button-1>", lambda e: command())