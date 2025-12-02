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

### 5) Neden böyle bir yapı? (kısa gerekçe)
- Ayrık komponentler (clients vs api vs models) kodun test edilebilirliğini ve ileride üretime taşımayı kolaylaştırır.
- DB merkezli model: kalıcı içerikler, kullanıcı etkinlikleri ve ilişkiler izlenebilir olur.
- Dış kaynaklar için cache & rate limiter (development) ile API maliyeti ve test kararlılığı sağlanır; gerçek üretime taşınırken Redis/Shared rate-limiter tavsiye edilir.

### 6) Test stratejisi
- `tests/` içinde birim + entegrasyon testleri yer alır: clients mapping, explore ingestion, content-detail live gibi kritik davranışlar doğrulanmıştır.
- `conftest.py` DB izolasyonu ve seed işlemleri sağlar — testler izole çalışır.

---

Eğer isterseniz, bu bölümden türetilmiş daha ayrıntılı bir `ARCHITECTURE.md` dosyası oluşturabilirim (örneğin ER diyagramı, sequence diagram, nerelerde cache kullanıldığı, ve CI adımları). Bir sonraki adımda bunu genişleteyim mi?
