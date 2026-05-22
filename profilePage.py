import customtkinter as ctk
import json
import os
import shutil
import re 
from datetime import datetime, timedelta
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageOps
from styles import * 
from loginPage import UserDB

class ProfilePage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=BG_MAIN, corner_radius=0)
        self.app = app
        self.db = UserDB()
        
        self.username = "Guest"
        try:
            if os.path.exists("session.json"):
                with open("session.json", "r") as f:
                    s_data = json.load(f)
                    self.username = s_data.get("active_user", s_data.get("username", "Guest"))
        except: pass

        self.user_data = self.db.get_user_info(self.username) or {}
        self.is_new_pw_valid = False
        self.change_pw_popup = None
        
        # Konfigurasi ukuran avatar di sini agar konsisten
        self.avatar_size = (120, 120) 

        self._build_ui()

    def _build_ui(self):
        # Tombol Back Estetik
        back_btn = ctk.CTkButton(self, text="◀ Back to Dashboard", width=160, height=35, 
                                 fg_color=BG_TAB, hover_color=ACCENT, corner_radius=18, 
                                 font=("Trebuchet MS", 12, "bold"), text_color="white",
                                 command=lambda: self.app.show_page("dashboard"))
        back_btn.place(x=30, y=20)

        # Buat scrollable frame agar form panjang muat
        self.scroll_body = ctk.CTkScrollableFrame(self, fg_color="transparent", width=600, height=750)
        self.scroll_body.place(relx=0.5, rely=0.5, anchor="center")

        container = ctk.CTkFrame(self.scroll_body, fg_color=BG_NAV, corner_radius=20)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # --- Bagian Avatar (Sekarang Bulat & Berbingkai) ---
        avatar_section_frame = ctk.CTkFrame(container, fg_color="transparent")
        avatar_section_frame.pack(pady=(40, 10))

        # Label untuk menampung gambar (fg_color transparent agar bingkai dari fungsi helper terlihat)
        self.avatar_img_label = ctk.CTkLabel(avatar_section_frame, text="", fg_color="transparent") 
        self.avatar_img_label.pack()
        
        self._load_avatar_image() 

        ctk.CTkButton(avatar_section_frame, text="📷 Change Photo", width=120, height=30, corner_radius=15,
                    fg_color="#333", hover_color="#444", text_color="white", font=("Inter", 11),
                    command=self._change_avatar_image).pack(pady=15)

        ctk.CTkLabel(container, text=f"@{self.username}", font=("Arial", 16, "bold"), text_color=TEXT_GRAY).pack(pady=(0, 20))

        # --- Form Entries ---
        self.vars = {
            "full_name": ctk.StringVar(value=self.user_data.get("full_name", "")),
            "email": ctk.StringVar(value=self.user_data.get("email", "")),
            "bio": ctk.StringVar(value=self.user_data.get("bio", ""))
        }

        self._create_field(container, "Full Name", self.vars["full_name"])
        self._create_field(container, "Email Address", self.vars["email"])
        self._create_field(container, "Bio/Quote", self.vars["bio"])

        # --- Data Pribadi Baru (Gender & DOB) ---
        personal_frame = ctk.CTkFrame(container, fg_color="transparent")
        personal_frame.pack(fill="x", padx=60, pady=15)
        
        ctk.CTkLabel(personal_frame, text="Gender", font=("Arial", 11), text_color=TEXT_GRAY).pack(anchor="w")
        self.gender_var = ctk.StringVar(value=self.user_data.get("gender", "Male"))
        self.gender_switch = ctk.CTkSegmentedButton(personal_frame, values=["Male", "Female", "Other"], 
                                                     variable=self.gender_var, selected_color=ACCENT, height=40)
        self.gender_switch.pack(fill="x", pady=(5, 15))

        ctk.CTkLabel(personal_frame, text="Date of Birth (DD-MM-YYYY)", font=("Arial", 11), text_color=TEXT_GRAY).pack(anchor="w")
        self.dob_var = ctk.StringVar(value=self.user_data.get("dob", ""))
        self.dob_entry = ctk.CTkEntry(personal_frame, textvariable=self.dob_var, height=40, corner_radius=8,
                                       fg_color="#1e1e1e", border_color="#333", text_color="white")
        self.dob_entry.pack(fill="x", pady=5)

        # --- Bagian Kata Sandi ---
        pw_frame = ctk.CTkFrame(container, fg_color="#1a1a1a", corner_radius=10)
        pw_frame.pack(fill="x", padx=60, pady=20)
        
        ctk.CTkLabel(pw_frame, text="Account Security", font=("Arial", 13, "bold"), text_color="white").pack(anchor="w", padx=15, pady=10)
        ctk.CTkLabel(pw_frame, text="Password is set and secured.", font=("Inter", 12), text_color=TEXT_GRAY).pack(anchor="w", padx=15)
        
        ctk.CTkButton(pw_frame, text="🔒 Change Password", width=150, height=35, corner_radius=8,
                    fg_color="#333", hover_color="#444", text_color="white", font=("Inter", 12, "bold"),
                    command=self._open_change_password_popup).pack(anchor="e", padx=15, pady=15)

        # ── SECTION BECOME AN ADMIN (DIBAWAH CHANGE PASSWORD) ──
        admin_frame = ctk.CTkFrame(container, fg_color="#1a1a1a", corner_radius=10)
        admin_frame.pack(fill="x", padx=60, pady=10)
        
        ctk.CTkLabel(admin_frame, text="Become an Admin?", font=("Arial", 13, "bold"), text_color="white").pack(anchor="w", padx=15, pady=10)
        
        requirements_text = (
            "Admin Privileges allow database management if scraping fails:\n"
            "• Create: Add new movies manually to data_film.json.\n"
            "• Update: Edit existing movie details from Movie Detail page.\n"
            "• Delete: Remove corrupt movie data safely."
        )
        ctk.CTkLabel(admin_frame, text=requirements_text, font=("Inter", 11), text_color=TEXT_GRAY, justify="left").pack(anchor="w", padx=15, pady=(0, 10))
        
        # Validasi status admin aktif secara permanen dari file konfigurasi
        is_user_already_admin = False
        if os.path.exists("admin_config.json"):
            try:
                with open("admin_config.json", "r") as f:
                    is_user_already_admin = self.username in json.load(f)
            except: pass
        
        self.app.is_admin = is_user_already_admin

        if is_user_already_admin:
            status_text = "Status: Authorized Admin 🔓"
            btn_text = "Revoke Admin Access"
            btn_color = "#AA2222"
        else:
            status_text = "Status: Regular User 🔒"
            btn_text = "Apply as Admin"
            btn_color = ACCENT

        self.status_lbl = ctk.CTkLabel(admin_frame, text=status_text, font=("Inter", 12, "bold"), text_color="#FF8C00")
        self.status_lbl.pack(anchor="w", padx=15, pady=(0, 5))
        
        self.admin_btn = ctk.CTkButton(admin_frame, text=btn_text, width=150, height=35, corner_radius=8,
                    fg_color=btn_color, text_color="white", font=("Inter", 12, "bold"),
                    command=self.toggle_admin_role)
        self.admin_btn.pack(anchor="e", padx=15, pady=15)

        # --- Tombol Aksi Utama ---
        ctk.CTkButton(container, text="Save Profile Changes", fg_color=ACCENT, hover_color="#e74c3c", height=45, corner_radius=10, font=("Trebuchet MS", 12, "bold"),
                    text_color="white", command=self._save_general_profile).pack(fill="x", padx=60, pady=(20, 10))
        
        ctk.CTkButton(container, text="Logout", fg_color="transparent", border_width=1, border_color="#333", text_color="white", hover_color="#222",
                    command=self._logout).pack(pady=5)

        ctk.CTkButton(container, text="Delete Account", text_color="#c0392b", fg_color="transparent", hover_color="#222",
                    command=self._delete_account).pack(pady=(5, 30))

    def _create_field(self, parent, label, var):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=60, pady=8)
        ctk.CTkLabel(frame, text=label, font=("Arial", 11), text_color=TEXT_GRAY).pack(anchor="w")
        ctk.CTkEntry(frame, textvariable=var, height=40, corner_radius=8, fg_color="#1e1e1e", border_color="#333", text_color="white").pack(fill="x", pady=2)

    # UPDATED LOGIKA: Fungsi toggle role admin dengan sistem Kuota & PIN Verification
    def toggle_admin_role(self):
        config_file = "admin_config.json"
        
        admin_list = []
        if os.path.exists(config_file):
            try:
                with open(config_file, "r") as f:
                    admin_list = json.load(f)
            except: pass

        current_status = getattr(self.app, "is_admin", False)

        if not current_status:
            # VALIDATOR 1: Batasi kuota maksimal 10 admin
            if len(admin_list) >= 10:
                messagebox.showwarning(
                    "Access Denied", 
                    "Registration Failed!\nThe maximum limit of 10 administrators has been reached."
                )
                return
            
            # CEK COOLDOWN SECURITY LOCKOUT
            is_locked, time_left_str = self._check_cooldown_status()
            if is_locked:
                messagebox.showerror(
                    "Security Lockout", 
                    f"Too many failed verification attempts.\nYour access is locked. Please try again in:\n{time_left_str}"
                )
                return

            # VALIDATOR 2: Jalankan Pop-up Verifikasi PIN 6-Digit
            self._open_admin_pin_popup(admin_list, config_file)

        else:
            # --- PROSES COPOT JABATAN ADMIN ---
            if self.username in admin_list:
                admin_list.remove(self.username)
                try:
                    with open(config_file, "w") as f:
                        json.dump(admin_list, f, indent=4)
                except: pass

            self.app.is_admin = False
            self.status_lbl.configure(text="Status: Regular User 🔒")
            self.admin_btn.configure(text="Apply as Admin", fg_color=ACCENT)
            messagebox.showinfo("Success", "Admin access revoked. You are now a Regular User.")
            print(f"[Validator] Access level revoked: REGULAR USER for @{self.username}")

    # NEW SECURITY HELPERS: Mengelola pembatasan percobaan & durasi hukuman secara permanen (JSON)
    def _get_cooldown_data(self):
        file_path = "admin_cooldown.json"
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    return json.load(f)
            except: pass
        return {}

    def _save_cooldown_data(self, data):
        try:
            with open("admin_cooldown.json", "w") as f:
                json.dump(data, f, indent=4)
        except: pass

    def _check_cooldown_status(self):
        data = self._get_cooldown_data()
        user_record = data.get(self.username, {})
        lock_until_str = user_record.get("lock_until")
        
        if lock_until_str:
            lock_until = datetime.strptime(lock_until_str, "%Y-%m-%d %H:%M:%S")
            if datetime.now() < lock_until:
                # Masih dalam masa hukuman lockout
                remaining = lock_until - datetime.now()
                hours, remainder = divmod(int(remaining.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                if hours > 0:
                    time_str = f"{hours}h {minutes}m {seconds}s"
                else:
                    time_str = f"{minutes}m {seconds}s"
                return True, time_str
            else:
                # Waktu hukuman sudah habis, reset log kesalahan tetapi pertahankan level penalti
                user_record["attempts"] = 0
                user_record["lock_until"] = None
                data[self.username] = user_record
                self._save_cooldown_data(data)
        return False, ""

    # NEW POPUP LOGIK: Membuka jendela verifikasi PIN yang modern & terpusat
    def _open_admin_pin_popup(self, admin_list, config_file):
        if hasattr(self, "admin_pop") and self.admin_pop is not None and self.admin_pop.winfo_exists():
            self.admin_pop.focus()
            return

        self.admin_pop = ctk.CTkToplevel(self)
        self.admin_pop.title("Security Verification")
        self.admin_pop.geometry("380x300")
        self.admin_pop.configure(fg_color="#1A1A1A")
        
        # Center Pop-up relative to Main App Window
        self.admin_pop.update_idletasks()
        x = self.app.winfo_x() + (self.app.winfo_width() // 2) - (self.admin_pop.winfo_width() // 2)
        y = self.app.winfo_y() + (self.app.winfo_height() // 2) - (self.admin_pop.winfo_height() // 2)
        self.admin_pop.geometry(f"+{x}+{y}")
        self.admin_pop.attributes("-topmost", True)

        pop_container = ctk.CTkFrame(self.admin_pop, fg_color="transparent")
        pop_container.pack(fill="both", expand=True, padx=30, pady=25)

        ctk.CTkLabel(pop_container, text="🔒 Admin Verification", font=("Arial", 18, "bold"), text_color="white").pack(pady=(0, 5))
        ctk.CTkLabel(pop_container, text="Enter the 6-digit Security PIN\nto activate administrator privileges.", 
                     font=("Inter", 12), text_color=TEXT_GRAY, justify="center").pack(pady=(0, 10))

        # Lacak sisa kesempatan live di UI
        cooldown_data = self._get_cooldown_data().get(self.username, {})
        current_attempts = cooldown_data.get("attempts", 0)
        remaining_attempts = max(3 - current_attempts, 0)

        self.attempts_lbl = ctk.CTkLabel(pop_container, text=f"Attempts remaining: {remaining_attempts}/3", 
                                         font=("Inter", 11, "bold"), text_color="#e74c3c" if remaining_attempts == 1 else "#FF8C00")
        self.attempts_lbl.pack()

        # Input PIN Lapisan Masking (show="*")
        self.pin_entry = ctk.CTkEntry(pop_container, placeholder_text="******", height=45, 
                                      fg_color="#1e1e1e", border_color="#333", text_color="white",
                                      font=("Arial", 16, "bold"), justify="center", show="*")
        self.pin_entry.pack(fill="x", pady=10)

        # Tombol Verifikasi Eksekusi PIN
        btn_verify = ctk.CTkButton(pop_container, text="Verify PIN", fg_color=ACCENT, 
                                   hover_color="#e74c3c", height=42, corner_radius=8, 
                                   font=("Inter", 12, "bold"), text_color="white",
                                   command=lambda: self._verify_admin_pin(admin_list, config_file))
        btn_verify.pack(fill="x", pady=(10, 0))

    # NEW VERIFY LOGIK: Validasi kecocokan PIN terhadap Master Key & Penalti Berjenjang
    def _verify_admin_pin(self, admin_list, config_file):
        input_pin = self.pin_entry.get().strip()
        MASTER_PIN = "261026" 

        if not input_pin:
            messagebox.showwarning("Input Required", "Please enter the security PIN.")
            return

        cooldown_data = self._get_cooldown_data()
        user_record = cooldown_data.get(self.username, {"attempts": 0, "penalty_level": 0, "lock_until": None})

        if input_pin == MASTER_PIN:
            # --- JIKA PIN BENAR ---
            # 1. Reset catatan kesalahan user ini karena berhasil tembus
            user_record["attempts"] = 0
            user_record["penalty_level"] = 0
            user_record["lock_until"] = None
            cooldown_data[self.username] = user_record
            self._save_cooldown_data(cooldown_data)

            if self.username not in admin_list:
                admin_list.append(self.username)
                try:
                    with open(config_file, "w") as f:
                        json.dump(admin_list, f, indent=4)
                except: pass

            self.app.is_admin = True
            self.status_lbl.configure(text="Status: Authorized Admin 🔓")
            self.admin_btn.configure(text="Revoke Admin Access", fg_color="#AA2222")
            
            # AKSI BARU: Hancurkan pop-up dlu agar tidak menutupi, baru luncurkan MessageBox Sukses!
            self.admin_pop.destroy()
            messagebox.showinfo("Access Granted", "PIN Verified!\nYou are now logged in as Admin.")
            print(f"[Validator] Access level granted: ADMIN for @{self.username}")
        else:
            # --- JIKA PIN SALAH ---
            user_record["attempts"] += 1
            attempts_done = user_record["attempts"]

            if attempts_done >= 3:
                # Tentukan durasi hukuman berdasarkan level kesalahan sebelumnya
                current_penalty = user_record.get("penalty_level", 0)
                if current_penalty == 0:
                    # Gagal pertama kali -> Kunci 10 Menit
                    cooldown_duration = timedelta(minutes=10)
                    time_msg = "10 Minutes"
                    user_record["penalty_level"] = 1
                else:
                    # Sudah pernah dihukum 10 menit tapi masih bebal salah lagi -> Kunci 24 Jam
                    cooldown_duration = timedelta(hours=24)
                    time_msg = "24 Hours (1 Day)"
                    user_record["penalty_level"] = 2

                unlock_time = datetime.now() + cooldown_duration
                user_record["lock_until"] = unlock_time.strftime("%Y-%m-%d %H:%M:%S")
                cooldown_data[self.username] = user_record
                self._save_cooldown_data(cooldown_data)

                self.admin_pop.destroy() # Tutup bar verifikasi karena diblokir
                messagebox.showerror(
                    "Security Lockout", 
                    f"You have entered the incorrect PIN 3 times.\nYour access has been locked for {time_msg}."
                )
            else:
                # Update sisa kuota live di layar pop-up verifikasi
                cooldown_data[self.username] = user_record
                self._save_cooldown_data(cooldown_data)
                
                remaining = 3 - attempts_done
                self.attempts_lbl.configure(text=f"Attempts remaining: {remaining}/3", 
                                             text_color="#e74c3c" if remaining == 1 else "#FF8C00")
                messagebox.showerror("Incorrect PIN", f"The PIN you entered is incorrect.\nRemaining attempts: {remaining}")

    def _get_circular_image_with_border(self, image_path, size, border_width=3, border_color="white"):
        try:
            img = Image.open(image_path).convert("RGBA")
            img = ImageOps.fit(img, size, centering=(0.5, 0.5))
            mask = Image.new('L', size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + size, fill=255)
            output = Image.new('RGBA', size, (0, 0, 0, 0))
            output.paste(img, (0, 0), mask)
            border_size = (size[0] + border_width * 2, size[1] + border_width * 2)
            final_img = Image.new('RGBA', border_size, (0, 0, 0, 0))
            draw_border = ImageDraw.Draw(final_img)
            draw_border.ellipse((0, 0) + border_size, fill=border_color)
            final_img.paste(output, (border_width, border_width), output)
            return ctk.CTkImage(final_img, size=border_size)
        except Exception as e:
            print(f"Error processing image: {e}")
            return None

    def _load_avatar_image(self):
        path = self.user_data.get("avatar_path")
        core_size = self.avatar_size 
        if path and os.path.exists(path):
            ctk_img = self._get_circular_image_with_border(path, core_size, border_width=4, border_color="white")
            if ctk_img:
                self.avatar_img_label.configure(image=ctk_img, text="")
                return 
        initial = self.username[0].upper() if self.username else "G"
        total_size = core_size[0] + 8
        self.avatar_img_label.configure(
            image="", text=initial, width=total_size, height=total_size, 
            corner_radius=total_size // 2, fg_color=ACCENT, text_color="white", font=("Arial", 48, "bold")
        )

    def _change_avatar_image(self):
        file_path = filedialog.askopenfilename(title="Select Profile Picture", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if not file_path: return
        if not os.path.exists("avatars"): os.makedirs("avatars")
        filename = f"{self.username}.jpg"
        destination = os.path.join("avatars", filename)
        try:
            img = Image.open(file_path).convert("RGB")
            img.save(destination, "JPEG")
            self.db.update_avatar_path(self.username, destination)
            self.user_data = self.db.get_user_info(self.username) 
            self._load_avatar_image()
            if hasattr(self.app, "show_toast"): self.app.show_toast("Photo updated!")
            else: messagebox.showinfo("Success", "Photo updated!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image: {e}")

    def _open_change_password_popup(self):
        if self.change_pw_popup is not None and self.change_pw_popup.winfo_exists():
            self.change_pw_popup.focus()
            return
        self.change_pw_popup = ctk.CTkToplevel(self)
        self.change_pw_popup.title("Change Password")
        self.change_pw_popup.geometry("450x570")
        self.change_pw_popup.configure(fg_color="#1A1A1A")
        self.change_pw_popup.update_idletasks()
        x = self.app.winfo_x() + (self.app.winfo_width() // 2) - (self.change_pw_popup.winfo_width() // 2)
        y = self.app.winfo_y() + (self.app.winfo_height() // 2) - (self.change_pw_popup.winfo_height() // 2)
        self.change_pw_popup.geometry(f"+{x}+{y}")
        self.change_pw_popup.attributes("-topmost", True)

        pop_container = ctk.CTkFrame(self.change_pw_popup, fg_color="transparent")
        pop_container.pack(fill="both", expand=True, padx=40, pady=30)
        ctk.CTkLabel(pop_container, text="🔒 Security Update", font=("Arial Black", 22), text_color="white").pack(pady=(0, 10))
        ctk.CTkLabel(pop_container, text=f"Updating password for @{self.username}", text_color=TEXT_GRAY).pack(pady=(0, 25))

        self.old_pw_entry = ctk.CTkEntry(pop_container, placeholder_text="Current Password", show="*", height=45, fg_color="#1e1e1e", border_color="#333", text_color="white")
        self.old_pw_entry.pack(fill="x", pady=10)
        ctk.CTkFrame(pop_container, height=1, fg_color="#333").pack(fill="x", pady=15)

        self.new_pw_entry = ctk.CTkEntry(pop_container, placeholder_text="New Password", show="*", height=45, fg_color="#1e1e1e", border_color="#333", text_color="white")
        self.new_pw_entry.pack(fill="x", pady=10)
        self.new_pw_entry.bind("<KeyRelease>", self._validate_new_password_realtime)

        self.conf_pw_entry = ctk.CTkEntry(pop_container, placeholder_text="Confirm New Password", show="*", height=45, fg_color="#1e1e1e", border_color="#333", text_color="white")
        self.conf_pw_entry.pack(fill="x", pady=10)

        crit_frame = ctk.CTkFrame(pop_container, fg_color="#141414", corner_radius=8)
        crit_frame.pack(fill="x", pady=15, padx=5)
        ctk.CTkLabel(crit_frame, text="Password Requirements:", font=("Inter", 11, "bold"), text_color="white").pack(anchor="w", padx=10, pady=(5,0))
        
        self.crit_pop_len = ctk.CTkLabel(crit_frame, text="• Minimum 8 characters", text_color=TEXT_GRAY, font=("Inter", 11))
        self.crit_pop_len.pack(anchor="w", padx=15)
        self.crit_pop_upper = ctk.CTkLabel(crit_frame, text="• At least 1 Uppercase letter (A-Z)", text_color=TEXT_GRAY, font=("Inter", 11))
        self.crit_pop_upper.pack(anchor="w", padx=15)
        self.crit_pop_num = ctk.CTkLabel(crit_frame, text="• At least 1 Number (0-9)", text_color=TEXT_GRAY, font=("Inter", 11))
        self.crit_pop_num.pack(anchor="w", padx=15, pady=(0, 5))

        self.submit_pw_btn = ctk.CTkButton(pop_container, text="Update Password", fg_color=ACCENT, hover_color="#e74c3c", height=45, corner_radius=10, 
                                            state="disabled", font=("Inter", 13, "bold"), text_color="white", command=self._save_secure_password)
        self.submit_pw_btn.pack(fill="x", pady=20)

    def _validate_new_password_realtime(self, event):
        pwd = self.new_pw_entry.get()
        v_len = len(pwd) >= 8
        v_upper = bool(re.search(r'[A-Z]', pwd))
        v_num = bool(re.search(r'\d', pwd))
        COLOR_VALID = "#2ecc71"
        self.crit_pop_len.configure(text_color=COLOR_VALID if v_len else TEXT_GRAY)
        self.crit_pop_upper.configure(text_color=COLOR_VALID if v_upper else TEXT_GRAY)
        self.crit_pop_num.configure(text_color=COLOR_VALID if v_num else TEXT_GRAY)
        self.is_new_pw_valid = all([v_len, v_upper, v_num])
        self.submit_pw_btn.configure(state="normal" if self.is_new_pw_valid else "disabled")

    def _save_secure_password(self):
        old_pw = self.old_pw_entry.get()
        new_pw = self.new_pw_entry.get()
        conf_pw = self.conf_pw_entry.get()
        if not old_pw: return messagebox.showwarning("Input", "Masukkan sandi lama.")
        if not self.is_new_pw_valid: return 
        if new_pw != conf_pw: return messagebox.showerror("Error", "Kata sandi baru tidak cocok dengan konfirmasi.")
        if old_pw == new_pw: return messagebox.showwarning("Input", "Sandi baru tidak boleh sama dengan sandi lama.")
        ok, msg = self.db.change_password_secure(self.username, old_pw, new_pw)
        if ok:
            messagebox.showinfo("Success", msg)
            self.change_pw_popup.destroy()
        else: messagebox.showerror("Error", msg)

    def _save_general_profile(self):
        fn = self.vars["full_name"].get().strip()
        em = self.vars["email"].get().strip()
        bio = self.vars["bio"].get().strip()
        gen = self.gender_var.get()
        dob = self.dob_var.get().strip()
        if not fn or not em or not dob: return messagebox.showwarning("Input", "Full Name, Email, dan DOB wajib diisi.")
        if not re.match(r'^\d{2}-\d{2}-\d{4}$', dob): return messagebox.showwarning("Input", "Format DOB salah. Gunakan DD-MM-YYYY (misal: 17-08-1945)")
        ok, msg = self.db.update_profile_info(self.username, fn, em, bio, gen, dob)
        messagebox.showinfo("Profile", msg)
        self.user_data = self.db.get_user_info(self.username)
        self._load_avatar_image() 

    def _logout(self):
        if messagebox.askyesno("Confirm", "Logout dari akun?"):
            if os.path.exists("session.json"): os.remove("session.json")
            self.app.show_page("login")

    def _delete_account(self):
        if messagebox.askyesno("⚠️ DANGER", "Hapus akun secara permanen? Semua data watchlist & review akan hilang."):
            path = self.user_data.get("avatar_path")
            if path and os.path.exists(path):
                try: os.remove(path)
                except: pass
            if self.db.delete_user(self.username):
                if os.path.exists("session.json"): os.remove("session.json")
                if os.path.exists(f"watchlist_{self.username}.json"): os.remove(f"watchlist_{self.username}.json")
                self.app.show_page("login")