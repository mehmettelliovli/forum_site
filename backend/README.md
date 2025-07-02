# Flask Forum Backend

## Kurulum

1. Gerekli paketleri yükleyin:

```bash
pip install -r requirements.txt
```

2. Ortam değişkenlerini ayarlayın (isteğe bağlı):

- `DATABASE_URL` (PostgreSQL bağlantı stringi)
- `SECRET_KEY` (Flask için gizli anahtar)

3. Uygulamayı başlatın:

```bash
python app.py
```

## API Endpointleri

### Auth
- POST `/auth/signup` — Kayıt ol
- POST `/auth/login` — Giriş yap
- GET `/auth/logout` — Çıkış yap

### Kullanıcılar
- GET `/users/` — Tüm kullanıcıları listele

### Forum
- GET `/forum/posts` — Tüm konuları listele
- POST `/forum/posts` — Yeni konu oluştur (giriş gerekli)

## Notlar
- Tüm POST isteklerinde `Content-Type: application/json` header'ı olmalı.
- Kimlik doğrulama cookie (session) bazlıdır.
- Hatalar uygun HTTP kodları ile döner. 