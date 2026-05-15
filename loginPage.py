import customtkinter as ctk
import os
import json
from PIL import Image
from styles import ENTRY_STYLE, TEXT_GRAY

class UserDB:
    def __init__(self, db_file="users.json", session_file="session.json"):
        self.db_file = db_file
        self.session_file = session_file
        if not os.path.exists(self.db_file):
            with open(self.db_file, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def _load_data(self):
        with open(self.db_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_data(self, data):
        with open(self.db_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def register_user(self, full_name, username, email, password):
        data = self._load_data()
        if username in data: return False, "Username sudah terdaftar!"
        data[username] = {"full_name": full_name, "email": email, "password": password}
        self._save_data(data)
        return True, "Akun berhasil dibuat!"

    def login_user(self, username, password):
        data = self._load_data()
        if username in data and data[username]["password"] == password:
            return True, "Login Berhasil!"
        return False, "Username atau Password salah!"

    def reset_password(self, username, new_password):
        data = self._load_data()
        if username not in data: return False, "Username tidak ditemukan!"
        data[username]["password"] = new_password
        self._save_data(data)
        return True, "Password berhasil diubah!"

    def save_session(self, username):
        with open(self.session_file, "w", encoding="utf-8") as f:
            json.dump({"active_user": username, "username": username}, f)

class AuthPages:
    def __init__(self, master, app):
        self.master = master
        self.app = app
        self.db = UserDB()
        self.logo_path = os.path.join("assets", "logo", "Cinephile.png")

    def create_round_logo(self, container, size=130):
        if not os.path.exists(self.logo_path):
            ctk.CTkLabel(container, text="🎬", font=("Inter", 50)).pack(pady=(0, 10))
            return
        try:
            img = ctk.CTkImage(Image.open(self.logo_path), size=(size, size))
            ctk.CTkLabel(container, text="", image=img).pack(pady=(0, 10))
        except:
            ctk.CTkLabel(container, text="🎬", font=("Inter", 50)).pack(pady=(0, 10))

    def _clear_master(self):
        for widget in self.master.winfo_children(): widget.destroy()

    def render_login(self):
        self._clear_master()
        container = ctk.CTkFrame(self.master, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        self.create_round_logo(container)
        ctk.CTkLabel(container, text="Welcome back!", font=("Arial Black", 28, "bold"), text_color="white").pack(pady=(0,5))
        ctk.CTkLabel(container, text="Please enter your details", font=("Inter", 15), text_color=TEXT_GRAY).pack(pady=(0, 20))
        
        self.l_user = ctk.CTkEntry(container, placeholder_text="Username", **ENTRY_STYLE)
        self.l_user.pack(pady=10)
        self.l_pass = ctk.CTkEntry(container, placeholder_text="Password", show="*", **ENTRY_STYLE)
        self.l_pass.pack(pady=10)
        
        fg_btn = ctk.CTkLabel(container, text="Forgot Password?", cursor="hand2", font=("Inter", 13), text_color=TEXT_GRAY)
        fg_btn.pack(anchor="e", padx=20)
        fg_btn.bind("<Button-1>", lambda e: self.render_forgot_password())
        
        self.error_lbl = ctk.CTkLabel(container, text="", text_color="#E53935", font=("Inter", 13, "bold"))
        self.error_lbl.pack(pady=5)

        ctk.CTkButton(container, text="Log In", fg_color="#E53935", hover_color="#C62828", width=340, height=48, corner_radius=15, font=("Inter", 15, "bold"), command=self._handle_login).pack(pady=(5, 25))
        
        b_frame = ctk.CTkFrame(container, fg_color="transparent")
        b_frame.pack()
        ctk.CTkLabel(b_frame, text="Don't have an account? ", text_color=TEXT_GRAY, font=("Inter", 13)).pack(side="left")
        reg_btn = ctk.CTkLabel(b_frame, text="Sign up", text_color="white", cursor="hand2", font=("Inter", 13, "bold"))
        reg_btn.pack(side="left")
        reg_btn.bind("<Button-1>", lambda e: self.app.show_page("register"))

    def render_register(self):
        self._clear_master()
        container = ctk.CTkFrame(self.master, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        self.create_round_logo(container, size=100)
        ctk.CTkLabel(container, text="Create Account", font=("Arial Black", 28, "bold"), text_color="white").pack(pady=(0, 20))
        
        self.r_name = ctk.CTkEntry(container, placeholder_text="Full Name", **ENTRY_STYLE); self.r_name.pack(pady=8)
        self.r_user = ctk.CTkEntry(container, placeholder_text="Username", **ENTRY_STYLE); self.r_user.pack(pady=8)
        self.r_email = ctk.CTkEntry(container, placeholder_text="Email", **ENTRY_STYLE); self.r_email.pack(pady=8)
        self.r_pass = ctk.CTkEntry(container, placeholder_text="Password", show="*", **ENTRY_STYLE); self.r_pass.pack(pady=8)
        
        self.error_lbl = ctk.CTkLabel(container, text="", text_color="#E53935", font=("Inter", 13, "bold"))
        self.error_lbl.pack(pady=5)
        
        ctk.CTkButton(container, text="Sign Up", fg_color="#E53935", hover_color="#C62828", width=340, height=48, corner_radius=15, font=("Inter", 15, "bold"), command=self._handle_register).pack(pady=(5, 25))
        b_frame = ctk.CTkFrame(container, fg_color="transparent")
        b_frame.pack()
        ctk.CTkLabel(b_frame, text="Already have an account? ", text_color=TEXT_GRAY, font=("Inter", 13)).pack(side="left")
        log_btn = ctk.CTkLabel(b_frame, text="Log in", text_color="white", cursor="hand2", font=("Inter", 13, "bold"))
        log_btn.pack(side="left")
        log_btn.bind("<Button-1>", lambda e: self.app.show_page("login"))

    def render_forgot_password(self):
        self._clear_master()
        container = ctk.CTkFrame(self.master, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        self.create_round_logo(container, size=100)
        ctk.CTkLabel(container, text="Reset Password", font=("Arial Black", 28, "bold"), text_color="white").pack(pady=(0, 20))
        
        self.fg_user = ctk.CTkEntry(container, placeholder_text="Enter username", **ENTRY_STYLE); self.fg_user.pack(pady=10)
        self.fg_pass1 = ctk.CTkEntry(container, placeholder_text="Enter new password", show="*", **ENTRY_STYLE); self.fg_pass1.pack(pady=10)
        self.fg_pass2 = ctk.CTkEntry(container, placeholder_text="Confirm new password", show="*", **ENTRY_STYLE); self.fg_pass2.pack(pady=10)
        
        self.error_lbl = ctk.CTkLabel(container, text="", text_color="#E53935", font=("Inter", 13, "bold"))
        self.error_lbl.pack(pady=5)
        
        ctk.CTkButton(container, text="Reset Password", fg_color="#631d2a", hover_color="#4a151f", width=340, height=48, corner_radius=15, font=("Inter", 15, "bold"), command=self._handle_forgot_password).pack(pady=(5, 25))
        back_btn = ctk.CTkLabel(container, text="Back to Login", cursor="hand2", text_color=TEXT_GRAY, font=("Inter", 13))
        back_btn.pack()
        back_btn.bind("<Button-1>", lambda e: self.app.show_page("login"))

    def _show_error(self, msg):
        self.error_lbl.configure(text=msg)

    def _handle_login(self):
        un = self.l_user.get().strip()
        pw = self.l_pass.get().strip()
        if not un or not pw: 
            return self._show_error("Harap isi semua field!")
        ok, msg = self.db.login_user(un, pw)
        if ok:
            self.db.save_session(un)
            self.app.show_welcome_transition(un) # Panggil animasi
        else: 
            self._show_error(msg)

    def _handle_register(self):
        fn = self.r_name.get().strip()
        un = self.r_user.get().strip()
        em = self.r_email.get().strip()
        pw = self.r_pass.get().strip()
        if not all([fn, un, em, pw]): 
            return self._show_error("Isi semua field!")
        ok, msg = self.db.register_user(fn, un, em, pw)
        if ok: self.app.show_page("login")
        else: self._show_error(msg)

    def _handle_forgot_password(self):
        un = self.fg_user.get().strip()
        p1 = self.fg_pass1.get().strip()
        p2 = self.fg_pass2.get().strip()
        if not all([un, p1, p2]): return self._show_error("Isi semua field!")
        if p1 != p2: return self._show_error("Password tidak cocok!")
        ok, msg = self.db.reset_password(un, p1)
        if ok: self.app.show_page("login")
        else: self._show_error(msg)