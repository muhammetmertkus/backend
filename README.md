# Yüz Tanıma ile Yoklama Sistemi

Bu proje, üniversite ve okullarda yüz tanıma teknolojisi kullanarak yoklama sistemini otomatikleştiren bir API uygulamasıdır.

## Özellikler

- Yüz tanıma ile otomatik yoklama
- Çoklu sınıf ve ders desteği
- Öğrenci, öğretmen ve yönetici rolleri
- JWT tabanlı kimlik doğrulama
- RESTful API yapısı
- Detaylı raporlama ve istatistikler

## Kurulum

### Geliştirme Ortamı

1. Depoyu klonlayın:
```bash
git clone https://github.com/muhammetmertkus/backend.git
cd backend
```

2. Sanal ortam oluşturun ve aktifleştirin:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

4. `.env` dosyasını oluşturun:
```bash
cp .env.example .env
# Gerekli bilgileri düzenleyin
```

5. Veritabanını oluşturun:
```bash
flask db upgrade
```

6. Uygulamayı çalıştırın:
```bash
python run.py
```

### Heroku'ya Deployment

1. Heroku CLI'yi yükleyin ve giriş yapın:
```bash
heroku login
```

2. Heroku uygulaması oluşturun:
```bash
heroku create yoklama-sistemi
```

3. PostgreSQL veritabanı ekleyin:
```bash
heroku addons:create heroku-postgresql:hobby-dev
```

4. Gerekli çevre değişkenlerini ayarlayın:
```bash
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secret-key
heroku config:set JWT_SECRET_KEY=your-jwt-secret-key
```

5. Uygulamayı deploy edin:
```bash
git push heroku master
```

6. Veritabanı migrasyonlarını çalıştırın:
```bash
heroku run flask db upgrade
```

## API Dokümantasyonu

API endpointlerinin tam listesi için `/api/docs` adresini ziyaret edin.

### Temel Endpointler

- `POST /api/auth/login`: Kullanıcı girişi
- `POST /api/auth/register`: Yeni kullanıcı kaydı
- `GET /api/courses`: Derslerin listesi
- `POST /api/attendance/record`: Yoklama kaydetme
- `GET /api/reports/course/{course_id}`: Derse ait yoklama raporu

## Katkıda Bulunma

1. Bu depoyu fork edin
2. Yeni bir özellik dalı oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Harika bir özellik ekle'`)
4. Dalınıza push edin (`git push origin feature/amazing-feature`)
5. Pull request açın

## Lisans

Bu proje MIT Lisansı ile lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## İletişim

Muhammet Mert Kuş - muhammetmertkus@gmail.com 