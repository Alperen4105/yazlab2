# yazlab2 — mini sosyal kütüphane (development)

Bu repository üniversite/ders projesi olarak hazırlanmış bir Flask uygulaması içerir.

Önemli: Proje içinde Copilot/AI destekli üretim ve kullanım kuralları bulunmaktadır — lütfen takip etmeden önce okuyun:

- Repository-level Copilot kuralları: `.github/COPILOT_RULES.md`

Proje hakkında daha fazla bilgi ve geliştirme notları için `docs/` klasörüne bakabilirsiniz.

## Admin DB Özeti (opsiyonel)
- Endpoint: `/api/admin/db-summary`
- Koruma: Header `X-Admin-Key: <key>`; key env değişkeni `ADMIN_KEY` ile belirlenir.
- Örnek kullanım (PowerShell):

```
$env:ADMIN_KEY = "my-secret"
curl -H "X-Admin-Key: my-secret" http://127.0.0.1:5000/api/admin/db-summary
```

