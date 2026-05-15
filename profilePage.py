import customtkinter as ctk
import json
import os
import shutil
import re 
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

    # ==============================================================================
    # PERBAIKAN: Fungsi Helper untuk memotong gambar jadi bulat & memberi border
    # ==============================================================================
    def _get_circular_image_with_border(self, image_path, size, border_width=3, border_color="white"):
        """Memproses gambar menjadi bulat sempurna dengan bingkai."""
        try:
            # 1. Buka gambar dan ubah ke mode RGBA (transparan)
            img = Image.open(image_path).convert("RGBA")
            
            # 2. Crop gambar menjadi kotak (square) di tengah (center)
            img = ImageOps.fit(img, size, centering=(0.5, 0.5))
            
            # 3. Buat mask untuk membuat gambar bulat
            mask = Image.new('L', size, 0)
            draw = ImageDraw.Draw(mask)
            # Menggambar lingkaran putih penuh di mask
            draw.ellipse((0, 0) + size, fill=255)
            
            # 4. Terapkan mask ke gambar
            output = Image.new('RGBA', size, (0, 0, 0, 0)) # Background transparan
            output.paste(img, (0, 0), mask)
            
            # 5. Buat Bingkai (Border)
            # Kita buat gambar baru yang sedikit lebih besar untuk bingkai
            border_size = (size[0] + border_width * 2, size[1] + border_width * 2)
            final_img = Image.new('RGBA', border_size, (0, 0, 0, 0)) # Transparan
            
            # Gambar lingkaran bingkai
            draw_border = ImageDraw.Draw(final_img)
            # CTk menggunakan nama warna, kita perlu ubah ke hex/RGB jika perlu, 
            # tapi PIL Draw menerima nama warna standar.
            draw_border.ellipse((0, 0) + border_size, fill=border_color)
            
            # 6. Tempelkan gambar bulat di tengah bingkai
            final_img.paste(output, (border_width, border_width), output)
            
            # Kembali dalam bentuk CTkImage agar rasio aspek terjaga saat penskalaan CTk
            # Gunakan ukuran border_size agar tidak terpotong
            return ctk.CTkImage(final_img, size=border_size)
        except Exception as e:
            print(f"Error processing image: {e}")
            return None

    def _load_avatar_image(self):
        path = self.user_data.get("avatar_path")
        # Ukuran inti gambar (sebelum ditambah border)
        core_size = self.avatar_size 
        
        if path and os.path.exists(path):
            # Gunakan fungsi helper untuk mendapatkan gambar bulat ber-border
            ctk_img = self._get_circular_image_with_border(path, core_size, border_width=4, border_color="white")
            if ctk_img:
                self.avatar_img_label.configure(image=ctk_img, text="")
                return 
            
        # --- Fallback: Jika tidak ada foto, buat bulatan warna dengan inisial ---
        initial = self.username[0].upper() if self.username else "G"
        # Untuk teks, kita bisa pakai corner_radius label
        total_size = core_size[0] + 8 # Sesuaikan dengan border_width * 2 di atas
        self.avatar_img_label.configure(
            image="", 
            text=initial, 
            width=total_size, 
            height=total_size, 
            corner_radius=total_size // 2, # Bulat sempurna
            fg_color=ACCENT, 
            text_color="white", 
            font=("Arial", 48, "bold")
        )

    def _change_avatar_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Profile Picture",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")]
        )
        if not file_path: return
        if not os.path.exists("avatars"): os.makedirs("avatars")
        filename = f"{self.username}.jpg"
        destination = os.path.join("avatars", filename)

        try:
            # Buka dan simpan ulang sebagai JPG untuk kompresi/uniformity
            img = Image.open(file_path)
            img = img.convert("RGB") # Hapus transparansi jika ada sebelum save ke jpg
            img.save(destination, "JPEG")
            
            self.db.update_avatar_path(self.username, destination)
            self.user_data = self.db.get_user_info(self.username) 
            self._load_avatar_image()
            if hasattr(self.app, "show_toast"):
                self.app.show_toast("Photo updated!")
            else:
                messagebox.showinfo("Success", "Photo updated!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image: {e}")

    # --- Sisa fungsi (Password popup, dll) tetap sama ---
    def _open_change_password_popup(self):
        if self.change_pw_popup is not None and self.change_pw_popup.winfo_exists():
            self.change_pw_popup.focus()
            return
        self.change_pw_popup = ctk.CTkToplevel(self)
        self.change_pw_popup.title("Change Password")
        self.change_pw_popup.geometry("450x570")
        self.change_pw_popup.configure(fg_color="#1A1A1A")
        
        # Center popup relative to main app
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
        else:
            messagebox.showerror("Error", msg)

    def _save_general_profile(self):
        fn = self.vars["full_name"].get().strip()
        em = self.vars["email"].get().strip()
        bio = self.vars["bio"].get().strip()
        gen = self.gender_var.get()
        dob = self.dob_var.get().strip()

        if not fn or not em or not dob:
            return messagebox.showwarning("Input", "Full Name, Email, dan DOB wajib diisi.")
        if not re.match(r'^\d{2}-\d{2}-\d{4}$', dob):
            return messagebox.showwarning("Input", "Format DOB salah. Gunakan DD-MM-YYYY (misal: 17-08-1945)")

        ok, msg = self.db.update_profile_info(self.username, fn, em, bio, gen, dob)
        messagebox.showinfo("Profile", msg)
        self.user_data = self.db.get_user_info(self.username)
        # Reload image just in case background color needs refreshing, 
        # though not strictly necessary if image exists
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