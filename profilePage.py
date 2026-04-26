import customtkinter as ctk
from tkinter import messagebox
from styles import *

class ProfilePage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=BG_MAIN, corner_radius=0)
        self.app = app
        
        # Ambil data user yang login (asumsi dari AuthPages/Database)
        self.user_data = self.app.auth.db.get_session() or {"username": "User", "email": "user@example.com"}

        self._build_ui()

    def _build_ui(self):
        # 1. Navigasi (Sama kayak Dashboard)
        self._build_nav()

        # 2. Main Content
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(pady=60)

        # Avatar Bulat (Simulasi)
        avatar = ctk.CTkFrame(content, width=120, height=120, fg_color=BG_TAB, corner_radius=60)
        avatar.pack(pady=20)
        ctk.CTkLabel(avatar, text="👤", font=("Arial", 60)).place(relx=0.5, rely=0.5, anchor="center")

        # Username & Email
        ctk.CTkLabel(content, text=self.user_data['username'], font=("Helvetica", 28, "bold"), text_color=TEXT_WHITE).pack()
        ctk.CTkLabel(content, text=self.user_data['email'], font=("Trebuchet MS", 14), text_color=TEXT_GRAY).pack(pady=(0, 30))

        # Box Statistik
        stats_frame = ctk.CTkFrame(content, fg_color=BG_NAV, corner_radius=12, width=400, height=100)
        stats_frame.pack(pady=10, padx=20)
        stats_frame.pack_propagate(False)
        
        # Contoh Isi Statistik
        ctk.CTkLabel(stats_frame, text="12\nWatchlist", font=("Helvetica", 14, "bold"), text_color=TEXT_WHITE).pack(side="left", expand=True)
        ctk.CTkLabel(stats_frame, text="Epic\nTop Genre", font=("Helvetica", 14, "bold"), text_color=TEXT_WHITE).pack(side="left", expand=True)

        # Tombol Log Out
        logout_btn = ctk.CTkButton(content, text="LOG OUT", fg_color=ACCENT, hover_color="#C62828", 
                                font=("Trebuchet MS", 12, "bold"), width=200, height=40,
                                command=self.confirm_logout)
        logout_btn.pack(pady=40)

    def _build_nav(self):
        # (Copy paste struktur nav dari GenreAnalyze, tapi tandai tombol 'Profile' yang aktif)
        nav = ctk.CTkFrame(self, fg_color=BG_NAV, height=44)
        nav.pack(fill="x", side="top")
        # ... (Struktur navigasi lainnya sama seperti sebelumnya)

    def confirm_logout(self):
        # VALIDASI LOGOUT
        jawaban = messagebox.askyesno("Konfirmasi Log Out", "Apakah kamu yakin ingin keluar dari Cinephile?")
        if jawaban:
            self.app.logout()