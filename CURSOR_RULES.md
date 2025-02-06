# Veritabanı Kuralları
- SQLite veritabanı kullanılacak
- Veritabanı dosyası: attendance.db
- Tablo isimleri çoğul ve snake_case
- Primary key'ler 'id' olarak isimlendirilmeli
- Foreign key'ler 'table_name_id' formatında olmalı
- Index isimleri 'idx_' prefix'i ile başlamalı
- Tarih alanları için UTC timezone kullanılmalı
- SQLite için PRAGMA foreign_keys = ON kullanılmalı 