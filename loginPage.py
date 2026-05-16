import customtkinter as ctk
import os
import json
import re
from tkinter import messagebox
from PIL import Image, ImageDraw, ImageOps
from styles import ENTRY_STYLE, TEXT_GRAY, COLOR_VALID, COLOR_INVALID

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

    def register_user(self, full_name, username, email, password, gender, dob):
        data = self._load_data()
        if username in data: return False, "Username sudah terdaftar!"
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
            self.save_session(username)
            return True, "Login Berhasil!"
        return False, "Username atau Password salah!"

    def get_user_info(self, username):
        data = self._load_data()
        return data.get(username, None)

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
        return False, "Gagal memperbarui profil!"

    def update_avatar_path(self, username, file_path):
        data = self._load_data()
        if username in data:
            data[username]["avatar_path"] = file_path
            self._save_data(data)
            return True
        return False

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
            # Tetap menggunakan "active_user" agar main.py lama kamu membaca dengan benar
            json.dump({"active_user": username}, f)


class AuthPages:
    def __init__(self, master, app):
        self.master = master
        self.app = app
        self.db = UserDB()
        self.reg_pw_valid = False
        self.forgot_pw_valid = False
        self.logo_size = (120, 120)
        self.accent_color = "#5C1D24" 

    def _create_base_ui(self):
        for w in self.master.winfo_children(): w.destroy()
        self.container = ctk.CTkFrame(self.master, fg_color="transparent")
        self.container.place(relx=0.5, rely=0.5, anchor="center")

    def _get_processed_logo(self, path, size):
        try:
            if os.path.exists(path):
                img = Image.open(path).convert("RGBA")
                img = ImageOps.fit(img, size, centering=(0.5, 0.5))
                mask = Image.new('L', size, 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0) + size, fill=255)
                output = Image.new('RGBA', size, (0, 0, 0, 0))
                output.paste(img, (0, 0), mask)
                return ctk.CTkImage(output, size=size)
        except Exception as e:
            print(f"Error logo: {e}")
        return None

    def _render_logo_header(self):
        ctk_logo = self._get_processed_logo("Cinephile.png", self.logo_size)
        if ctk_logo:
            lbl = ctk.CTkLabel(self.container, image=ctk_logo, text="")
            lbl.pack(pady=(10, 15))
        else:
            lbl = ctk.CTkLabel(self.container, text="C", width=self.logo_size[0], height=self.logo_size[1],
                               corner_radius=self.logo_size[0]//2, fg_color="white", text_color="black",
                               font=("Arial", 60, "bold"))
            lbl.pack(pady=(10, 15))

    def _toggle_password_visibility(self, entry_field, checkbox):
        if checkbox.get():
            entry_field.configure(show="")
        else:
            entry_field.configure(show="*")

    # ─── 1. LANDING/WELCOME PAGE ───
    def render_welcome_page(self):
        for w in self.master.winfo_children(): w.destroy()
        self.master.master.geometry("1100x850")

        header_frame = ctk.CTkFrame(self.master, fg_color="transparent")
        header_frame.pack(anchor="nw", padx=50, pady=50)

        ctk_logo = self._get_processed_logo("Cinephile.png", (90, 90))
        if ctk_logo:
            logo_lbl = ctk.CTkLabel(header_frame, image=ctk_logo, text="")
            logo_lbl.pack(side="left", padx=(0, 20))
        
        text_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        text_frame.pack(side="left")

        ctk.CTkLabel(text_frame, text="Welcome To Cinephile", font=("Arial Black", 36, "bold"), text_color="white").pack(anchor="w")
        ctk.CTkLabel(text_frame, text="Discover Movies Beyond the Surface", font=("Arial", 16), text_color=TEXT_GRAY).pack(anchor="w")

        center_container = ctk.CTkFrame(self.master, fg_color="transparent")
        center_container.place(relx=0.5, rely=0.6, anchor="center")

        btn_login = ctk.CTkButton(center_container, text="Log in", fg_color=self.accent_color, hover_color="#78252E",
                                  width=340, height=45, corner_radius=12, font=("Arial", 14, "bold"), text_color="white",
                                  command=self.render_login)
        btn_login.pack(pady=(0, 15))

        reg_link_frame = ctk.CTkFrame(center_container, fg_color="transparent")
        reg_link_frame.pack()
        
        ctk.CTkLabel(reg_link_frame, text="don't have an account? ", font=("Inter", 13), text_color=TEXT_GRAY).pack(side="left")
        lbl_reg = ctk.CTkLabel(reg_link_frame, text="Create a account", font=("Inter", 13, "bold"), text_color="white", cursor="hand2")
        lbl_reg.pack(side="left")
        lbl_reg.bind("<Button-1>", lambda e: self.render_register())

    # ─── 2. LOGIN VIEW ───
    def render_login(self):
        self._create_base_ui()
        self._render_logo_header()

        ctk.CTkLabel(self.container, text="Log In Cinephile.", font=("Arial", 26, "bold"), text_color="white").pack(pady=(0, 20))

        self.error_lbl = ctk.CTkLabel(self.container, text="", text_color="red", font=("Inter", 12))
        self.error_lbl.pack()

        login_style = ENTRY_STYLE.copy()
        login_style.update({"width": 340, "height": 45, "corner_radius": 12})

        self.l_user = ctk.CTkEntry(self.container, placeholder_text="Username", **login_style)
        self.l_user.pack(pady=8)
        
        self.l_pass = ctk.CTkEntry(self.container, placeholder_text="Password", show="*", **login_style)
        self.l_pass.pack(pady=8)
        
        show_pw_var = ctk.BooleanVar(value=False)
        cb_show = ctk.CTkCheckBox(self.container, text="Show Password", variable=show_pw_var, font=("Inter", 11),
                                  text_color=TEXT_GRAY, checkbox_width=16, checkbox_height=16,
                                  command=lambda: self._toggle_password_visibility(self.l_pass, show_pw_var))
        cb_show.pack(anchor="w", padx=5, pady=(0, 5))

        self.remember_cb = ctk.CTkCheckBox(self.container, text="Remember Me", font=("Inter", 12), text_color=TEXT_GRAY)
        self.remember_cb.pack(pady=10)

        ctk.CTkButton(self.container, text="Log in", fg_color=self.accent_color, hover_color="#78252E",
                      width=340, height=45, corner_radius=12, font=("Arial", 14, "bold"), command=self._handle_login).pack(pady=(10, 15))
        
        link_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        link_frame.pack(fill="x")
        
        btn_reg = ctk.CTkLabel(link_frame, text="Don't have an account? Create one", font=("Inter", 12), text_color=TEXT_GRAY, cursor="hand2")
        btn_reg.pack(pady=3)
        btn_reg.bind("<Button-1>", lambda e: self.render_register())

        btn_forgot = ctk.CTkLabel(link_frame, text="Forgot your password?", font=("Inter", 11), text_color=TEXT_GRAY, cursor="hand2")
        btn_forgot.pack(pady=5)
        btn_forgot.bind("<Button-1>", lambda e: self.render_forgot_password())

    def _handle_login(self):
        un = self.l_user.get().strip()
        pw = self.l_pass.get().strip()
        ok, msg = self.db.login_user(un, pw)
        if ok:
            # Sinkronisasi ke MainApp core property
            self.app.username = un 
            self.app.show_welcome_transition(un)
        else:
            self.error_lbl.configure(text=msg)

    # ─── 3. REGISTER VIEW ───
    def render_register(self):
        self._create_base_ui()
        self.master.master.geometry("1100x950")
        self._render_logo_header()

        ctk.CTkLabel(self.container, text="REGISTER", font=("Arial Black", 32), text_color="white").pack(pady=(0, 15))
        self.error_lbl = ctk.CTkLabel(self.container, text="", text_color="red")
        self.error_lbl.pack()

        reg_style = ENTRY_STYLE.copy()
        reg_style.update({"width": 340, "height": 42, "corner_radius": 10})

        self.r_name = ctk.CTkEntry(self.container, placeholder_text="Full Name", **reg_style)
        self.r_name.pack(pady=5)
        self.r_user = ctk.CTkEntry(self.container, placeholder_text="Username", **reg_style)
        self.r_user.pack(pady=5)
        self.r_email = ctk.CTkEntry(self.container, placeholder_text="Email", **reg_style)
        self.r_email.pack(pady=5)
        
        gender_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        gender_frame.pack(pady=5)
        ctk.CTkLabel(gender_frame, text="Gender:", text_color="white", font=("Inter", 12)).pack(side="left", padx=10)
        self.r_gender = ctk.CTkSegmentedButton(gender_frame, values=["Male", "Female", "Other"], selected_color=self.accent_color)
        self.r_gender.pack(side="left")
        self.r_gender.set("Male")

        self.r_dob = ctk.CTkEntry(self.container, placeholder_text="DOB (DD-MM-YYYY)", **reg_style)
        self.r_dob.pack(pady=5)

        self.r_pass = ctk.CTkEntry(self.container, placeholder_text="Password", show="*", **reg_style)
        self.r_pass.pack(pady=5)
        self.r_pass.bind("<KeyRelease>", self._validate_reg_password)

        show_reg_pw_var = ctk.BooleanVar(value=False)
        cb_show_reg = ctk.CTkCheckBox(self.container, text="Show Password", variable=show_reg_pw_var, font=("Inter", 11),
                                      text_color=TEXT_GRAY, checkbox_width=16, checkbox_height=16,
                                      command=lambda: self._toggle_password_visibility(self.r_pass, show_reg_pw_var))
        cb_show_reg.pack(anchor="w", padx=5, pady=(0, 5))

        criteria_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        criteria_frame.pack(pady=5)
        self.crit_len = ctk.CTkLabel(criteria_frame, text="• Minimum 8 characters", text_color=TEXT_GRAY, font=("Inter", 11))
        self.crit_len.pack(anchor="w")
        self.crit_upper = ctk.CTkLabel(criteria_frame, text="• At least 1 Uppercase letter (A-Z)", text_color=TEXT_GRAY, font=("Inter", 11))
        self.crit_upper.pack(anchor="w")
        self.crit_num = ctk.CTkLabel(criteria_frame, text="• At least 1 Number (0-9)", text_color=TEXT_GRAY, font=("Inter", 11))
        self.crit_num.pack(anchor="w")
        
        self.reg_btn = ctk.CTkButton(self.container, text="Create Account", fg_color=self.accent_color, hover_color="#78252E",
                                     state="disabled", width=340, height=45, corner_radius=12, font=("Arial", 13, "bold"),
                                     command=self._handle_register)
        self.reg_btn.pack(pady=15)
        
        ctk.CTkButton(self.container, text="Back to Login", fg_color=self.accent_color, hover_color="#78252E",
                      width=150, height=35, corner_radius=18, font=("Trebuchet MS", 12, "bold"), 
                      command=self._go_back_login).pack(pady=5)

    def _validate_reg_password(self, event):
        pwd = self.r_pass.get()
        v_len = len(pwd) >= 8
        v_upper = bool(re.search(r'[A-Z]', pwd))
        v_num = bool(re.search(r'\d', pwd))

        self.crit_len.configure(text_color=COLOR_VALID if v_len else TEXT_GRAY)
        self.crit_upper.configure(text_color=COLOR_VALID if v_upper else TEXT_GRAY)
        self.crit_num.configure(text_color=COLOR_VALID if v_num else TEXT_GRAY)

        self.reg_pw_valid = all([v_len, v_upper, v_num])
        self.reg_btn.configure(state="normal" if self.reg_pw_valid else "disabled")

    def _go_back_login(self):
        self.master.master.geometry("1100x850")
        self.render_login()

    def _handle_register(self):
        fn, un = self.r_name.get().strip(), self.r_user.get().strip()
        em, pw = self.r_email.get().strip(), self.r_pass.get()
        gen, dob = self.r_gender.get(), self.r_dob.get().strip()

        if not all([fn, un, em, pw, gen, dob]):
            return self.error_lbl.configure(text="Mohon isi semua field")
        if not self.reg_pw_valid: return
        if not re.match(r'^\d{2}-\d{2}-\d{4}$', dob):
            return self.error_lbl.configure(text="Format Lahir salah (DD-MM-YYYY)")

        ok, msg = self.db.register_user(fn, un, em, pw, gen, dob)
        if ok: 
            self._go_back_login()
        else: 
            self.error_lbl.configure(text=msg)

    # ─── 4. FORGOT PASSWORD VIEW ───
    def render_forgot_password(self):
        self._create_base_ui()
        self.master.master.geometry("1100x850")
        self._render_logo_header()

        ctk.CTkLabel(self.container, text="FORGOT PASSWORD", font=("Arial Black", 28), text_color="white").pack(pady=(0, 10))
        
        self.f_error_lbl = ctk.CTkLabel(self.container, text="", text_color="red", font=("Inter", 12))
        self.f_error_lbl.pack()

        style_f = ENTRY_STYLE.copy()
        style_f.update({"width": 340, "height": 45, "corner_radius": 12})

        self.f_user = ctk.CTkEntry(self.container, placeholder_text="Enter Registered Username", **style_f)
        self.f_user.pack(pady=8)

        self.f_new_pw = ctk.CTkEntry(self.container, placeholder_text="Enter New Password", show="*", **style_f)
        self.f_new_pw.pack(pady=8)
        self.f_new_pw.bind("<KeyRelease>", self._validate_forgot_password_live)

        self.f_crit_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.f_crit_frame.pack(pady=4)
        self.f_crit_len = ctk.CTkLabel(self.f_crit_frame, text="• Minimum 8 characters", text_color=TEXT_GRAY, font=("Inter", 11))
        self.f_crit_len.pack(anchor="w")
        self.f_crit_upper = ctk.CTkLabel(self.f_crit_frame, text="• At least 1 Uppercase letter (A-Z)", text_color=TEXT_GRAY, font=("Inter", 11))
        self.f_crit_upper.pack(anchor="w")
        self.f_crit_num = ctk.CTkLabel(self.f_crit_frame, text="• At least 1 Number (0-9)", text_color=TEXT_GRAY, font=("Inter", 11))
        self.f_crit_num.pack(anchor="w")

        self.f_confirm_pw = ctk.CTkEntry(self.container, placeholder_text="Confirm New Password", show="*", **style_f)
        self.f_confirm_pw.pack(pady=8)

        show_f_pw_var = ctk.BooleanVar(value=False)
        def toggle_f_pws():
            show_char = "" if show_f_pw_var.get() else "*"
            self.f_new_pw.configure(show=show_char)
            self.f_confirm_pw.configure(show=show_char)

        cb_show_f = ctk.CTkCheckBox(self.container, text="Show Passwords", variable=show_f_pw_var, font=("Inter", 11),
                                    text_color=TEXT_GRAY, checkbox_width=16, checkbox_height=16, command=toggle_f_pws)
        cb_show_f.pack(anchor="w", padx=5, pady=5)

        self.f_submit_btn = ctk.CTkButton(self.container, text="Recover & Save Password", fg_color=self.accent_color,
                                          hover_color="#78252E", width=340, height=45, corner_radius=12, 
                                          font=("Arial", 14, "bold"), state="disabled", command=self._execute_forgot_password_flow)
        self.f_submit_btn.pack(pady=15)
        
        ctk.CTkButton(self.container, text="Back to Login", fg_color=self.accent_color, hover_color="#78252E",
                      width=150, height=35, corner_radius=18, font=("Trebuchet MS", 12, "bold"), 
                      command=self._go_back_login).pack(pady=5)

    def _validate_forgot_password_live(self, event):
        pwd = self.f_new_pw.get()
        v_len = len(pwd) >= 8
        v_upper = bool(re.search(r'[A-Z]', pwd))
        v_num = bool(re.search(r'\d', pwd))

        self.f_crit_len.configure(text_color=COLOR_VALID if v_len else TEXT_GRAY)
        self.f_crit_upper.configure(text_color=COLOR_VALID if v_upper else TEXT_GRAY)
        self.f_crit_num.configure(text_color=COLOR_VALID if v_num else TEXT_GRAY)

        self.forgot_pw_valid = all([v_len, v_upper, v_num])
        self.f_submit_btn.configure(state="normal" if self.forgot_pw_valid else "disabled")

    def _execute_forgot_password_flow(self):
        un = self.f_user.get().strip()
        new_pw = self.f_new_pw.get()
        conf_pw = self.f_confirm_pw.get()

        if not un:
            return self.f_error_lbl.configure(text="Username tidak boleh kosong!")
        if new_pw != conf_pw:
            return self.f_error_lbl.configure(text="Sandi baru dan konfirmasi tidak cocok!")

        users = self.db._load_data()
        if un not in users:
            return self.f_error_lbl.configure(text="Username tidak terdaftar di sistem!")

        users[un]["password"] = new_pw
        self.db._save_data(users)
        
        messagebox.showinfo("Success", f"Sandi baru untuk @{un} berhasil diperbarui!\nSilakan login kembali.")
        self._go_back_login()