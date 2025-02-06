# Yüz Tanıma ile Yoklama Sistemi Deployment Kılavuzu

## Sistem Gereksinimleri

- Python 3.8+
- SQLite3
- pip (Python paket yöneticisi)
- virtualenv (Sanal ortam yöneticisi)

## Kurulum Adımları

### 1. Python Sanal Ortamı Oluşturma

```bash
# Sanal ortam oluştur
python -m venv venv

# Sanal ortamı aktifleştir
# Windows için:
venv\Scripts\activate
# Linux/Mac için:
source venv/bin/activate
```

### 2. Bağımlılıkları Yükleme

```bash
# Gerekli paketleri yükle
pip install -r requirements.txt
```

### 3. Çevre Değişkenlerini Ayarlama

```bash
# .env.example dosyasını .env olarak kopyala
cp .env.example .env

# .env dosyasını düzenle ve gerekli değişkenleri ayarla
# Özellikle şu değişkenleri ayarlamayı unutmayın:
# - SECRET_KEY
# - JWT_SECRET_KEY
# - SMTP_* değişkenleri (email bildirimleri için)
```

### 4. Veritabanı Oluşturma

```bash
# Veritabanı migrasyonlarını çalıştır
alembic upgrade head
```

### 5. Uygulama Klasör Yapısını Hazırlama

```bash
# Gerekli klasörleri oluştur
mkdir -p logs uploads/faces uploads/attendance
```

### 6. Uygulamayı Test Etme

```bash
# Test veritabanını oluştur ve testleri çalıştır
pytest
```

### 7. Uygulamayı Çalıştırma

#### Development Ortamı

```bash
# Debug modunda çalıştır
python run.py
```

#### Production Ortamı

1. Systemd Service Dosyası Oluşturma:

```ini
# /etc/systemd/system/yoklama.service
[Unit]
Description=Yoklama Sistemi
After=network.target

[Service]
User=yoklama
WorkingDirectory=/opt/yoklama
Environment="PATH=/opt/yoklama/venv/bin"
ExecStart=/opt/yoklama/venv/bin/python run.py
Restart=always

[Install]
WantedBy=multi-user.target
```

2. Servisi Başlatma:

```bash
# Servisi etkinleştir ve başlat
sudo systemctl enable yoklama
sudo systemctl start yoklama
```

### 8. Nginx ile Reverse Proxy (Opsiyonel)

```nginx
# /etc/nginx/sites-available/yoklama
server {
    listen 80;
    server_name yoklama.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /opt/yoklama/static;
    }

    location /uploads {
        alias /opt/yoklama/uploads;
    }
}
```

### 9. Log Rotasyonu Ayarlama

```bash
# /etc/logrotate.d/yoklama
/opt/yoklama/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 yoklama yoklama
    sharedscripts
    postrotate
        systemctl reload yoklama
    endscript
}
```

## Güvenlik Önlemleri

1. Uygulama Kullanıcısı Oluşturma:
```bash
# Dedicated sistem kullanıcısı oluştur
sudo useradd -r -s /bin/false yoklama
```

2. Dosya İzinlerini Ayarlama:
```bash
# Dosya sahipliğini ve izinleri ayarla
sudo chown -R yoklama:yoklama /opt/yoklama
sudo chmod -R 750 /opt/yoklama
sudo chmod -R 760 /opt/yoklama/logs
sudo chmod -R 760 /opt/yoklama/uploads
```

3. Firewall Ayarları:
```bash
# Sadece gerekli portları aç
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

## Bakım ve İzleme

### Log Dosyaları
- Uygulama logları: `/opt/yoklama/logs/app.log`
- Hata logları: `/opt/yoklama/logs/error.log`
- Access logları: `/opt/yoklama/logs/access.log`

### Veritabanı Yedekleme
```bash
# Günlük yedek alma
sqlite3 yoklama.db ".backup '/opt/yoklama/backups/yoklama_$(date +%Y%m%d).db'"
```

### Performans İzleme
```bash
# CPU ve memory kullanımını izle
top -p $(pgrep -f "python run.py")

# Disk kullanımını kontrol et
du -sh /opt/yoklama/*
```

## Sorun Giderme

### Yaygın Hatalar ve Çözümleri

1. Uygulama Başlatma Hataları
```bash
# Log dosyalarını kontrol et
tail -f /opt/yoklama/logs/error.log

# Servis durumunu kontrol et
systemctl status yoklama
```

2. Veritabanı Hataları
```bash
# Veritabanı bütünlüğünü kontrol et
sqlite3 yoklama.db "PRAGMA integrity_check;"
```

3. Dosya İzin Hataları
```bash
# İzinleri yeniden ayarla
sudo chown -R yoklama:yoklama /opt/yoklama
sudo chmod -R 750 /opt/yoklama
```

## Güncelleme Prosedürü

1. Uygulamayı Durdur:
```bash
sudo systemctl stop yoklama
```

2. Yedek Al:
```bash
# Kod ve veritabanı yedeği
cp -r /opt/yoklama /opt/yoklama_backup_$(date +%Y%m%d)
sqlite3 yoklama.db ".backup '/opt/yoklama/backups/yoklama_$(date +%Y%m%d).db'"
```

3. Kodu Güncelle:
```bash
git pull origin main
pip install -r requirements.txt
alembic upgrade head
```

4. Uygulamayı Başlat:
```bash
sudo systemctl start yoklama
```

## İletişim ve Destek

- Teknik destek: support@example.com
- Hata bildirimi: issues@example.com
- Dokümantasyon: docs.example.com 