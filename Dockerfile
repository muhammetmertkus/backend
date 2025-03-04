FROM python:3.11-slim

# Sistem bağımlılıklarını kur
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    pkg-config \
    libx11-dev \
    libatlas-base-dev \
    libgtk-3-dev \
    libboost-python-dev \
    python3-dev \
    python3-pip \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Çalışma dizinini ayarla
WORKDIR /app

# Gerekli dosyaları kopyala
COPY requirements.txt .
COPY . .

# Python bağımlılıklarını kur
RUN pip install --no-cache-dir -r requirements.txt

# Veritabanı migrasyonlarını çalıştır
RUN alembic upgrade head

# Uygulamayı çalıştır
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
