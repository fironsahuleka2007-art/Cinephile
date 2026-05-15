import json, os

with open("data_film.json", "r", encoding="utf-8") as f:
    movies = json.load(f)

no_path_titles = ["Léon", "Rear Window", "Dune: Part Two", 
                  "Avengers: Infinity War", "Toy Story", "Capharnaüm"]

for m in movies:
    if m.get("title") in no_path_titles:
        m["poster_local"] = ""
        print(f"Reset path: {m['title']}")

with open("data_film.json", "w", encoding="utf-8") as f:
    json.dump(movies, f, indent=4, ensure_ascii=False)

print("Selesai!")