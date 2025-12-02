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
