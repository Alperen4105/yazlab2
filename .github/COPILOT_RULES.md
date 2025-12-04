# Copilot / AI Yardım Kuralları — proje genel rehberi

Bu dosya, bu repository (yazlab2) içinde Copilot ve diğer yapay zeka destekli kod/komut üreticilerini ("Copilot", "assistant", "AI yardımcısı") kullanırken uyulması gereken kuralları açıklar. Hem güvenlik, hem hukuki, hem de kalite/iş akışı sebepleriyle tüm katkıda bulunanların bu kurallara uyması beklenir.

Önemli: Bu rehber, kodu otomatik üreten araçların tamamen yasaklanması anlamına gelmez — doğru, gözden geçirilmiş ve test edilmiş kullanıma izin verir. Ancak otomatik çıktılar her zaman insan tarafından incelenmeli ve projeye uygunluk, güvenlik ve lisans uyumluluğu kontrol edilmelidir.

---

## 1) Kapsam ve amaç
- Bu proje için Copilot/AI araçları aşağı amaçlar için kullanılabilir:
  - Tekrarlayan kod şablonları (ör. CRUD boilerplate) üretimi ve önerileri
  - Birim testleri için örnek test gövdeleri oluşturma
  - Belgelendirme taslakları veya README iyileştirmeleri
  - Karmaşık ama tekrarlı mantık için öneri ve açıklama (developer yardımcısı)

- Aşağı durumlar için Copilot çıktıları SADECE referans olarak kullanılmalı (doğrudan commit edilmeyecek):
  - Tasarım kararları (mimari değişiklikler)
  - Güvenlik kritik kod (auth, crypto, SQL sorgu inşa, input validation)
  - Gizli veya hassas bilgi (API anahtarları, parolalar) içerebilecek öneriler

## 2) Güvenlik & gizlilik
- AI tarafından üretildiği öne sürülen kodlar insan tarafından gözden geçirilmeli ve testsiz commit edilmemelidir.
- Hiçbir durumda Copilot çıktısı doğrudan secrets (anahtarlar, şifreler, kişisel veriler) içermemelidir. Eğer öneri içinde böyle içerik görülürse, derhal silinmeli ve güvenli alternatif (örn. env değişkeni kullanım) tercih edilmelidir.
- Test veya demo amaçlı gizli değer kullanılması gerekiyorsa, bunun yerine proje içindeki `.env.example` veya fixtures/test-data içine dummy değer konulmalı — gerçek secret'lar repo veya testler içine asla konmamalıdır.

## 3) Lisans & telif
- Copilot tarafından üretilen kod parçalarının lisans durumu, üretici araç tarafından geldikleri verilerin kaynağına dayanabilir. Bu yüzden:
  - Üretilen koda ait orijin ve lisans açısından emin olunamadığında (özellikle büyük, benzersiz snippetler) doğrudan eklemeyin.
  - Üretilen uzun veya benzersiz kod blokları varsa, kodu basitleştirin veya yeniden yazın; gerektiğinde kaynakça/attribution ekleyin.

## 4) Kod kalitesi, test ve review gereksinimleri
- Copilot ile üretilen her yeni işlev veya değişiklik için:
  - Sorumlu geliştirici manuel code review yapmalı.
  - Gerekli birim/entegrasyon testleri eklenmeli veya var olanlar güncellenmeli.
  - Yeni kod için `pytest` testleri çalıştırılmalı ve CI (varsa) üzerinde başarılı olmalı.
- Kod stili (PEP8/formatting) otomatik araçlarla düzeltilmeli; büyük biçim değişiklikleri ayrı commit olarak yapılmalıdır.

## 5) Pull Request ve PR checklist
- PR açarken aşağıdaki maddeler Copilot-üretimli katkılar için zorunludur:
  - "Bu PR Copilot veya benzeri bir AI yardımcıyla üretilen kod içeriyor" şeklinde kısa bir açıklama.
  - Hangi kısımların otomatik üretildiği ve nelerin elle düzeltildiğinin kısa özeti.
  - Eklenen/aydınlatılan testlerin çalıştığını gösteren CI başarısı (veya `pytest` çıktısı yerel olarak).

## 6) Güvenli örnek kullanım pratikleri
- Örnek: bir fonksiyon şablonu Copilot ile üretildiyse:
  - Fonksiyonun giriş/çıkış davranışı, hata koşulları, sınır durumları el ile doğrulanmalı.
  - SQL sorguları veya dış kaynak çağrıları için parametre bağlama, input doğrulama ve timeout kontrolü eklenmeli.

## 7) İstisnalar ve acil durumlar
- Kritik güvenlik fix'leri: eğer bir güvenlik açığı hızlıca kapatılması gerekiyorsa ve Copilot bir patche yardımcı olduysa, yine de ilgili uzman tarafından review edilip test edilmeli. Eğer zaman kısıtlıysa, PR açıklamasına bu durum net yazılmalıdır.

## 8) Araç & yapılandırma tavsiyeleri
- Editor/IDE tarafında Copilot veya AI-assistant özelliği kullananlar için öneriler:
  - `Copilot` veya benzeri eklentileri açmadan önce `git status` kontrol edin; büyük, otomatik eklemeleri commit etmeden önce gözden geçirin.
  - Otomatik completions için güvenli bir `.editorconfig` / linter kombinasyonu kullanın.

## 9) Sıkça sorulan kısa kurallar (hızlı rehber)
- Commit etmeye hazır ol: AI çıktılarını *inceleyin* => *düzeltin* => *test edin* => *commit edin*.
- Gizli bilgiyi commit etmeyin. Düşük güvenliğe sahip önerileri iptal edin.
- Lisans konusunda şüphe varsa, parçayı yeniden yazın veya maintainerlara danışın.

---

Eğer isterseniz, bu kuralları `README.md` içinde kısa bir başlıkla işaretleyebilirim (katkıda bulunanlar için görünür link). Daha sonra CI konfigürasyonuna (örn. bir `pre-commit` hook ile) basit bir uyarı mekanizması eklemek de faydalı olacaktır.

Teşekkürler — bu rehberi repo seviyesinde tutarlı şekilde uygulamak proje güvenliği ve kalitesi için yardımcı olacaktır.

---

## Proje mimarisi, veritabanı ve kullanılan ana fonksiyonlar (özet)

Aşağıda repository içindeki "neden" ve "nerede" sorularına pratik, kısa ve geliştirici-odaklı cevaplar yer alır — bu kısım dokümantasyon amaçlıdır ve `backend/` içindeki dosyalara referans verir.

### 1) Genel yapı
- `app.py` — uygulamanın giriş noktası; frontend yüzü (`templates/`) ile `backend` API istemcisini bağlar (`backend.init_app`).
- `backend/` — uygulamanın sunucu tarafı mantığı:
  - `api/__init__.py` — REST benzeri endpoint'lerin tamamı (feed, explore, content-detail, auth, ratings, reviews, library, lists, follow, reactions vb.). UI'nin veri kaynağı burada bulunur.
  - `clients.py` — dış kaynak (TMDb, Google Books, OpenLibrary) için küçük helper fonksiyonlar; arama ve detay çekme; ayrıca (development amaçlı) in-memory TTL cache ve basit per-provider rate limiter içerir.
  - `models/__init__.py` — SQLAlchemy modelleri; kullanıcılar, içerikler, rating, review, liste ve activity tabloları yer alır.
  - `fixtures.py` ve `data/sample_data.py` — başlangıç verisi ve test/demo için sabit içerikler.

### 2) Neden bu fonksiyonlar ve ne için kullanılıyor — clients (dış API) tarafı
Ana klient fonksiyonlar ve kullanım amaçları:

- `search_tmdb_movies(query, limit)`
  - Ne yapar: TMDb (The Movie Database) araması yapar, dönene sonuçları proje formatına (mapping) çevirir.
  - Neden var: Kullanıcılar keşfetirken DB'de olmayan film içeriklerini bulmak ve (opsiyonel) ingest etmek için kullanılır.
  - Önemli not: fonksiyon artık bir in-memory cache kullanır (anahtar: `tmdb:search:<query>:<limit>`) ve per-provider rate limiter (`tmdb`) ile quota korunur.

- `search_google_books(query, limit)`
  - Ne yapar: Google Books (varsa) kullanır; yoksa Open Library'e rağbet eder. Sonuçları uygulama standardına çevirir (`page_count`, `poster`, `title`, `year` vb.).
  - Neden var: Keşfet ve arama senaryolarında kitaplar için dış kaynak sağlayıcı.
  - Önemli not: Benzer şekilde cache (`google:search:<query>:<limit>`) ve rate limiter (`google`) kullanır.

- `get_tmdb_movie_details(external_id)`
  - Ne yapar: Belirtilen TMDb id'si için detay (runtime, poster, title, vb.) çeker, map'leyip döner ve cache'e kaydeder (`tmdb:detail:<external_id>`). Eğer rate limit aşılmışsa None dönebilir.
  - Neden: Content-detail sayfası DB'de olmayan `mov-...` external_id'ler için canlı detay sağlamak amacıyla.

- `get_book_details(external_id)`
  - Ne yapar: `book-<id>` için Google Books veya OpenLibrary üzerinden detay getirir; map'ler ve cache'e kaydeder.
  - Neden: Content-detail sayfası veya canlı kaynak gösterimleri için kitap detayının anlık alınması.

- `_cache_get` / `_cache_set` / `_rate_allow`
  - Ne yapar: küçük, process-local, TTL bazlı cache ve dakika-temelli sayaç ile rate limit uygular.
  - Neden: geliştirme ortamında API çağrı sayısını sınırlamak, test/speed stabilitesi sağlamak. (Not: production için Redis gibi merkezi bir cache tercih edilir.)

### 3) API katmanı — nerede ne yapılıyor (`backend/api/__init__.py`)
- `api/feed`: Kullanıcının takip ettiği kişiler veya genel aktiviteler. Kaynak: DB (Activity). Fallback sample data.
- `api/explore`: DB öncelikli arama; DB'de sonuç yoksa dış API'lar ile arama yapılır. External ingest opsiyoneldir (ENV: `INGEST_EXTERNAL_RESULTS`).
- `api/content/<id>`: DB'de varsa persisted detay döner; DB yoksa external_id pattern'lerine göre canlı detay çekilir (`get_tmdb_movie_details` / `get_book_details`) ve frontende tek-seferlik sonuç sağlanır.
- ratings, reviews, reactions, library, lists, follow endpoints: kullanıcı etkileşimleri ve ilişkisel veritabanı işlemleri (create/update/delete + activity kaydı işlemleri).

### 4) Veritabanı modeli ve ilişkiler (`backend/models/__init__.py`)
Ana tablolar:

- `User` (users) — temel kullanıcı kaydı, takip ilişkisi (`Follow`), avatar, profil bilgisi.
- `Follow` (follows) — many-to-many (self-referential) takip tablosu; (follower_id, followed_id) kompozit anahtar.
- `Content` (contents) — içerik kayıtları: `external_id`, `content_type` (movie/book), `title`, `runtime_minutes`, `page_count`, `cover_url`, `extra_metadata`.
- `LibraryItem` (library_items) — kullanıcı kütüphanelerine eklenen içerikler (`status`: watched/watchlist/read/reading_list).
- `Rating` (ratings) — user-content tekil puan (unique constraint user+content).
- `Review` (reviews) — user-content yorumları; zaman damgaları ve update takibi.
- `ReviewReaction` (review_reactions) — kullanıcıların review'ler üzerindeki like/dislike tepkileri.
- `Activity` (activities) — kullanıcı aktivitelerini özetleyen (rating, review, list_add, library_status) kayıtlar. Feed ekranı bu tablodan beslenir.
- `PasswordReset` (password_resets) — parola sıfırlama token'ları; user_id, token (unique), used flag, expires_at.

### 5) Neden böyle bir yapı? (kısa gerekçe)
- Ayrık komponentler (clients vs api vs models) kodun test edilebilirliğini ve ileride üretime taşımayı kolaylaştırır.
- DB merkezli model: kalıcı içerikler, kullanıcı etkinlikleri ve ilişkiler izlenebilir olur.
- Dış kaynaklar için cache & rate limiter (development) ile API maliyeti ve test kararlılığı sağlanır; gerçek üretime taşınırken Redis/Shared rate-limiter tavsiye edilir.

### 6) Test stratejisi
- `tests/` içinde birim + entegrasyon testleri yer alır: clients mapping, explore ingestion, content-detail live gibi kritik davranışlar doğrulanmıştır.
- `conftest.py` DB izolasyonu ve seed işlemleri sağlar — testler izole çalışır.

---

## GÜNCELLEMELER VE SON DURUMU (04.12.2025)

### 🎯 Tamamlanan Özellikler

#### 1. ŞİFREMİ UNUTTUM (Forgot Password) ✅
Güvenli parola sıfırlama sistemi tamamen implementasyonu tamamlandı.

**Veritabanı Tarafı:**
- `backend/models/__init__.py`: Yeni `PasswordReset` modeli oluşturuldu
  - `user_id` (FK), `token` (unique, indexed), `used` (bool), `expires_at`, `created_at`
  - User modeliyle ilişki kuruldu

**API Endpoints:**
- `POST /api/auth/forgot-password` (backend/api/__init__.py satır 510)
  - Email girdisini alır (case-insensitive lookup)
  - `secrets.token_urlsafe(32)` ile güvenli token üretir
  - Parola sıfırlama email'ini gönderir
  - Güvenlik: User varlığını ifşa etmeyen mesaj döner

- `POST /api/auth/reset-password` (backend/api/__init__.py satır 558)
  - Token doğrulaması (geçerli, kullanılmamış, süresi dolmamış)
  - Şifreyi hash'leyip günceller
  - Token'ı kullanılmış işaretler

**Email Sistemi:**
- `backend/mail.py`: Yeni `send_email()` fonksiyonu
  - Gmail SMTP desteği (smtp.gmail.com:587 + STARTTLS)
  - SMTP_SSL desteği (465 portu)
  - Detaylı loglama: bağlantı, TLS, login, gönderim
  - Fallback: SMTP yapılandırılmamış/başarısızsa Flask loguna yazılır
  - Exception handling: SMTPAuthenticationError, SMTPException ayrı ele alınır

**Web Routes:**
- `app.py /forgot-password` (satır 126): GET → form, POST → API çağrısı
- `app.py /reset-password` (satır 144): GET → form, POST → şifre güncelleme
- `api_request()` helper ile internal API çağrıları yapılır

**HTML Templates:**
- `templates/auth/forgot_password.html`: Email input formu
- `templates/auth/reset_password.html`: İki şifre alanı + token field

**Konfigürasyon (.env):**
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=alperenplk.28@gmail.com
SMTP_PASS=<16-basamaklı App Password>
MAIL_FROM=alperenplk.28@gmail.com
APP_BASE_URL=http://127.0.0.1:5000
RESET_TOKEN_EXPIRATION=3600 (varsayılan 1 saat)
```

**Gmail Setup:**
- 2FA aktif hesaplar için Google App Password kullanılmalı
- https://myaccount.google.com/apppasswords → 16 basamaklı şifre alınır
- SMTP_PASS'e eklenirken boşluk olmamalı

**Test Sonuçları:**
✅ `test_smtp.py` — Bağımsız SMTP testi başarılı, email teslim edildi
✅ `test_forgot_endpoint.py` — API endpoint'leri çalışıyor, email gönderiliyor
✅ Backend: %100 çalışıyor ve test edildi

---

#### 2. MOBİL ENTEGRASYON (PWA + Responsive) ✅
Mobil cihazlar için Progressive Web App ve responsive tasarım tamamlandı.

**PWA Manifest:**
- `static/manifest.json` oluşturuldu
  - name, short_name, description, start_url, display: "standalone"
  - theme_color, background_color, icons (192x192, 512x512)
  - Web app olarak home screen'e eklenme özelliği

**Service Worker:**
- `static/service-worker.js` oluşturuldu
  - Cache-first stratejisi: /, /static/styles.css, /static/favicon.png
  - install event: cache oluşturma
  - fetch event: cache → network fallback
  - Offline çalışma desteği (temel sayfalar için)

**Responsive Design:**
- `templates/base.html` güncellemeler:
  - Manifest link eklendi
  - Service worker registration scripti eklendi
  - Hamburger menü butonu (#menuToggle)
  - Mobile overlay (#mobileOverlay) gizleme için
  - JavaScript toggle: nav-open class'ı ile menü kontrolü

- `static/styles.css` yeni media query (max-width: 700px):
  - Navigation: fixed position slide-out sidebar
  - Transform: translateX(100%) → translateX(0) animasyon
  - Overlay: opacity 0 → 0.5 geçişi
  - Touch-friendly: minimum 44x44px tap targets
  - Container padding/margin optimizasyonu
  - Mobile-first yaklaşım

**Mobil UX:**
- Hamburger icon: "☰" karakteri
- Smooth slide-in/out animasyon (0.3s ease-in-out)
- Overlay tıklama → menü kapanır
- Responsive form elemanları
- Tüm ekran boyutlarında uyumlu

**Test Sonuçları:**
✅ Slide-out menu çalışıyor
✅ Overlay animasyonu smooth
✅ Responsive CSS media queries aktif
✅ Service worker kayıtlı
✅ PWA manifest valid

---

### 🔧 Sorun Giderme & Çözümleri

**Problem 1: .env Dosya Formatı**
- Sorun: python-dotenv tırnak işaretlerini literal character olarak okuyor
- Örnek: `SMTP_HOST="smtp.gmail.com"` → `"smtp.gmail.com"` (tırnak dahil)
- Çözüm: Tüm tırınaklar kaldırılmış, boşluk temizlenmiş
- Doğru format: `SMTP_HOST=smtp.gmail.com` (tırnak YOK, boşluk YOK)

**Problem 2: PowerShell Venv Activation**
- Sorun: ExecutionPolicy hatası
- Çözüm: `.venv\Scripts\python.exe` direkt kullan
- Alternatif: `Set-ExecutionPolicy -Scope CurrentUser Unrestricted`

**Problem 3: Gmail 2FA Blokası**
- Sorun: Gmail, 2FA aktif hesaplarda normal şifre kabul etmiyor
- Çözüm: App Password oluştur https://myaccount.google.com/apppasswords
- Not: 16 basamaklı şifre, boşluksuz eklenmelidir

---

### 📊 Dosya Değişiklikleri Özeti

**YENİ DOSYALAR:**
- ✅ backend/mail.py (email gönderimi)
- ✅ templates/auth/forgot_password.html
- ✅ templates/auth/reset_password.html
- ✅ static/manifest.json
- ✅ static/service-worker.js
- ✅ test_smtp.py (debug)
- ✅ test_forgot_endpoint.py (debug)

**DEĞİŞTİRİLEN DOSYALAR:**
- ✅ backend/models/__init__.py (PasswordReset model)
- ✅ backend/api/__init__.py (forgot/reset endpoints + mail import)
- ✅ app.py (forgot/reset routes)
- ✅ templates/base.html (PWA + mobile menu)
- ✅ static/styles.css (mobile responsive)
- ✅ .env (format düzeltildi, tırnak kaldırıldı)

---

### 🚀 Devam Eden & Planlanan

**TAMAMLANDI:**
- ✅ PasswordReset model ve DB schema
- ✅ API endpoints (forgot + reset)
- ✅ SMTP email gönderimi
- ✅ Token generation & validation
- ✅ Web routes & HTML forms
- ✅ Gmail App Password setup
- ✅ PWA manifest
- ✅ Service worker (cache-first)
- ✅ Responsive CSS + mobile menu
- ✅ Detaylı loglama ve debugging
- ✅ Test scriptleri (SMTP + endpoint)

**GELECEK İYİLEŞTİRMELER:**
- 📋 UX toasts + error notifications (inline messages)
- 📧 HTML email template (şu an plain text)
- 🧹 Expired token cleanup job (ek background task)
- 🛡️ Rate limiting (forgot-password endpoint için)
- 🤖 CAPTCHA entegrasyonu (bot koruması)
- 📱 iOS/Android PWA installability test

---

### ✅ QA Kontrol Listesi

**Backend:**
- [x] PasswordReset model migration
- [x] API endpoint'leri (forgot + reset) kayıtlı
- [x] SMTP Gmail bağlantısı test edildi
- [x] Email gönderimi başarılı
- [x] Token doğrulaması çalışıyor
- [x] Exception handling yapılmış
- [x] Detaylı logging aktif
- [x] test_smtp.py başarılı
- [x] test_forgot_endpoint.py başarılı

**Frontend:**
- [x] forgot_password.html form yapısı doğru
- [x] reset_password.html form yapısı doğru
- [x] Form submission POST ile API'yi çağırıyor
- [x] Mobile menu slide-out çalışıyor
- [x] Service worker kayıtlı
- [x] PWA manifest valid
- [x] Responsive CSS aktif

**Güvenlik:**
- [x] Token'lar secrets.token_urlsafe ile üretiliyor
- [x] Token'lar DB'de unique ve indexed
- [x] Single-use token pattern uygulanmış
- [x] Şifreler hash'lenmiş
- [x] .env dosyasında secret'lar (tırnak kontrollü)
- [x] User varlığını ifşa etmeyen mesajlar
- [x] STARTTLS ile şifreli SMTP

---

### 📝 Notlar & En İyi Uygulamalar

1. **Email Test:** Flask sunucusu restart edilmeli ve browser'da manuel test yapılmalı
2. **.env Güvenliği:** Tırnak ve boşluk dikkatli kontrol edilmeli
3. **Gmail 2FA:** App Password mutlaka kullanılmalı
4. **Token Expiration:** RESET_TOKEN_EXPIRATION env var ile ayarlanabilir
5. **Service Worker:** Hard refresh (Ctrl+Shift+R) gerekebilir
6. **Mobile Test:** DevTools device mode kullanılabilir
7. **Rate Limiting:** Gelecekte forgot-password endpoint için eklenmelidir
8. **HTML Emails:** Plain text yerine styled HTML template yapılabilir
- Bu proje için Copilot/AI araçları aşağı amaçlar için kullanılabilir:
  - Tekrarlayan kod şablonları (ör. CRUD boilerplate) üretimi ve önerileri
  - Birim testleri için örnek test gövdeleri oluşturma
  - Belgelendirme taslakları veya README iyileştirmeleri
  - Karmaşık ama tekrarlı mantık için öneri ve açıklama (developer yardımcısı)

- Aşağı durumlar için Copilot çıktıları SADECE referans olarak kullanılmalı (doğrudan commit edilmeyecek):
  - Tasarım kararları (mimari değişiklikler)
  - Güvenlik kritik kod (auth, crypto, SQL sorgu inşa, input validation)
  - Gizli veya hassas bilgi (API anahtarları, parolalar) içerebilecek öneriler

## 2) Güvenlik & gizlilik
- AI tarafından üretildiği öne sürülen kodlar insan tarafından gözden geçirilmeli ve testsiz commit edilmemelidir.
- Hiçbir durumda Copilot çıktısı doğrudan secrets (anahtarlar, şifreler, kişisel veriler) içermemelidir. Eğer öneri içinde böyle içerik görülürse, derhal silinmeli ve güvenli alternatif (örn. env değişkeni kullanım) tercih edilmelidir.
- Test veya demo amaçlı gizli değer kullanılması gerekiyorsa, bunun yerine proje içindeki `.env.example` veya fixtures/test-data içine dummy değer konulmalı — gerçek secret'lar repo veya testler içine asla konmamalıdır.

## 3) Lisans & telif
- Copilot tarafından üretilen kod parçalarının lisans durumu, üretici araç tarafından geldikleri verilerin kaynağına dayanabilir. Bu yüzden:
  - Üretilen koda ait orijin ve lisans açısından emin olunamadığında (özellikle büyük, benzersiz snippetler) doğrudan eklemeyin.
  - Üretilen uzun veya benzersiz kod blokları varsa, kodu basitleştirin veya yeniden yazın; gerektiğinde kaynakça/attribution ekleyin.

## 4) Kod kalitesi, test ve review gereksinimleri
- Copilot ile üretilen her yeni işlev veya değişiklik için:
  - Sorumlu geliştirici manuel code review yapmalı.
  - Gerekli birim/entegrasyon testleri eklenmeli veya var olanlar güncellenmeli.
  - Yeni kod için `pytest` testleri çalıştırılmalı ve CI (varsa) üzerinde başarılı olmalı.
- Kod stili (PEP8/formatting) otomatik araçlarla düzeltilmeli; büyük biçim değişiklikleri ayrı commit olarak yapılmalıdır.

## 5) Pull Request ve PR checklist
- PR açarken aşağıdaki maddeler Copilot-üretimli katkılar için zorunludur:
  - "Bu PR Copilot veya benzeri bir AI yardımcıyla üretilen kod içeriyor" şeklinde kısa bir açıklama.
  - Hangi kısımların otomatik üretildiği ve nelerin elle düzeltildiğinin kısa özeti.
  - Eklenen/aydınlatılan testlerin çalıştığını gösteren CI başarısı (veya `pytest` çıktısı yerel olarak).

## 6) Güvenli örnek kullanım pratikleri
- Örnek: bir fonksiyon şablonu Copilot ile üretildiyse:
  - Fonksiyonun giriş/çıkış davranışı, hata koşulları, sınır durumları el ile doğrulanmalı.
  - SQL sorguları veya dış kaynak çağrıları için parametre bağlama, input doğrulama ve timeout kontrolü eklenmeli.

## 7) İstisnalar ve acil durumlar
- Kritik güvenlik fix'leri: eğer bir güvenlik açığı hızlıca kapatılması gerekiyorsa ve Copilot bir patche yardımcı olduysa, yine de ilgili uzman tarafından review edilip test edilmeli. Eğer zaman kısıtlıysa, PR açıklamasına bu durum net yazılmalıdır.

## 8) Araç & yapılandırma tavsiyeleri
- Editor/IDE tarafında Copilot veya AI-assistant özelliği kullananlar için öneriler:
  - `Copilot` veya benzeri eklentileri açmadan önce `git status` kontrol edin; büyük, otomatik eklemeleri commit etmeden önce gözden geçirin.
  - Otomatik completions için güvenli bir `.editorconfig` / linter kombinasyonu kullanın.

## 9) Sıkça sorulan kısa kurallar (hızlı rehber)
- Commit etmeye hazır ol: AI çıktılarını *inceleyin* => *düzeltin* => *test edin* => *commit edin*.
- Gizli bilgiyi commit etmeyin. Düşük güvenliğe sahip önerileri iptal edin.
- Lisans konusunda şüphe varsa, parçayı yeniden yazın veya maintainerlara danışın.

---

Eğer isterseniz, bu kuralları `README.md` içinde kısa bir başlıkla işaretleyebilirim (katkıda bulunanlar için görünür link). Daha sonra CI konfigürasyonuna (örn. bir `pre-commit` hook ile) basit bir uyarı mekanizması eklemek de faydalı olacaktır.

Teşekkürler — bu rehberi repo seviyesinde tutarlı şekilde uygulamak proje güvenliği ve kalitesi için yardımcı olacaktır.

---

## Proje mimarisi, veritabanı ve kullanılan ana fonksiyonlar (özet)

Aşağıda repository içindeki "neden" ve "nerede" sorularına pratik, kısa ve geliştirici-odaklı cevaplar yer alır — bu kısım dokümantasyon amaçlıdır ve `backend/` içindeki dosyalara referans verir.

### 1) Genel yapı
- `app.py` — uygulamanın giriş noktası; frontend yüzü (`templates/`) ile `backend` API istemcisini bağlar (`backend.init_app`).
- `backend/` — uygulamanın sunucu tarafı mantığı:
  - `api/__init__.py` — REST benzeri endpoint'lerin tamamı (feed, explore, content-detail, auth, ratings, reviews, library, lists, follow, reactions vb.). UI'nin veri kaynağı burada bulunur.
  - `clients.py` — dış kaynak (TMDb, Google Books, OpenLibrary) için küçük helper fonksiyonlar; arama ve detay çekme; ayrıca (development amaçlı) in-memory TTL cache ve basit per-provider rate limiter içerir.
  - `models/__init__.py` — SQLAlchemy modelleri; kullanıcılar, içerikler, rating, review, liste ve activity tabloları yer alır.
  - `fixtures.py` ve `data/sample_data.py` — başlangıç verisi ve test/demo için sabit içerikler.

### 2) Neden bu fonksiyonlar ve ne için kullanılıyor — clients (dış API) tarafı
Ana klient fonksiyonlar ve kullanım amaçları:

- `search_tmdb_movies(query, limit)`
  - Ne yapar: TMDb (The Movie Database) araması yapar, dönene sonuçları proje formatına (mapping) çevirir.
  - Neden var: Kullanıcılar keşfetirken DB'de olmayan film içeriklerini bulmak ve (opsiyonel) ingest etmek için kullanılır.
  - Önemli not: fonksiyon artık bir in-memory cache kullanır (anahtar: `tmdb:search:<query>:<limit>`) ve per-provider rate limiter (`tmdb`) ile quota korunur.

- `search_google_books(query, limit)`
  - Ne yapar: Google Books (varsa) kullanır; yoksa Open Library'e rağbet eder. Sonuçları uygulama standardına çevirir (`page_count`, `poster`, `title`, `year` vb.).
  - Neden var: Keşfet ve arama senaryolarında kitaplar için dış kaynak sağlayıcı.
  - Önemli not: Benzer şekilde cache (`google:search:<query>:<limit>`) ve rate limiter (`google`) kullanır.

- `get_tmdb_movie_details(external_id)`
  - Ne yapar: Belirtilen TMDb id'si için detay (runtime, poster, title, vb.) çeker, map'leyip döner ve cache'e kaydeder (`tmdb:detail:<external_id>`). Eğer rate limit aşılmışsa None dönebilir.
  - Neden: Content-detail sayfası DB'de olmayan `mov-...` external_id'ler için canlı detay sağlamak amacıyla.

- `get_book_details(external_id)`
  - Ne yapar: `book-<id>` için Google Books veya OpenLibrary üzerinden detay getirir; map'ler ve cache'e kaydeder.
  - Neden: Content-detail sayfası veya canlı kaynak gösterimleri için kitap detayının anlık alınması.

- `_cache_get` / `_cache_set` / `_rate_allow`
  - Ne yapar: küçük, process-local, TTL bazlı cache ve dakika-temelli sayaç ile rate limit uygular.
  - Neden: geliştirme ortamında API çağrı sayısını sınırlamak, test/speed stabilitesi sağlamak. (Not: production için Redis gibi merkezi bir cache tercih edilir.)

### 3) API katmanı — nerede ne yapılıyor (`backend/api/__init__.py`)
- `api/feed`: Kullanıcının takip ettiği kişiler veya genel aktiviteler. Kaynak: DB (Activity). Fallback sample data.
- `api/explore`: DB öncelikli arama; DB'de sonuç yoksa dış API'lar ile arama yapılır. External ingest opsiyoneldir (ENV: `INGEST_EXTERNAL_RESULTS`).
- `api/content/<id>`: DB'de varsa persisted detay döner; DB yoksa external_id pattern'lerine göre canlı detay çekilir (`get_tmdb_movie_details` / `get_book_details`) ve frontende tek-seferlik sonuç sağlanır.
- ratings, reviews, reactions, library, lists, follow endpoints: kullanıcı etkileşimleri ve ilişkisel veritabanı işlemleri (create/update/delete + activity kaydı işlemleri).

### 4) Veritabanı modeli ve ilişkiler (`backend/models/__init__.py`)
Ana tablolar:

- `User` (users) — temel kullanıcı kaydı, takip ilişkisi (`Follow`), avatar, profil bilgisi.
- `Follow` (follows) — many-to-many (self-referential) takip tablosu; (follower_id, followed_id) kompozit anahtar.
- `Content` (contents) — içerik kayıtları: `external_id`, `content_type` (movie/book), `title`, `runtime_minutes`, `page_count`, `cover_url`, `extra_metadata`.
- `LibraryItem` (library_items) — kullanıcı kütüphanelerine eklenen içerikler (`status`: watched/watchlist/read/reading_list).
- `Rating` (ratings) — user-content tekil puan (unique constraint user+content).
- `Review` (reviews) — user-content yorumları; zaman damgaları ve update takibi.
- `ReviewReaction` (review_reactions) — kullanıcıların review'ler üzerindeki like/dislike tepkileri.
- `Activity` (activities) — kullanıcı aktivitelerini özetleyen (rating, review, list_add, library_status) kayıtlar. Feed ekranı bu tablodan beslenir.

### 5) Neden böyle bir yapı? (kısa gerekçe)
- Ayrık komponentler (clients vs api vs models) kodun test edilebilirliğini ve ileride üretime taşımayı kolaylaştırır.
- DB merkezli model: kalıcı içerikler, kullanıcı etkinlikleri ve ilişkiler izlenebilir olur.
- Dış kaynaklar için cache & rate limiter (development) ile API maliyeti ve test kararlılığı sağlanır; gerçek üretime taşınırken Redis/Shared rate-limiter tavsiye edilir.

### 6) Test stratejisi
- `tests/` içinde birim + entegrasyon testleri yer alır: clients mapping, explore ingestion, content-detail live gibi kritik davranışlar doğrulanmıştır.
- `conftest.py` DB izolasyonu ve seed işlemleri sağlar — testler izole çalışır.

---

Eğer isterseniz, bu bölümden türetilmiş daha ayrıntılı bir `ARCHITECTURE.md` dosyası oluşturabilirim (örneğin ER diyagramı, sequence diagram, nerelerde cache kullanıldığı, ve CI adımları). Bir sonraki adımda bunu genişleteyim mi?
