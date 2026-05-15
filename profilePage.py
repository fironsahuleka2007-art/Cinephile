import customtkinter as ctk
import json
import os
from tkinter import messagebox

class ProfileWidget(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app
        
        # 1. Ambil Nama User dari Session
        self.username = "Guest"
        try:
            if os.path.exists("session.json"):
                with open("session.json", "r") as f:
                    data = json.load(f)
                    self.username = data.get("username", "Guest")
        except: pass

        # Container Utama (Horizontal)
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(padx=5, pady=5)

        # 2. Avatar Bulat (Inisial Nama)
        initial = self.username[0].upper() if self.username else "G"
        self.avatar = ctk.CTkLabel(
            self.container, 
            text=initial, 
            width=35, 
            height=35, 
            corner_radius=17,
            fg_color="#E50914", # Warna Merah Netflix
            text_color="white",
            font=("Helvetica", 14, "bold")
        )
        self.avatar.pack(side="left", padx=(0, 10))

        # 3. Nama User & Tombol Dropdown/Logout
        self.user_info = ctk.CTkLabel(
            self.container, 
            text=self.username, 
            font=("Helvetica", 13, "bold"),
            text_color="white"
        )
        self.user_info.pack(side="left", padx=(0, 15))

        self.logout_btn = ctk.CTkButton(
            self.container,
            text="Logout",
            width=70,
            height=28,
            fg_color="#333",
            hover_color="#E50914",
            text_color="white",
            font=("Helvetica", 11, "bold"),
            command=self._confirm_logout
        )
        self.logout_btn.pack(side="left")

    def _confirm_logout(self):
        # VALIDASI: Pop up konfirmasi sebelum keluar
        jawaban = messagebox.askyesno(
            "Konfirmasi Logout", 
            f"Halo {self.username}, apakah kamu yakin ingin keluar dari aplikasi?"
        )
        if jawaban:
            print(f"User {self.username} logged out.")
            self.app.logout() # Memanggil fungsi logout di main.py