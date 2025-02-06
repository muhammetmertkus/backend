# Yüz Tanıma ile Yoklama Sistemi

Bu proje, eğitim kurumlarında yoklama sürecini otomatikleştirmek için yüz tanıma teknolojisi kullanan bir sistemdir.

## Özellikler

- Otomatik yüz tanıma ile yoklama
- Gerçek zamanlı duygu analizi
- Çoklu yüz tespiti ve tanıma
- Katılım istatistikleri ve raporlama
- Email bildirimleri
- Devamsızlık takibi
- Ders bazlı analitikler

## Teknolojiler

- Python 3.8+
- FastAPI
- SQLite
- face_recognition
- deepface
- OpenCV
- SQLAlchemy
- Alembic
- Pytest

## Hızlı Başlangıç

1. Gereksinimleri yükleyin:
```bash
pip install -r requirements.txt
```

2. Çevre değişkenlerini ayarlayın:
```bash
cp .env.example .env
# .env dosyasını düzenleyin
```

3. Veritabanını oluşturun:
```bash
alembic upgrade head
```

4. Uygulamayı çalıştırın:
```bash
python run.py
```

5. API dokümantasyonuna erişin:
```
http://localhost:8000/api/v1/docs
```

## Geliştirme

### Test

```bash
pytest
```

### Lint

```bash
flake8 .
```

### Migrasyon

```bash
# Yeni migrasyon oluştur
alembic revision --autogenerate -m "migration_adi"

# Migrasyonları uygula
alembic upgrade head
```

## API Endpoints

### Kimlik Doğrulama
- POST /api/v1/auth/login
- POST /api/v1/auth/register

### Öğrenciler
- GET /api/v1/students
- POST /api/v1/students
- GET /api/v1/students/{id}
- PUT /api/v1/students/{id}
- POST /api/v1/students/{id}/face

### Yoklama
- POST /api/v1/attendance/face
- POST /api/v1/attendance/manual
- GET /api/v1/attendance/{id}
- GET /api/v1/attendance/course/{course_id}

### Raporlar
- GET /api/v1/reports/attendance/daily
- GET /api/v1/reports/emotions/course/{course_id}
- GET /api/v1/reports/attendance/student/{student_id}

## Deployment

Detaylı deployment talimatları için [DEPLOYMENT.md](DEPLOYMENT.md) dosyasına bakın.

## Katkıda Bulunma

1. Bu repository'yi fork edin
2. Feature branch'i oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'feat: amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır - detaylar için [LICENSE](LICENSE) dosyasına bakın.

## İletişim

- Proje Yöneticisi - [@username](https://github.com/username)
- Proje Linki: [https://github.com/username/yoklama-sistemi](https://github.com/username/yoklama-sistemi) 