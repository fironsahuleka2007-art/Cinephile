import customtkinter as ctk
import os
import json
from PIL import Image, ImageDraw
from styles import ENTRY_STYLE, TEXT_GRAY

# ==========================================
# 1. LOGIKA DATABASE & SESSION (JSON)
# ==========================================
class UserDB:
    def __init__(self, db_file="users.json", session_file="session.json"):
        self.db_file = db_file
        self.session_file = session_file
        
        # Buat file json kosong jika belum ada
        if not os.path.exists(self.db_file):
            with open(self.db_file, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def _load_data(self):
        with open(self.db_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_data(self, data):
        with open(self.db_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    # --- Fitur Autentikasi ---
    def register_user(self, full_name, username, email, password):
        data = self._load_data()
        if username in data:
            return False, "Username sudah terdaftar!"
        
        data[username] = {
            "full_name": full_name,
            "email": email,
            "password": password
        }
        self._save_data(data)
        return True, "Akun berhasil dibuat!"

    def login_user(self, username, password):
        data = self._load_data()
        if username in data and data[username]["password"] == password:
            return True, "Login Berhasil!"
        return False, "Username atau Password salah!"

    def reset_password(self, username, new_password):
        data = self._load_data()
        if username not in data:
            return False, "Username tidak ditemukan!"
        
        data[username]["password"] = new_password
        self._save_data(data)
        return True, "Password berhasil diubah!"

    # --- Fitur Remember Me (Sesi) ---
    def save_session(self, username):
        with open(self.session_file, "w", encoding="utf-8") as f:
            json.dump({"active_user": username}, f)

    def get_session(self):
        if os.path.exists(self.session_file):
            with open(self.session_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("active_user")
        return None

    def clear_session(self):
        if os.path.exists(self.session_file):
            os.remove(self.session_file)


# ==========================================
# 2. UI AUTHENTICATION PAGES
# ==========================================
class AuthPages:
    def __init__(self, master, app):
        self.master = master
        self.app = app
        self.db = UserDB() # Inisialisasi Database

    def create_round_logo(self, container, size=130):
        logo_path = "Cinephile.png"
        if not os.path.exists(logo_path):
            ctk.CTkLabel(container, text="🎬", font=("Inter", 50)).pack(pady=(0, 10))
            return
        try:
            img = Image.open(logo_path).convert("RGBA")
            w, h = img.size
            min_dim = min(w, h)
            img = img.crop(((w-min_dim)//2, (h-min_dim)//2, (w+min_dim)//2, (h+min_dim)//2))
            img = img.resize((size-10, size-10), Image.LANCZOS)
            mask = Image.new("L", img.size, 0)
            ImageDraw.Draw(mask).ellipse((0, 0, img.size[0], img.size[1]), fill=255)
            img.putalpha(mask)
            final_img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            ImageDraw.Draw(final_img).ellipse((0, 0, size, size), fill="white")
            final_img.paste(img, (5, 5), img)
            img_icon = ctk.CTkImage(light_image=final_img, dark_image=final_img, size=(size, size))
            ctk.CTkLabel(container, image=img_icon, text="").pack(pady=(0, 20))
        except: pass

    # ------------------------------------------
    # HALAMAN LOGIN
    # ------------------------------------------
    def render_login(self):
        container = ctk.CTkFrame(self.master, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")
        self.create_round_logo(container, 140)
        ctk.CTkLabel(container, text="Log In Cinephile.", font=("Inter", 28, "bold")).pack(pady=(0, 20))
        
        self.login_user_entry = ctk.CTkEntry(container, placeholder_text="Username", **ENTRY_STYLE)
        self.login_user_entry.pack(pady=10)
        
        self.login_pass_entry = ctk.CTkEntry(container, placeholder_text="Password", show="*", **ENTRY_STYLE)
        self.login_pass_entry.pack(pady=10)
        
        # Checkbox Remember Me
        self.remember_var = ctk.IntVar(value=0)
        remember_cb = ctk.CTkCheckBox(container, text="Remember Me", variable=self.remember_var, 
                                    text_color=TEXT_GRAY, fg_color="#631d2a", hover_color="#4a151f")
        remember_cb.pack(pady=(0, 10))

        ctk.CTkButton(container, text="Log in", fg_color="#631d2a", hover_color="#4a151f", 
                    width=320, height=45, corner_radius=15, font=("Inter", 14, "bold"),
                    command=self._handle_login).pack(pady=(15, 25))
        
        reg_btn = ctk.CTkLabel(container, text="Don't have an account? Create one", cursor="hand2", text_color=TEXT_GRAY)
        reg_btn.pack(); reg_btn.bind("<Button-1>", lambda e: self.app.show_page("register"))

        forgot_btn = ctk.CTkLabel(container, text="Forgot your password?", cursor="hand2", text_color=TEXT_GRAY)
        forgot_btn.pack(); forgot_btn.bind("<Button-1>", lambda e: self.app.show_page("forgot_password"))

    def _handle_login(self):
        username = self.login_user_entry.get().strip()
        password = self.login_pass_entry.get().strip()

        if not username or not password:
            self.app.show_toast("Harap isi semua kolom!")
            return

        success, message = self.db.login_user(username, password)
        if success:
            if self.remember_var.get() == 1:
                self.db.save_session(username)
            self.app.show_toast(message, target="dashboard")
        else:
            self.app.show_toast(message)

    # ------------------------------------------
    # HALAMAN REGISTER
    # ------------------------------------------
    def render_register(self):
        container = ctk.CTkFrame(self.master, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")
        self.create_round_logo(container, 100)
        ctk.CTkLabel(container, text="Sign Up Cinephile.", font=("Inter", 26, "bold")).pack(pady=20)
        
        self.reg_entries = {}
        for f in ["Full Name", "Username", "Email", "Password"]:
            entry = ctk.CTkEntry(container, placeholder_text=f, show="*" if f=="Password" else "", **ENTRY_STYLE)
            entry.pack(pady=7)
            self.reg_entries[f] = entry
            
        ctk.CTkButton(container, text="Create Account", fg_color="#631d2a", hover_color="#4a151f",
                    width=320, height=45, corner_radius=15, font=("Inter", 14, "bold"),
                    command=self._handle_register).pack(pady=25)

        back_btn = ctk.CTkLabel(container, text="Already have an account? Log In", cursor="hand2", text_color=TEXT_GRAY)
        back_btn.pack(); back_btn.bind("<Button-1>", lambda e: self.app.show_page("login"))
        
    def _handle_register(self):
        fn = self.reg_entries["Full Name"].get().strip()
        un = self.reg_entries["Username"].get().strip()
        em = self.reg_entries["Email"].get().strip()
        pw = self.reg_entries["Password"].get().strip()

        if not all([fn, un, em, pw]):
            self.app.show_toast("Harap isi semua kolom!")
            return

        success, message = self.db.register_user(fn, un, em, pw)
        if success:
            self.app.show_toast(message, target="login")
        else:
            self.app.show_toast(message)

    # ------------------------------------------
    # HALAMAN FORGOT PASSWORD
    # ------------------------------------------
    def render_forgot_password(self):
        container = ctk.CTkFrame(self.master, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")
        self.create_round_logo(container, 100)
        ctk.CTkLabel(container, text="Forgot Password?", font=("Inter", 26, "bold")).pack(pady=20)
        
        self.fg_user = ctk.CTkEntry(container, placeholder_text="Enter username", **ENTRY_STYLE)
        self.fg_user.pack(pady=10)
        self.fg_pass1 = ctk.CTkEntry(container, placeholder_text="Enter new password", show="*", **ENTRY_STYLE)
        self.fg_pass1.pack(pady=10)
        self.fg_pass2 = ctk.CTkEntry(container, placeholder_text="Confirm new password", show="*", **ENTRY_STYLE)
        self.fg_pass2.pack(pady=10)
        
        ctk.CTkButton(container, text="Reset Password", fg_color="#631d2a", hover_color="#4a151f",
                    width=320, height=45, corner_radius=15, font=("Inter", 14, "bold"),
                    command=self._handle_forgot_password).pack(pady=25)

        back_btn = ctk.CTkLabel(container, text="Back to Login", cursor="hand2", text_color=TEXT_GRAY)
        back_btn.pack(); back_btn.bind("<Button-1>", lambda e: self.app.show_page("login"))

    def _handle_forgot_password(self):
        un = self.fg_user.get().strip()
        p1 = self.fg_pass1.get().strip()
        p2 = self.fg_pass2.get().strip()

        if not all([un, p1, p2]):
            self.app.show_toast("Harap isi semua kolom!")
            return

        if p1 != p2:
            self.app.show_toast("Password tidak sama!")
            return

        success, message = self.db.reset_password(un, p1)
        if success:
            self.app.show_toast(message, target="login")
        else:
            self.app.show_toast(message)