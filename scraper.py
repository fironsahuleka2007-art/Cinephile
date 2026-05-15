import os
import time
import random
import urllib.request
import urllib.parse
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

DATA_FILE = "data_film.json"

class MovieScraper:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

        print("Menyiapkan WebDriver...")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)

        if not os.path.exists("posters"):
            os.makedirs("posters")

    # ─────────────────────────────────────────────
    # HELPER: load & save data_film.json
    # ─────────────────────────────────────────────
    def _load_existing(self):
        """Muat data film yang sudah ada agar bisa di-resume."""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

    def _save_all(self, data):
        """Simpan seluruh list ke data_film.json (dipanggil tiap film selesai)."""
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    # ─────────────────────────────────────────────
    # JUSTWATCH
    # ─────────────────────────────────────────────
    def scrape_justwatch_data(self, title):
        detail = {
            "synopsis": "No synopsis available.",
            "genre": "N/A",
            "platforms": "Not Available Online",
            "year": "Unknown"
        }
        try:
            search_url = f"https://www.justwatch.com/id/search?q={urllib.parse.quote(title)}"
            self.driver.get(search_url)

            first_result = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.title-list-row__column-header, a.title-card-link"))
            )
            self.driver.get(first_result.get_attribute("href"))
            time.sleep(2)

            # Synopsis
            try:
                synopsis_el = self.driver.find_element(By.CSS_SELECTOR, "#synopsis p, p.text-wrap-pre-line.mt-0")
                if synopsis_el.text.strip():
                    detail["synopsis"] = synopsis_el.text.strip()
            except: pass

            # Genre
            try:
                headings = self.driver.find_elements(By.CSS_SELECTOR, "h3.detail-infos__subheading")
                for heading in headings:
                    if "Genre" in heading.text:
                        parent = heading.find_element(By.XPATH, "..")
                        value_div = parent.find_element(By.CSS_SELECTOR, "div.detail-infos__value")
                        detail["genre"] = value_div.text.strip()
                        break
            except: pass

            # Tahun (backup)
            try:
                year_el = self.driver.find_element(By.CSS_SELECTOR, "div.title-block span.text-muted")
                year_text = year_el.text.replace("(", "").replace(")", "").strip()
                if year_text.isdigit():
                    detail["year"] = year_text
            except: pass

            # Platform
            try:
                logo_elements = self.driver.find_elements(By.CSS_SELECTOR, "img.provider-icon")
                nama_platform_list = []
                for logo in logo_elements:
                    nama_platform = logo.get_attribute("alt")
                    if nama_platform and nama_platform not in nama_platform_list:
                        nama_platform_list.append(nama_platform)
                if nama_platform_list:
                    detail["platforms"] = ", ".join(nama_platform_list)
            except: pass

        except Exception as e:
            print(f"  [JustWatch] Tidak ditemukan untuk '{title}': {e}")

        return detail

    # ─────────────────────────────────────────────
    # IMDB DETAIL (dengan retry)
    # ─────────────────────────────────────────────
    def _get_movie_details(self, url, retries=3):
        for attempt in range(retries + 1):
            try:
                self.driver.get(url)
                # Jeda acak 2-5 detik biar tidak kena rate-limit IMDb
                time.sleep(random.uniform(2, 5))

                script_tag = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, "//script[@type='application/ld+json']"))
                )
                json_text = script_tag.get_attribute("innerHTML")
                data = json.loads(json_text)

                title = data.get("name", "Unknown Title")
                genre_raw = data.get("genre", ["General"])
                genre = ", ".join(genre_raw) if isinstance(genre_raw, list) else genre_raw
                year = data.get("datePublished", "Unknown").split("-")[0] if "datePublished" in data else "Unknown"
                rating = str(data.get("aggregateRating", {}).get("ratingValue", "N/A"))
                poster = data.get("image", "")

                # Ambil synopsis dari IMDb sebagai fallback
                synopsis = "No synopsis available."
                try:
                    syn_el = self.driver.find_element(By.CSS_SELECTOR, "span[data-testid='plot-l'], span[data-testid='plot-xl']")
                    if syn_el.text.strip():
                        synopsis = syn_el.text.strip()
                except: pass

                return {
                    "title": title, "year": year, "genre": genre, "rating": rating,
                    "poster_url": poster, "status": "Plan to Watch",
                    "imdb_synopsis": synopsis
                }
            except Exception as e:
                if attempt < retries:
                    wait_time = (attempt + 1) * 5  # makin lama tiap retry: 5s, 10s, 15s
                    print(f"  [IMDb] Retry {attempt+1}/{retries} (tunggu {wait_time}s)...")
                    time.sleep(wait_time)
                else:
                    return {"error": str(e)}

    # ─────────────────────────────────────────────
    # MAIN: scrape top movies dengan RESUME
    # ─────────────────────────────────────────────
    def scrape_top_movies(self, limit=250, progress_callback=None):
        """
        Scrape top movies dari IMDb dengan fitur:
        - Resume: skip film yang sudah ada di data_film.json
        - Auto-save: simpan tiap film selesai (aman kalau crash)
        - Retry: coba ulang otomatis kalau gagal
        - Progress callback: untuk update UI
        """
        print(f"Memulai scraping {limit} film teratas dari IMDb Top 250...")

        # Load data yang sudah ada (untuk resume)
        hasil_list = self._load_existing()
        existing_titles = {m.get("title", "").lower() for m in hasil_list}
        print(f"  → {len(existing_titles)} film sudah ada, akan di-skip.")

        try:
            self.driver.get("https://www.imdb.com/chart/top/")
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.ipc-metadata-list-summary-item")))
            links = self.driver.find_elements(By.CSS_SELECTOR, "a.ipc-title-link-wrapper")
            urls = [link.get_attribute("href") for link in links[:limit]]
            print(f"  → Berhasil ambil {len(urls)} URL dari IMDb Top Chart.")
        except Exception as e:
            print(f"Gagal mengambil daftar Top Movies: {e}")
            return hasil_list

        skipped = 0
        scraped = 0
        failed = 0

        for i, url in enumerate(urls):
            # Cek dulu apakah film ini sudah ada (resume support)
            # Ambil title preview dari URL sebagai hint
            try:
                # Kita cek dengan scraping ringan dulu
                self.driver.get(url)
                script_tag = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, "//script[@type='application/ld+json']"))
                )
                preview_data = json.loads(script_tag.get_attribute("innerHTML"))
                preview_title = preview_data.get("name", "").lower()

                if preview_title in existing_titles:
                    print(f"[{i+1}/{limit}] SKIP (sudah ada): {preview_data.get('name')}")
                    skipped += 1
                    if progress_callback:
                        progress_callback(i + 1, limit, f"Skip: {preview_data.get('name')}", scraped, skipped, failed)
                    continue
            except:
                pass  # Kalau preview gagal, lanjut scraping normal

            print(f"[{i+1}/{limit}] Scraping: {url.split('/title/')[1][:15] if '/title/' in url else '...'}...")

            detail = self._get_movie_details(url)

            if "error" in detail:
                print(f"  [GAGAL] {detail['error']}")
                failed += 1
                if progress_callback:
                    progress_callback(i + 1, limit, f"Gagal film ke-{i+1}", scraped, skipped, failed)
                continue

            title = detail.get("title", "")

            # Double-check setelah dapat title lengkap
            if title.lower() in existing_titles:
                print(f"  SKIP (sudah ada): {title}")
                skipped += 1
                if progress_callback:
                    progress_callback(i + 1, limit, f"Skip: {title}", scraped, skipped, failed)
                continue

            # Scrape JustWatch
            print(f"  → Ambil data JustWatch untuk '{title}'...")
            jw_data = self.scrape_justwatch_data(title)

            detail["description"] = jw_data["synopsis"] if jw_data["synopsis"] != "No synopsis available." else detail.get("imdb_synopsis", "No synopsis available.")
            detail["platform_string"] = jw_data["platforms"]
            detail.pop("imdb_synopsis", None)

            if jw_data.get("genre") != "N/A":
                detail["genre"] = jw_data["genre"]

            if detail.get("year") == "Unknown" and jw_data.get("year") != "Unknown":
                detail["year"] = jw_data["year"]

            # Download poster
            img_url = detail.get("poster_url", "")
            if img_url and img_url.startswith("http"):
                safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c == ' ']).rstrip()
                local_path = f"posters/{safe_title.replace(' ', '_')}.jpg"
                try:
                    req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=5) as response, open(local_path, 'wb') as out_file:
                        out_file.write(response.read())
                    detail["poster_local"] = local_path
                    print(f"  → Poster disimpan: {local_path}")
                except Exception as pe:
                    print(f"  [Poster] Gagal download: {pe}")
                    detail["poster_local"] = ""
            else:
                detail["poster_local"] = ""

            detail.pop("poster_url", None)

            # Tambah ke list & langsung save (aman kalau crash)
            hasil_list.append(detail)
            existing_titles.add(title.lower())
            self._save_all(hasil_list)
            scraped += 1

            print(f"  ✓ Tersimpan! Total sekarang: {len(hasil_list)} film.")

            if progress_callback:
                progress_callback(i + 1, limit, f"✓ {title}", scraped, skipped, failed)

            # Jeda acak antar film biar tidak kena rate-limit
            time.sleep(random.uniform(2, 4))

        print(f"\n=== SELESAI ===")
        print(f"  Baru di-scrape : {scraped}")
        print(f"  Di-skip        : {skipped}")
        print(f"  Gagal          : {failed}")
        print(f"  Total di DB    : {len(hasil_list)} film")

        return hasil_list

    def search_movie(self, query):
        pass

    def close(self):
        self.driver.quit()