"""
fix_posters.py
Jalankan: python fix_posters.py
Script ini cari file poster yang kosong (0 byte atau corrupt),
lalu re-download dari URL IMDb menggunakan data di data_film.json.
Kalau URL tidak ada di JSON, fallback ke pencarian IMDb.
"""

import json
import os
import urllib.request
import urllib.parse
import time

DATA_FILE = "data_film.json"
POSTERS_DIR = "posters"


def is_valid_image(path):
    """Cek apakah file gambar valid (tidak kosong dan bisa dibaca)"""
    if not os.path.exists(path):
        return False
    if os.path.getsize(path) < 1000:  # < 1KB = pasti rusak
        return False
    # Coba baca header file (JPEG dimulai dengan FF D8)
    try:
        with open(path, "rb") as f:
            header = f.read(3)
            return header[:2] == b'\xff\xd8' or header[:3] == b'\x89PNG'
    except:
        return False


def search_imdb_poster(title, year):
    """Cari poster dari IMDb search"""
    try:
        query = urllib.parse.quote(f"{title} {year}")
        search_url = f"https://www.imdb.com/find/?q={query}&s=tt&ttype=ft"
        req = urllib.request.Request(
            search_url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        # Kita tidak bisa parse HTML tanpa selenium di sini
        # Jadi fallback: cari dari poster_url kalau ada di JSON
        return None
    except:
        return None


def download_poster(url, path):
    """Download gambar dari URL ke path"""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        with urllib.request.urlopen(req, timeout=10) as response, open(path, "wb") as out:
            out.write(response.read())
        return is_valid_image(path)
    except Exception as e:
        print(f"  Gagal download: {e}")
        return False


def fix_posters_via_selenium(broken_movies):
    """Re-scrape poster untuk film yang rusak menggunakan Selenium"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from webdriver_manager.chrome import ChromeDriverManager
        import json as _json

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")

        print("Menyiapkan WebDriver untuk re-scrape poster...")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        wait = WebDriverWait(driver, 10)
        fixed = 0

        for movie in broken_movies:
            title = movie.get("title", "")
            year = movie.get("year", "")
            local_path = movie.get("poster_local", "")

            print(f"  Re-scrape poster: {title}...")
            try:
                # Cari di IMDb
                query = urllib.parse.quote(f"{title}")
                driver.get(f"https://www.imdb.com/find/?q={query}&s=tt&ttype=ft")
                time.sleep(1.5)

                # Klik hasil pertama
                first = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "a.ipc-metadata-list-summary-item__t")
                ))
                driver.get(first.get_attribute("href"))
                time.sleep(2)

                # Ambil poster URL dari ld+json
                script_tag = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//script[@type='application/ld+json']")
                ))
                data = _json.loads(script_tag.get_attribute("innerHTML"))
                poster_url = data.get("image", "")

                if poster_url:
                    success = download_poster(poster_url, local_path)
                    if success:
                        print(f"  ✓ Poster fixed: {local_path}")
                        fixed += 1
                    else:
                        print(f"  ✗ Download gagal untuk {title}")
                else:
                    print(f"  ✗ Tidak ada URL poster untuk {title}")

            except Exception as e:
                print(f"  ✗ Error scrape {title}: {e}")

            time.sleep(1)

        driver.quit()
        return fixed

    except ImportError:
        print("Selenium tidak tersedia.")
        return 0


def main():
    # Load data film
    if not os.path.exists(DATA_FILE):
        print(f"File {DATA_FILE} tidak ditemukan!")
        return

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        movies = json.load(f)

    print(f"Total film di database: {len(movies)}")
    print("Mengecek poster yang rusak/kosong...\n")

    broken = []
    missing = []

    for movie in movies:
        path = movie.get("poster_local", "")
        title = movie.get("title", "Unknown")

        if not path:
            missing.append(movie)
            print(f"  [NO PATH]  {title}")
        elif not os.path.exists(path):
            missing.append(movie)
            print(f"  [MISSING]  {title} → {path}")
        elif not is_valid_image(path):
            broken.append(movie)
            size = os.path.getsize(path)
            print(f"  [CORRUPT]  {title} → {path} ({size} bytes)")

    print(f"\nTotal rusak/kosong: {len(broken) + len(missing)} film")
    print(f"  - File corrupt/kosong : {len(broken)}")
    print(f"  - File tidak ada      : {len(missing)}")

    if not broken and not missing:
        print("\n✅ Semua poster valid!")
        return

    all_broken = broken + missing
    print(f"\nMulai re-download {len(all_broken)} poster...\n")

    fixed = fix_posters_via_selenium(all_broken)

    print(f"\n=== SELESAI ===")
    print(f"  Berhasil difix : {fixed}")
    print(f"  Masih rusak    : {len(all_broken) - fixed}")


if __name__ == "__main__":
    main()