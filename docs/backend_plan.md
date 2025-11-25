# Backend Skeleton Plan

Bu bölüm, frontend prototipini gerçek veriyle besleyecek Python tabanlı backend servisinin iskeletini anlatır. Adımları kodlamaya başlamadan önce netleştirmek, ileride yapılacak mimari kararların tutarlı olmasını sağlar.

## 1. Teknoloji Yığını

- **Framework:** Flask (REST API için Blueprint yapısı).
- **Veritabanı erişimi:** SQLAlchemy + Alembic (migration).
- **Kimlik doğrulama:** JSON Web Token (PyJWT) veya Flask-JWT-Extended.
- **Dış servisler:** TMDb, Google Books/Open Library (requests + basit caching).

## 2. Proje Yapısı

```
backend/
  __init__.py
  config.py
  extensions.py        # db, migrate, jwt gibi init fonksiyonları
  models/              # SQLAlchemy modelleri
  api/
    __init__.py
    auth/routes.py
    feed/routes.py
    content/routes.py
    profiles/routes.py
  services/
    tmdb_client.py
    books_client.py
  schemas/             # Marshmallow / pydantic yanıt modelleri
```

Frontend’in kullandığı HTML view’leri korumak için mevcut `app.py` dosyasını “web” katmanı olarak bırakabilir, API Blueprint’lerini `backend` paketinden import edip `/api/...` altında yayınlayabiliriz.

## 3. Yapılandırma Katmanı

- `config.py` içinde Dev/Staging/Prod sınıfları.
- `.env` dosyasından API anahtarları, DB URL, JWT secret okunur.
- `create_app()` fonksiyonu bu config’i yükler, blueprint ve uzantıları kaydeder.

## 4. Ortak Uzantılar

- `extensions.py`: `db = SQLAlchemy()`, `migrate = Migrate()`, `jwt = JWTManager()` vb.
- App factory’de `extensions.init_app(app)` şeklinde çağrılacak.

## 5. Blueprint İskeleti

Her feature alanı için ayrı blueprint:

- `auth_bp`: `/api/auth/login`, `/api/auth/register`, `/api/auth/refresh`
- `feed_bp`: `/api/feed`, `/api/feed/<int:page>`
- `content_bp`: `/api/content/<content_id>`, `/api/search`
- `profiles_bp`: `/api/profiles/<username>`, `/api/profiles/<username>/library`

Blueprint’ler request doğrulaması ve hata yönetimi için ortak yardımcı fonksiyon kullanır.

## 6. Harici Servis Katmanı

- `tmdb_client.py` ve `books_client.py` dosyaları dış API çağrılarını soyutlar.
- Basit bir cache (örn. `functools.lru_cache` veya Redis’e hazır olacak interface) ile gereksiz istekler azaltılır.
- Servis katmanı API cevaplarını normalize ederek içerik modellerine uygun hale getirir.

## 7. Test Stratejisi

- Pytest + Flask test client.
- `tests/` dizininde unit (service) ve integration (API) testleri.
- Örnek db için SQLite in-memory + fixture verileri.

Bu plan tamamlandıktan sonra ikinci adım olan veritabanı şemasını tasarlamaya geçebiliriz.

