from scraper import MovieScraper

s = MovieScraper()
s.scrape_top_movies(limit=250)
s.close()

print("SELESAI!")