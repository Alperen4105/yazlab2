#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()
from backend.clients import search_tmdb_movies, search_google_books

# Test film arama
print('=== TMDb Film Araması Test ===')
results = search_tmdb_movies('avatar', limit=5)
print(f'Sonuçlar: {len(results)} film bulundu')
if results:
    for r in results[:2]:
        print(f'  - {r.get("title")} ({r.get("year")})')
else:
    print('  Sonuç yok (network hatası veya API key eksik)')

print()
print('=== Google Books Araması Test ===')
results = search_google_books('python', limit=5)
print(f'Sonuçlar: {len(results)} kitap bulundu')
if results:
    for r in results[:2]:
        print(f'  - {r.get("title")} ({r.get("year")})')
else:
    print('  Sonuç yok (network hatası veya API key eksik)')
