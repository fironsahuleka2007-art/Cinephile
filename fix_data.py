import json
import html
import os

DATA_FILE = "data_film.json"

def fix_html_entities(obj):
    """Rekursif decode HTML entities di semua string dalam data"""
    if isinstance(obj, str):
        return html.unescape(obj)
    elif isinstance(obj, list):
        return [fix_html_entities(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: fix_html_entities(value) for key, value in obj.items()}
    return obj

def main():
    if not os.path.exists(DATA_FILE):
        print(f"File {DATA_FILE} tidak ditemukan!")
        return

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Total film: {len(data)}")
    print("Memperbaiki HTML entities...")

    fixed_data = fix_html_entities(data)

    # Cek & tampilkan yang berubah
    changed = 0
    for original, fixed in zip(data, fixed_data):
        if original.get("title") != fixed.get("title"):
            print(f"  ✓ Fix: '{original['title']}' → '{fixed['title']}'")
            changed += 1

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(fixed_data, f, indent=4, ensure_ascii=False)

    print(f"\nSelesai! {changed} judul diperbaiki.")
    print(f"Data disimpan ke {DATA_FILE}")

if __name__ == "__main__":
    main()