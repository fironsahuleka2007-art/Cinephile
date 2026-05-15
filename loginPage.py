import customtkinter as ctk
import os
import json
import re # Untuk validasi sandi di registrasi
from styles import ENTRY_STYLE, TEXT_GRAY, COLOR_VALID, COLOR_INVALID
from PIL import Image, ImageDraw

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

    # Tambah parameter gender & dob
    def register_user(self, full_name, username, email, password, gender, dob):
        data = self._load_data()
        if username in data: return False, "Username sudah terdaftar!"
        # Simpan data tambahan & default avatar_path None
        data[username] = {
            "full_name": full_name, 
            "email": email, 
            "password": password, 
            "gender": gender, 
            "dob": dob, 
            "bio": "",
            "avatar_path": None 
        }
        self._save_data(data)
        return True, "Akun berhasil dibuat!"

    def login_user(self, username, password):
        data = self._load_data()
        if username in data and data[username]["password"] == password:
            return True, "Login Berhasil!"
        return False, "Username atau Password salah!"

    def get_user_info(self, username):
        data = self._load_data()
        return data.get(username, None)

    # General Update (Tanpa Password)
    def update_profile_info(self, username, full_name, email, bio, gender, dob):
        data = self._load_data()
        if username in data:
            data[username].update({
                "full_name": full_name,
                "email": email,
                "bio": bio,
                "gender": gender,
                "dob": dob
            })
            self._save_data(data)
            return True, "Profil diperbarui!"
        return False, "Gagal!"

    # Khusus Update Path Avatar
    def update_avatar_path(self, username, file_path):
        data = self._load_data()
        if username in data:
            data[username]["avatar_path"] = file_path
            self._save_data(data)
            return True
        return False

    # Khusus Update Password (Lama -> Baru)
    def change_password_secure(self, username, old_pw, new_pw):
        data = self._load_data()
        if username in data:
            if data[username]["password"] == old_pw:
                data[username]["password"] = new_pw
                self._save_data(data)
                return True, "Kata sandi berhasil diubah!"
            else:
                return False, "Kata sandi lama salah!"
        return False, "User tidak ditemukan."

    def delete_user(self, username):
        data = self._load_data()
        if username in data:
            del data[username]
            self._save_data(data)
            return True
        return False

    def save_session(self, username):
        with open(self.session_file, "w") as f:
            json.dump({"active_user": username}, f)

class AuthPages:
    def __init__(self, master, app):
        self.master = master
        self.app = app
        self.db = UserDB()
        self.is_reg_pw_valid = False

    def render_login(self):
        self._create_base_ui("LOGIN")
        self.l_user = ctk.CTkEntry(self.container, placeholder_text="Username", **ENTRY_STYLE)
        self.l_user.pack(pady=10)
        self.l_pass = ctk.CTkEntry(self.container, placeholder_text="Password", show="*", **ENTRY_STYLE)
        self.l_pass.pack(pady=10)
        ctk.CTkButton(self.container, text="Login", fg_color="#E53935", command=self._handle_login).pack(pady=20)
        btn = ctk.CTkLabel(self.container, text="Don't have an account? Register", cursor="hand2")
        btn.pack(); btn.bind("<Button-1>", lambda e: self.app.show_page("register"))

    def render_register(self):
        self._create_base_ui("REGISTER")
        self.master.master.geometry("1100x950") # Pinjam geometri biar muat form panjang

        self.r_name = ctk.CTkEntry(self.container, placeholder_text="Full Name", **ENTRY_STYLE)
        self.r_name.pack(pady=5)
        self.r_user = ctk.CTkEntry(self.container, placeholder_text="Username", **ENTRY_STYLE)
        self.r_user.pack(pady=5)
        self.r_email = ctk.CTkEntry(self.container, placeholder_text="Email", **ENTRY_STYLE)
        self.r_email.pack(pady=5)
        
        # Gender & DOB
        gender_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        gender_frame.pack(pady=5)
        ctk.CTkLabel(gender_frame, text="Gender:", text_color="white").pack(side="left", padx=10)
        self.r_gender = ctk.CTkSegmentedButton(gender_frame, values=["Male", "Female", "Other"], selected_color=ACCENT)
        self.r_gender.pack(side="left")
        self.r_gender.set("Male")

        self.r_dob = ctk.CTkEntry(self.container, placeholder_text="DOB (DD-MM-YYYY)", **ENTRY_STYLE)
        self.r_dob.pack(pady=5)

        # Password with criteria
        self.r_pass = ctk.CTkEntry(self.container, placeholder_text="Password", show="*", **ENTRY_STYLE)
        self.r_pass.pack(pady=5)
        self.r_pass.bind("<KeyRelease>", self._validate_reg_password)

        criteria_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        criteria_frame.pack(pady=5)
        self.crit_len = ctk.CTkLabel(criteria_frame, text="• Min 8 chars", text_color=TEXT_GRAY, font=("Inter", 11))
        self.crit_len.pack(anchor="w")
        self.crit_upper = ctk.CTkLabel(criteria_frame, text="• 1 Uppercase", text_color=TEXT_GRAY, font=("Inter", 11))
        self.crit_upper.pack(anchor="w")
        self.crit_num = ctk.CTkLabel(criteria_frame, text="• 1 Number", text_color=TEXT_GRAY, font=("Inter", 11))
        self.crit_num.pack(anchor="w")
        
        self.reg_btn = ctk.CTkButton(self.container, text="Create Account", fg_color="#E53935", state="disabled", command=self._handle_register)
        self.reg_btn.pack(pady=20)
        
        btn = ctk.CTkLabel(self.container, text="Back to Login", cursor="hand2")
        btn.pack(); btn.bind("<Button-1>", lambda e: self._go_back_login())

    def _validate_reg_password(self, event):
        pwd = self.r_pass.get()
        v_len = len(pwd) >= 8
        v_upper = bool(re.search(r'[A-Z]', pwd))
        v_num = bool(re.search(r'\d', pwd))

        self.crit_len.configure(text_color=COLOR_VALID if v_len else TEXT_GRAY)
        self.crit_upper.configure(text_color=COLOR_VALID if v_upper else TEXT_GRAY)
        self.crit_num.configure(text_color=COLOR_VALID if v_num else TEXT_GRAY)

        self.is_reg_pw_valid = all([v_len, v_upper, v_num])
        self.reg_btn.configure(state="normal" if self.is_reg_pw_valid else "disabled")

    def _create_base_ui(self, title):
        for w in self.master.winfo_children(): w.destroy()
        self.container = ctk.CTkFrame(self.master, fg_color="transparent")
        self.container.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(self.container, text=title, font=("Arial Black", 32)).pack(pady=20)
        self.error_lbl = ctk.CTkLabel(self.container, text="", text_color="red")
        self.error_lbl.pack()

    def _handle_login(self):
        un, pw = self.l_user.get().strip(), self.l_pass.get().strip()
        ok, msg = self.db.login_user(un, pw)
        if ok: 
            self.db.save_session(un)
            self.master.master.geometry("1100x850") # Reset geometri
            self.app.show_welcome_transition(un)
        else: self.error_lbl.configure(text=msg)

    def _go_back_login(self):
        self.master.master.geometry("1100x850") # Reset geometri
        self.app.show_page("login")

    def _handle_register(self):
        fn = self.r_name.get().strip()
        un = self.r_user.get().strip()
        em = self.r_email.get().strip()
        pw = self.r_pass.get()
        gen = self.r_gender.get()
        dob = self.r_dob.get().strip()

        if not all([fn, un, em, pw, gen, dob]):
            return self.error_lbl.configure(text="Mohon isi semua field")

        if not self.is_reg_pw_valid: return

        # Validasi format DOB simple (DD-MM-YYYY)
        if not re.match(r'^\d{2}-\d{2}-\d{4}$', dob):
            return self.error_lbl.configure(text="Format Lahir salah (DD-MM-YYYY)")

        ok, msg = self.db.register_user(fn, un, em, pw, gen, dob)
        if ok: 
            self.master.master.geometry("1100x850") # Reset geometri
            self.app.show_page("login")
        else: self.error_lbl.configure(text=msg)