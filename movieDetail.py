import customtkinter as ctk
import math
from PIL import Image
import urllib.request
import io

class MovieDetailPage(ctk.CTkFrame):
    def __init__(self, master, app, movie_data=None):
        # Background utama super gelap
        super().__init__(master, fg_color="#141414", corner_radius=0)
        self.app = app
        self.movie = movie_data if movie_data else {}
        self._build_ui()

    def _generate_dynamic_chart(self, rating_str):
        try:
            rating = float(rating_str)
        except:
            rating = 5.0

        distribution = {}
        for score in range(1, 11):
            distance = abs(score - rating)
            weight = math.exp(-(distance ** 2) / 2.0) 
            import random
            noise = random.uniform(0.8, 1.2)
            distribution[score] = weight * noise     

        total_weight = sum(distribution.values())
        for score in distribution:
            distribution[score] = distribution[score] / total_weight
        return distribution

    def _build_ui(self):
        # NAVBAR (Seragam #111111)
        nav_widget = ctk.CTkFrame(self, fg_color="#111111", height=50, corner_radius=0)
        nav_widget.pack(fill="x", side="top")
        nav_widget.pack_propagate(False)

        ctk.CTkButton(nav_widget, text="← Back to Dashboard", width=120, height=30, 
                    fg_color="transparent", text_color="#FF8C00", font=("Trebuchet MS", 12, "bold"),
                    command=lambda: self.app.show_page("dashboard")).pack(side="left", padx=10, pady=10)

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="#141414", corner_radius=0)
        self.scroll.pack(fill="both", expand=True)

        # 1. HEADER (Movie Details)
        header_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        header_frame.pack(fill="x", pady=(20, 10))
        ctk.CTkLabel(header_frame, text="Movie Details", font=("Helvetica", 65, "bold"), text_color="white").pack(pady=20)

        # 2. MOVIE TITLE (Classic Font)
        title = self.movie.get("title", "Unknown Title")
        ctk.CTkLabel(self.scroll, text=title, font=("Georgia", 40, "italic"), text_color="white").pack(pady=(10, 30))

        content_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        content_frame.pack(fill="x", padx=50)

        # 3. SYNOPSIS SECTION
        synopsis_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        synopsis_frame.pack(fill="x", pady=20)
        
        ctk.CTkLabel(synopsis_frame, text="Synopsis", font=("Helvetica", 16, "bold"), text_color="white", width=150, anchor="nw").pack(side="left", fill="y")
        
        synopsis_text = self.movie.get("description", self.movie.get("synopsis", "No synopsis available for this movie."))
        ctk.CTkLabel(synopsis_frame, text=synopsis_text, font=("Helvetica", 14), text_color="#DDDDDD", wraplength=700, justify="left").pack(side="left", fill="both", expand=True)

        ctk.CTkFrame(content_frame, fg_color="#333", height=1).pack(fill="x", pady=10)

        # 4. GENRE & PLATFORMS SECTION
        mid_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        mid_frame.pack(fill="x", pady=20)

        # Kiri: Genres (Red Pills) + Star Ratings
        left_mid = ctk.CTkFrame(mid_frame, fg_color="transparent")
        left_mid.pack(side="left", fill="y")

        genre_row = ctk.CTkFrame(left_mid, fg_color="transparent")
        genre_row.pack(anchor="w")
        raw_genre = self.movie.get("genre", "General")
        genres = [g.strip() for g in raw_genre.split(",")] if isinstance(raw_genre, str) else raw_genre
        for g in genres[:3]:
            ctk.CTkButton(genre_row, text=g, fg_color="#990000", text_color="white", hover=False, corner_radius=20, height=35, font=("Helvetica", 13, "bold")).pack(side="left", padx=(0, 10))

        rating_val = self.movie.get("rating", "N/A")
        stars = "★" * int(float(rating_val)//2) if rating_val != "N/A" else "★★★"
        ctk.CTkLabel(left_mid, text=f"{stars} {rating_val}/10", font=("Helvetica", 20, "bold"), text_color="#FF3333").pack(anchor="w", pady=(15, 0))

        # Kanan: Where To Watch (Badges)
        # Kanan: Where To Watch (Badges/Logos)
        right_mid = ctk.CTkFrame(mid_frame, fg_color="transparent")
        right_mid.pack(side="right", fill="y", anchor="e")
        
        ctk.CTkLabel(right_mid, text="Where To Watch:", font=("Helvetica", 14, "bold"), text_color="white").pack(anchor="e", pady=(0, 10))
        
        plat_row = ctk.CTkFrame(right_mid, fg_color="transparent")
        plat_row.pack(anchor="e")

        # Ambil data teks platform dan data link logo dari database
        platform_str = self.movie.get("platform_string", "")
        platforms = [p.strip() for p in platform_str.split(",")] if platform_str else []
        logo_urls = self.movie.get("logo_urls", [])

        # Skenario 1: Kalau ada link logonya
        if logo_urls:
            for i, url in enumerate(logo_urls[:4]):
                try:
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    raw_data = urllib.request.urlopen(req, timeout=5).read()
                    image = Image.open(io.BytesIO(raw_data))
                    logo_img = ctk.CTkImage(light_image=image, dark_image=image, size=(40, 40))
                    ctk.CTkLabel(plat_row, text="", image=logo_img).pack(side="left", padx=5)
                
                except Exception as e:
                    print(f"❌ Gagal load logo dari {url}: {e}") 
                    
                    fallback_text = platforms[i] if i < len(platforms) else "Unknown"
                    ctk.CTkButton(plat_row, text=fallback_text, fg_color="#222", hover=False, corner_radius=20, height=35).pack(side="left", padx=5)
        
        # Skenario 3: Kalau gak ada link logonya, tapi ada teks platformnya
        elif platforms:
            for p in platforms[:4]:
                if p: 
                    ctk.CTkButton(plat_row, text=p, fg_color="#222", border_color="white", border_width=1, text_color="white", hover=False, corner_radius=20, height=35).pack(side="left", padx=5)
        
        # Skenario 4: Kosong sama sekali
        else:
            ctk.CTkLabel(plat_row, text="Not Available Online", text_color="gray").pack()

        # 5. DYNAMIC CHART SECTION (Horizontal, Red Bars)
        chart_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        chart_frame.pack(fill="x", pady=(40, 20), anchor="w")
        
        ctk.CTkLabel(chart_frame, text=f"Ratings {rating_val}", font=("Helvetica", 24, "bold"), text_color="white").pack(anchor="w", pady=(0,20))

        ratings_data = self._generate_dynamic_chart(rating_val)
        for score in sorted(ratings_data.keys(), reverse=True):
            value = ratings_data[score]
            row = ctk.CTkFrame(chart_frame, fg_color="transparent")
            row.pack(fill="x", pady=5)
            
            ctk.CTkLabel(row, text=str(score), font=("Helvetica", 14), text_color="white", width=30, anchor="w").pack(side="left")
            
            fill_width = max(5, int(value * 500)) 
            bar = ctk.CTkFrame(row, fg_color="#C00000", height=24, width=fill_width, corner_radius=5)
            bar.pack(side="left", padx=10)
            bar.pack_propagate(False)

        # 6. MORE STORIES
        more_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        more_frame.pack(fill="x", pady=(50, 20))
        ctk.CTkLabel(more_frame, text="More Stories", font=("Helvetica", 18, "bold"), text_color="white", width=150, anchor="nw").pack(side="left", fill="y")
        
        posters_frame = ctk.CTkFrame(more_frame, fg_color="transparent")
        posters_frame.pack(side="left", fill="both", expand=True)
        # Bikin 3 placeholder poster kotak
        for i in range(3):
            p = ctk.CTkFrame(posters_frame, fg_color="#2A2A2A", width=150, height=220, corner_radius=10)
            p.pack(side="left", padx=(0, 20))
            p.pack_propagate(False)
            ctk.CTkLabel(p, text="Poster", text_color="#555").place(relx=0.5, rely=0.5, anchor="center")

        # 7. WATCHLIST BANNER (Oranye Terang)
        banner = ctk.CTkFrame(self.scroll, fg_color="#FF8C00", corner_radius=0, height=200)
        banner.pack(fill="x", pady=(50, 0))
        banner.pack_propagate(False)
        
        ctk.CTkLabel(banner, text="Don't forget your Watchlist!", font=("Georgia", 32, "italic"), text_color="black").pack(pady=(40, 5))
        ctk.CTkLabel(banner, text="Update it and discover what to watch next.", font=("Helvetica", 14, "bold"), text_color="black").pack()
        
        ctk.CTkButton(banner, text="Go to Watchlist", fg_color="#1A1A1A", text_color="white", font=("Helvetica", 14, "bold"), height=40, corner_radius=5, command=lambda: self.app.show_page("watchlist")).pack(pady=20)