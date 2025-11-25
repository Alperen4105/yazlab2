# Veritabanı Şeması ve Modeller

Backend katmanını kodlamadan önce kalıcı veri modeli üzerinde anlaşmak kritik. Aşağıdaki tablo/ilişkiler, PDF’deki gereksinimleri karşılayacak minimum yapıyı sunar. İsimler İngilizce tutuldu, ancak migration sırasında kolayca uyarlanabilir.

## 1. Kullanıcı ve İlişkileri

### `users`
| sütun | tip | not |
| --- | --- | --- |
| id | UUID / BIGINT | PK |
| username | varchar(50) | benzersiz |
| email | varchar(255) | benzersiz |
| password_hash | varchar(255) | bcrypt/argon saklanacak |
| display_name | varchar(100) | |
| avatar_url | text | |
| bio | text | |
| created_at | timestamptz | varsayılan now |

### `follows`
| sütun | tip | not |
| follower_id | FK users.id | PK (bileşik) |
| followed_id | FK users.id | PK (bileşik) |
| created_at | timestamptz | |

## 2. İçerik (Film/Kitap) Katmanı

### `contents`
Ortak alanları tek tabloda tutup `content_type` ile film/kitap ayrımı yapılır.

| sütun | tip | not |
| --- | --- | --- |
| id | UUID/BIGINT | PK |
| external_id | varchar | TMDb/OpenLibrary kimliği |
| content_type | enum('movie','book') | |
| title | varchar(255) | |
| synopsis | text | |
| release_year | smallint | |
| runtime_minutes / page_count | smallint | nullable |
| cover_url | text | |
| extra_metadata | jsonb | yönetmen, yazar, tür listeleri gibi ayrıntılar |
| created_at | timestamptz | |

İsteğe bağlı olarak `people` ve `content_people` ilişki tabloları kurulup yönetmen/yazar isimleri normalize edilebilir.

## 3. Kullanıcı Kütüphanesi

### `library_items`
Kullanıcının “izledim/izlenecek/okudum/okunacak” listelerini temsil eder.

| sütun | tip | not |
| --- | --- | --- |
| id | PK |
| user_id | FK users.id | |
| content_id | FK contents.id | |
| status | enum('watched','watchlist','read','reading_list') | |
| created_at | timestamptz | |

### `custom_lists`
| sütun | tip | not |
| id | PK |
| user_id | FK users.id | |
| title | varchar(120) | |
| description | text | nullable |
| visibility | enum('public','private','followers') | |
| created_at | timestamptz | |

### `custom_list_items`
| sütun | tip | not |
| id | PK |
| list_id | FK custom_lists.id | |
| content_id | FK contents.id | |
| order_index | int | drag-drop için |

## 4. Puanlama ve Yorumlar

### `ratings`
| sütun | tip | not |
| id | PK |
| user_id | FK users.id | unique bersama content |
| content_id | FK contents.id | |
| score | smallint | 1-10 |
| created_at | timestamptz | |

### `reviews`
| sütun | tip | not |
| id | PK |
| user_id | FK users.id | |
| content_id | FK contents.id | |
| body | text | |
| created_at | timestamptz | |
| updated_at | timestamptz | nullable |

### `review_reactions`
| sütun | tip | not |
| id | PK |
| review_id | FK reviews.id | |
| user_id | FK users.id | |
| reaction_type | enum('like','dislike') | |

## 5. Aktivite Akışı

### `activities`
Bu tablo, feed’de gördüğümüz “kullanıcı X şunu yaptı” kayıtlarını depolar.

| sütun | tip | not |
| id | PK |
| user_id | FK users.id | |
| activity_type | enum('rating','review','list_add','library_status') | |
| related_id | uuid | ratings/reviews/custom_list_items kayıtlarına FK |
| extra_metadata | jsonb | kartta gösterilecek ek bilgiler |
| created_at | timestamptz | |

Aktivite üretimi, ilgili modellerde `after_insert` hook’ları veya servis katmanı aracılığıyla gerçekleştirilebilir.

## 6. ER Diyagramı Özeti

- `users` 1—N `ratings`, `reviews`, `library_items`, `custom_lists`, `activities`
- `contents` 1—N `ratings`, `reviews`, `library_items`, `custom_list_items`
- `custom_lists` 1—N `custom_list_items`
- `users` — `follows` — `users`

## 7. Model Sınıfları (SQLAlchemy)

Başlangıç için aşağıdaki modeller tanımlanacak:

- `User`, `Follow`
- `Content`
- `LibraryItem`
- `CustomList`, `CustomListItem`
- `Rating`, `Review`, `ReviewReaction`
- `Activity`

Bu şema üzerine Alembic migration oluşturduktan sonra üçüncü adıma (çekirdek API endpoint’lerini yazma) geçebiliriz.

