# Yüz Tanıma ile Yoklama Sistemi Backend PRD

## 1. Proje Amacı ve Genel Bakış

### 1.1 Amaç
Bu sistem, eğitim kurumlarında yoklama sürecini otomatikleştirmek, öğrenci katılımını analiz etmek ve eğitim kalitesini artırmak için tasarlanmıştır. Yüz tanıma teknolojisi ve duygu analizi kullanarak, öğrenci katılımını ve derse olan ilgisini ölçer.

### 1.2 Temel Özellikler
- Otomatik yüz tanıma ile yoklama
- Gerçek zamanlı duygu analizi
- Çoklu yüz tespiti ve tanıma
- Katılım istatistikleri ve raporlama
- Email bildirimleri
- Devamsızlık takibi
- Ders bazlı analitikler

### 1.3 Kullanıcı Tipleri
- Öğretmenler
- Öğrenciler
- Yöneticiler
- Sistem admini

## 2. Teknoloji Yığını

### 2.1 Ana Teknolojiler
- **Flask**: Web framework
- **SQLite**: Veritabanı
- **Redis**: Önbellek (opsiyonel)
- **Gunicorn**: WSGI HTTP Sunucusu
- **Nginx**: Reverse Proxy (production)

### 2.2 Yapay Zeka ve Görüntü İşleme
- **face_recognition**: Yüz tespiti ve tanıma
- **deepface**: Duygu analizi ve yüz doğrulama
- **OpenCV**: Görüntü ön işleme
- **NumPy**: Matematiksel işlemler
- **TensorFlow Lite**: Hafif ML modelleri (opsiyonel)

### 2.3 Yardımcı Kütüphaneler
- **SQLAlchemy**: ORM
- **Pillow**: Görüntü işleme
- **pandas**: Veri analizi
- **matplotlib**: Grafik oluşturma
- **python-jose**: JWT işlemleri
- **passlib**: Şifre hashleme
- **python-dotenv**: Çevre değişkenleri
- **APScheduler**: Zamanlanmış görevler
- **Flask-Mail**: Email gönderimi

## 3. Sistem Mimarisi

### 3.1 Katmanlı Mimari
```
app/
├── api/           # API endpoints
├── core/          # Çekirdek fonksiyonlar
├── models/        # Veritabanı modelleri
├── services/      # İş mantığı servisleri
├── schemas/       # Veri şemaları
├── utils/         # Yardımcı fonksiyonlar
└── workers/       # Arkaplan işleri
```

### 3.2 Servis Mimarisi
```python
services/
├── auth_service.py        # Kimlik doğrulama
├── face_service.py        # Yüz işleme
├── emotion_service.py     # Duygu analizi
├── attendance_service.py  # Yoklama işlemleri
├── report_service.py      # Raporlama
├── email_service.py       # Email işlemleri
└── storage_service.py     # Dosya depolama
```

## 4. Veritabanı Yapısı

### 4.1 Ana Tablolar
```sql
-- Kullanıcılar
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    name TEXT NOT NULL,
    surname TEXT NOT NULL,
    role TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Öğrenciler
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    student_number TEXT UNIQUE,
    department TEXT,
    face_encodings TEXT,
    face_photo_url TEXT,
    preferences JSON,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Öğretmenler
CREATE TABLE teachers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    department TEXT,
    title TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Dersler
CREATE TABLE courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    teacher_id INTEGER,
    semester TEXT,
    schedule JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES teachers (id)
);

-- Yoklamalar
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    type TEXT CHECK(type IN ('auto', 'manual', 'face')),
    photo_url TEXT,
    metadata JSON,
    created_by INTEGER,
    FOREIGN KEY (course_id) REFERENCES courses (id),
    FOREIGN KEY (created_by) REFERENCES users (id)
);

-- Yoklama Detayları
CREATE TABLE attendance_details (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    attendance_id INTEGER,
    student_id INTEGER,
    status BOOLEAN DEFAULT FALSE,
    emotion_data JSON,
    confidence FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (attendance_id) REFERENCES attendance (id),
    FOREIGN KEY (student_id) REFERENCES students (id)
);

-- Duygu Analizi Geçmişi
CREATE TABLE emotion_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    course_id INTEGER,
    emotion TEXT,
    confidence FLOAT,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students (id),
    FOREIGN KEY (course_id) REFERENCES courses (id)
);
```

### 4.2 İndeksler
```sql
CREATE INDEX idx_attendance_course_date ON attendance(course_id, date);
CREATE INDEX idx_attendance_details_student ON attendance_details(student_id);
CREATE INDEX idx_emotion_history_student ON emotion_history(student_id);
```

## 5. API Endpoints

### 5.1 Kimlik Doğrulama
```python
POST /api/auth/login
POST /api/auth/logout
POST /api/auth/refresh
GET /api/auth/me
POST /api/auth/password/reset
POST /api/auth/password/change
```

### 5.2 Öğrenci İşlemleri
```python
GET /api/students
POST /api/students
GET /api/students/{id}
PUT /api/students/{id}
DELETE /api/students/{id}
POST /api/students/{id}/face
GET /api/students/{id}/attendance
GET /api/students/{id}/emotions
GET /api/students/{id}/courses
```

### 5.3 Yoklama İşlemleri
```python
POST /api/attendance/face
POST /api/attendance/manual
GET /api/attendance/{id}
PUT /api/attendance/{id}
GET /api/attendance/course/{course_id}
GET /api/attendance/student/{student_id}
GET /api/attendance/stats
```

### 5.4 Rapor İşlemleri
```python
GET /api/reports/attendance/daily
GET /api/reports/attendance/weekly
GET /api/reports/attendance/monthly
GET /api/reports/emotions/course/{course_id}
GET /api/reports/emotions/student/{student_id}
GET /api/reports/export/excel
GET /api/reports/export/pdf
```

## 6. Yüz Tanıma ve Duygu Analizi

### 6.1 Yüz Tanıma Süreci
```python
class FaceRecognitionService:
    def detect_faces(self, image):
        # Görüntüdeki yüzleri tespit et
        faces = face_recognition.face_locations(image)
        encodings = face_recognition.face_encodings(image, faces)
        return faces, encodings

    def compare_faces(self, known_encoding, unknown_encoding):
        # Yüz karşılaştırma
        distance = face_recognition.face_distance([known_encoding], unknown_encoding)
        return distance[0] <= 0.6  # Eşleşme eşiği

    def process_attendance(self, image, course_id):
        # Yoklama işlemi
        faces, encodings = self.detect_faces(image)
        results = []
        
        for encoding in encodings:
            student = self.find_matching_student(encoding)
            if student:
                emotion = self.analyze_emotion(image)
                results.append({
                    'student': student,
                    'emotion': emotion
                })
        
        return results
```

### 6.2 Duygu Analizi
```python
class EmotionAnalysisService:
    def analyze_emotion(self, face_image):
        # Duygu analizi yap
        analysis = DeepFace.analyze(
            face_image,
            actions=['emotion'],
            enforce_detection=False
        )
        
        return {
            'dominant_emotion': analysis['dominant_emotion'],
            'emotions': analysis['emotion'],
            'confidence': max(analysis['emotion'].values())
        }

    def track_emotion_history(self, student_id, course_id, emotion_data):
        # Duygu geçmişini kaydet
        emotion_history = EmotionHistory(
            student_id=student_id,
            course_id=course_id,
            emotion=emotion_data['dominant_emotion'],
            confidence=emotion_data['confidence']
        )
        db.session.add(emotion_history)
        db.session.commit()
```

## 7. Arkaplan Görevleri

### 7.1 Zamanlanmış Görevler
```python
def configure_scheduler(app):
    scheduler = APScheduler()
    scheduler.init_app(app)
    
    # Günlük devamsızlık raporu
    @scheduler.task('cron', id='daily_attendance_report', hour=18)
    def send_daily_attendance_report():
        report_service.generate_daily_reports()
        
    # Haftalık analiz
    @scheduler.task('cron', id='weekly_analysis', day_of_week='sun')
    def analyze_weekly_data():
        analytics_service.generate_weekly_analysis()
        
    scheduler.start()
```

### 7.2 Email Bildirimleri
```python
class EmailService:
    def send_attendance_notification(self, student, course, status):
        template = self.get_template('attendance_notification')
        content = template.render(
            student_name=student.name,
            course_name=course.name,
            status=status,
            date=datetime.now()
        )
        
        self.send_email(
            to=student.email,
            subject=f"Yoklama Bildirimi - {course.name}",
            content=content
        )

    def send_weekly_report(self, teacher, course):
        report = report_service.generate_weekly_report(course.id)
        template = self.get_template('weekly_report')
        content = template.render(report=report)
        
        self.send_email(
            to=teacher.email,
            subject=f"Haftalık Yoklama Raporu - {course.name}",
            content=content
        )
```

## 8. Güvenlik Önlemleri

### 8.1 Kimlik Doğrulama
```python
def authenticate_user(email, password):
    user = User.query.filter_by(email=email).first()
    if not user or not verify_password(password, user.password_hash):
        raise AuthenticationError()
        
    return create_access_token(user)

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('sub')
        return User.query.get(user_id)
    except JWTError:
        raise InvalidTokenError()
```

### 8.2 Yetkilendirme
```python
def require_roles(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.role in roles:
                raise UnauthorizedError()
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

## 9. Hata Yönetimi

### 9.1 Özel Hatalar
```python
class AppError(Exception):
    def __init__(self, message, code=400):
        self.message = message
        self.code = code

class AuthenticationError(AppError):
    def __init__(self):
        super().__init__('Kimlik doğrulama hatası', 401)

class ResourceNotFoundError(AppError):
    def __init__(self, resource):
        super().__init__(f'{resource} bulunamadı', 404)
```

### 9.2 Hata İşleme
```python
@app.errorhandler(AppError)
def handle_app_error(error):
    return jsonify({
        'error': error.message,
        'code': error.code
    }), error.code

@app.errorhandler(500)
def handle_server_error(error):
    # Log error
    logger.error(f'Server Error: {str(error)}')
    return jsonify({
        'error': 'Internal server error',
        'code': 500
    }), 500
```

## 10. Performans Optimizasyonları

### 10.1 Önbellek Stratejisi
```python
class CacheService:
    def __init__(self):
        self.redis = Redis()
        self.default_ttl = 3600  # 1 saat
        
    def get_or_set(self, key, callback, ttl=None):
        value = self.redis.get(key)
        if value:
            return json.loads(value)
            
        value = callback()
        self.redis.setex(
            key,
            ttl or self.default_ttl,
            json.dumps(value)
        )
        return value
```

### 10.2 Görüntü Optimizasyonu
```python
def optimize_image(image, max_size=(800, 800)):
    # Görüntü boyutunu küçült
    img = Image.open(image)
    img.thumbnail(max_size, Image.LANCZOS)
    
    # JPEG kalitesini düşür
    output = BytesIO()
    img.save(output, format='JPEG', quality=85)
    return output.getvalue()
```

## 11. Raporlama ve Analitikler

### 11.1 Yoklama Analizi
```python
def analyze_attendance(course_id, start_date, end_date):
    # Katılım oranları
    attendance_rates = db.session.query(
        Student.id,
        func.count(AttendanceDetail.id).label('total_attendance'),
        func.sum(case([(AttendanceDetail.status == True, 1)], else_=0)).label('present_count')
    ).join(AttendanceDetail).filter(
        AttendanceDetail.course_id == course_id,
        AttendanceDetail.date.between(start_date, end_date)
    ).group_by(Student.id).all()
    
    return {
        'total_classes': get_total_classes(course_id, start_date, end_date),
        'attendance_rates': attendance_rates,
        'average_attendance': calculate_average_attendance(attendance_rates)
    }
```

### 11.2 Duygu Analizi Raporları
```python
def analyze_emotions(course_id, date):
    emotions = db.session.query(
        EmotionHistory.emotion,
        func.count(EmotionHistory.id).label('count')
    ).filter(
        EmotionHistory.course_id == course_id,
        EmotionHistory.date >= date
    ).group_by(EmotionHistory.emotion).all()
    
    return {
        'emotions': emotions,
        'dominant_emotion': max(emotions, key=lambda x: x.count),
        'total_records': sum(e.count for e in emotions)
    }
```

## 12. Deployment ve DevOps

### 12.1 Python Yapılandırması
```bash
# Gerekli Python paketleri
pip install -r requirements.txt

# requirements.txt içeriği
flask==2.0.1
face-recognition==1.3.0
deepface==0.0.75
opencv-python==4.5.3.56
numpy==1.21.2
tensorflow-lite==2.5.0
sqlalchemy==1.4.23
pillow==8.3.2
pandas==1.3.3
matplotlib==3.4.3
python-jose==3.3.0
passlib==1.7.4
python-dotenv==0.19.0
apscheduler==3.8.1
flask-mail==0.9.1
gunicorn==20.1.0
```

### 12.2 Uygulama Başlatma
```python
# run.py
from app import create_app
from waitress import serve

app = create_app()

if __name__ == '__main__':
    if app.config['ENV'] == 'production':
        # Production'da Waitress WSGI sunucusu
        serve(app, host='0.0.0.0', port=8000)
    else:
        # Development'da Flask development sunucusu
        app.run(debug=True)
```

### 12.3 Production Yapılandırması
```python
# config.py
class ProductionConfig:
    DEBUG = False
    TESTING = False
    DATABASE_URL = 'sqlite:///./production.db'
    SECRET_KEY = 'your-secret-key'
    UPLOAD_FOLDER = '/app/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max-limit
    
    # Email ayarları
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'your-email@gmail.com'
    MAIL_PASSWORD = 'your-app-password'
    
    # Güvenlik ayarları
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
```

### 12.4 Servis Yapılandırması
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

### 12.5 Deployment Kontrol Listesi
1. Sistem Hazırlığı
   ```bash
   # Gerekli sistem paketlerini yükle
   sudo apt-get update
   sudo apt-get install python3-pip python3-venv

   # Uygulama dizinini oluştur
   sudo mkdir /opt/yoklama
   sudo chown -R $USER:$USER /opt/yoklama
   ```

2. Python Ortamı
   ```bash
   # Virtual environment oluştur
   python3 -m venv /opt/yoklama/venv
   source /opt/yoklama/venv/bin/activate

   # Bağımlılıkları yükle
   pip install -r requirements.txt
   ```

3. Uygulama Yapılandırması
   ```bash
   # Yapılandırma dosyasını oluştur
   cp config.example.py config.py
   nano config.py  # Gerekli ayarları düzenle

   # Veritabanını oluştur
   flask db upgrade
   ```

4. Servis Başlatma
   ```bash
   # Servis dosyasını kopyala
   sudo cp yoklama.service /etc/systemd/system/

   # Servisi etkinleştir ve başlat
   sudo systemctl enable yoklama
   sudo systemctl start yoklama
   ```

5. Log Yapılandırması
   ```python
   # logging_config.py
   LOGGING = {
       'version': 1,
       'disable_existing_loggers': False,
       'formatters': {
           'standard': {
               'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
           },
       },
       'handlers': {
           'file': {
               'class': 'logging.handlers.RotatingFileHandler',
               'filename': '/var/log/yoklama/app.log',
               'maxBytes': 10485760,  # 10MB
               'backupCount': 10,
               'formatter': 'standard',
           },
       },
       'root': {
           'handlers': ['file'],
           'level': 'INFO',
       },
   }
   ```

## 13. Test Stratejisi

### 13.1 Birim Testler
```python
def test_face_recognition():
    service = FaceRecognitionService()
    
    # Test görüntüsü yükle
    image = load_test_image('test_face.jpg')
    
    # Yüz tespiti test et
    faces, encodings = service.detect_faces(image)
    assert len(faces) > 0
    assert len(encodings) == len(faces)
    
    # Yüz karşılaştırma test et
    known_encoding = load_known_encoding()
    match = service.compare_faces(known_encoding, encodings[0])
    assert match is True
```

### 13.2 Entegrasyon Testleri
```python
def test_attendance_workflow():
    # Test verilerini hazırla
    course = create_test_course()
    students = create_test_students(3)
    
    # Yoklama al
    image = load_test_image('class_photo.jpg')
    response = client.post(f'/api/attendance/face', data={
        'course_id': course.id,
        'photo': image
    })
    
    assert response.status_code == 200
    assert len(response.json['present_students']) == 3
```

## 14. Gereksinimler ve Kurulum

### 14.1 Sistem Gereksinimleri
- Python 3.8+
- 4GB RAM (minimum)
- 10GB disk alanı
- Kamera erişimi
- İnternet bağlantısı

### 14.2 Kurulum Adımları
```bash
# Virtual environment oluştur
python -m venv venv
source venv/bin/activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# Veritabanını oluştur
flask db upgrade

# Uygulamayı başlat
flask run
```

## 15. Bakım ve İzleme

### 15.1 Loglama
```python
import logging

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

def setup_logging():
    # Handler'ları yapılandır
    file_handler = logging.FileHandler('app.log')
    console_handler = logging.StreamHandler()
    
    # Formatter'ı ayarla
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Root logger'a handler'ları ekle
    logging.getLogger('').addHandler(file_handler)
    logging.getLogger('').addHandler(console_handler)
```

### 15.2 Metrik Toplama
```python
def track_metrics():
    metrics = {
        'active_users': User.query.filter_by(is_active=True).count(),
        'total_attendance': Attendance.query.count(),
        'face_recognition_accuracy': calculate_recognition_accuracy(),
        'emotion_analysis_accuracy': calculate_emotion_accuracy(),
        'api_response_time': calculate_average_response_time()
    }
    
    save_metrics(metrics)
```

## 16. Gelecek Geliştirmeler

### 16.1 Planlanan Özellikler
- Çoklu dil desteği
- Mobil uygulama entegrasyonu
- Gelişmiş analitik dashboard
- Otomatik ders programı oluşturma
- Öğrenci davranış analizi
- Gerçek zamanlı bildirimler

### 16.2 Teknik İyileştirmeler
- GraphQL API desteği
- WebSocket entegrasyonu
- Mikroservis mimarisine geçiş
- Edge computing desteği
- Progressive Web App (PWA) dönüşümü

## 17. Deployment ve Hosting

### 17.1 Render Deployment

#### Hosting Seçimi
Backend API'miz Render'ın ücretsiz planında host edilecektir. Bu seçimin nedenleri:
- Ücretsiz katmanda cömert limitler (750 saat/ay)
- FastAPI ile mükemmel uyumluluk
- Kolay deployment süreci
- Ücretsiz SSL sertifikası
- GitHub entegrasyonu
- Kullanıcı dostu arayüz

#### Teknik Özellikler
```yaml
Plan: Free Tier
RAM: 512MB
CPU: Shared CPU
Bandwidth: 500GB/ay
Storage: 500MB
Build Command: pip install -r requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
```

#### Deployment Adımları
1. Render.com'da Hesap Oluşturma
   - render.com üzerinde yeni hesap oluştur
   - Email doğrulamasını tamamla
   - GitHub hesabı ile bağlantı kur

2. Web Service Oluşturma
   ```bash
   # New Web Service seçimi
   - Connect GitHub repository
   - Select Python environment
   - Configure build settings
   ```

3. Environment Variables
   ```env
   PYTHON_VERSION=3.9
   PORT=8000
   ENVIRONMENT=production
   DATABASE_URL=sqlite:///./app.db
   JWT_SECRET_KEY=your-secret-key
   ```

4. Build ve Deploy Konfigürasyonu
   ```yaml
   # render.yaml
   services:
     - type: web
       name: yoklama-api
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
       envVars:
         - key: PYTHON_VERSION
           value: 3.9
         - key: PORT
           value: 8000
   ```

5. Otomatik Deployment
   - GitHub main branch'e push edildiğinde otomatik deployment
   - Deploy logları takibi
   - Rollback imkanı

#### Monitoring ve Bakım
- Render dashboard üzerinden:
  - CPU kullanımı takibi
  - Memory kullanımı kontrolü
  - Request sayısı monitörleme
  - Error log takibi
  - Deployment history

#### Ölçeklendirme Planı
- Başlangıç: Free Tier
- İhtiyaç halinde:
  - Individual Plan ($7/ay)
    - 1GB RAM
    - Dedicated CPU
    - No sleep mode
  - Team Plan ($15/ay)
    - 2GB RAM
    - 2x CPU
    - Priority support

#### Yedekleme Stratejisi
```python
# Günlük otomatik yedekleme
@scheduler.scheduled_job('cron', hour=3)
async def backup_database():
    timestamp = datetime.now().strftime('%Y%m%d')
    backup_path = f'backups/db_backup_{timestamp}.sql'
    
    # Veritabanı yedeği al
    await backup_service.create_backup(backup_path)
    
    # Yedekleri Render storage'a yükle
    await storage_service.upload_backup(backup_path)
```

#### Güvenlik Önlemleri
1. SSL/TLS Konfigürasyonu
   ```nginx
   # Render otomatik SSL
   ssl_protocols TLSv1.2 TLSv1.3;
   ssl_prefer_server_ciphers on;
   ```

2. Rate Limiting
   ```python
   @app.middleware("http")
   async def rate_limit_middleware(request: Request, call_next):
       # IP bazlı rate limiting
       client_ip = request.client.host
       if await rate_limiter.is_rate_limited(client_ip):
           raise HTTPException(status_code=429)
       return await call_next(request)
   ```

3. CORS Politikası
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://your-frontend-domain.com"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

#### Performans Optimizasyonu
1. Caching Stratejisi
   ```python
   # Redis cache (opsiyonel ücretli plan için)
   @cache(expire=3600)
   async def get_student_attendance(student_id: str):
       return await db.get_attendance(student_id)
   ```

2. Database Indexing
   ```sql
   CREATE INDEX idx_attendance_date ON attendance(date);
   CREATE INDEX idx_student_course ON student_courses(student_id, course_id);
   ```

3. Query Optimizasyonu
   ```python
   # N+1 sorgu problemi çözümü
   students = (
       db.query(Student)
       .options(joinedload(Student.courses))
       .filter(Student.active == True)
       .all()
   )
   ``` 