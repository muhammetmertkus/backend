"""
Öğrenci işlemleri route'ları.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
import os
import secrets
import string
import json
import pandas as pd

from app import db
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.course import Course
from app.models.teacher import Teacher
from app.schemas.student import StudentSchema, StudentCreateSchema, StudentUpdateSchema, StudentListSchema
from app.services.face_service import FaceService
from app.utils.decorators import admin_required, teacher_or_admin_required
from app.core.config import Config
from app.utils.logger import logger
from app.services.email_service import email_service

bp = Blueprint('students', __name__)
face_service = FaceService()

@bp.route('/', methods=['GET'])
@jwt_required()
@teacher_or_admin_required
def get_students():
    """
    Tüm öğrencileri listele.
    
    Öğretmenler sadece kendi derslerindeki öğrencileri görebilir.
    Adminler tüm öğrencileri görebilir.
    """
    claims = get_jwt()
    role = claims.get('role', None)
    user_id = get_jwt_identity()
    
    logger.info(f"Öğrenci listesi isteği: user_id={user_id}, role={role}")
    
    # Rol bilgisi veya kontrol eksikliği için log
    if not role:
        logger.warning(f"JWT token'da rol bilgisi bulunamadı. Claims: {claims}")
        return jsonify({'error': 'Yetkilendirme bilgisi eksik'}), 403
    
    # Öğretmenler sadece kendi derslerindeki öğrencileri görebilsin
    if role == UserRole.TEACHER.value:
        # Öğretmeni user_id ile bul
        teacher = Teacher.query.join(User).filter(User.id == user_id).first()
        
        if not teacher:
            logger.error(f"Öğretmen bulunamadı: user_id={user_id}")
            return jsonify({'error': 'Öğretmen profili bulunamadı'}), 404
            
        teacher_id = teacher.id
        logger.info(f"Öğretmen bulundu: user_id={user_id}, teacher_id={teacher_id}")
        
        # Öğretmenin derslerindeki öğrencileri getir
        courses = Course.query.filter_by(teacher_id=teacher_id).all()
        logger.info(f"Öğretmen {teacher_id} için {len(courses)} ders bulundu")
        
        # Kursların isimlerini logla
        for course in courses:
            logger.info(f"Ders: id={course.id}, name={course.name}, öğrenci sayısı={len(course.students)}")
        
        if not courses:
            logger.warning(f"Öğretmen {teacher_id} için ders bulunamadı")
            return jsonify([]), 200
            
        student_ids = []
        for course in courses:
            for student in course.students:
                if student.id not in student_ids:
                    student_ids.append(student.id)
        
        logger.info(f"Toplam benzersiz öğrenci sayısı: {len(student_ids)}")
        students = Student.query.filter(Student.id.in_(student_ids)).all() if student_ids else []
    else:
        # Admin tüm öğrencileri görebilir
        students = Student.query.all()
        logger.info(f"Admin için {len(students)} öğrenci bulundu")
    
    # StudentSchema yerine öğrenci listesi için tasarlanmış StudentListSchema kullanılıyor
    schema = StudentListSchema(many=True)
    result = schema.dump(students)
    logger.info(f"Öğrenci listesi döndürülüyor: {len(result)} öğrenci")
    return jsonify(result), 200

@bp.route('/<int:student_id>', methods=['GET'])
@jwt_required()
@teacher_or_admin_required
def get_student(student_id):
    """
    Belirli bir öğrenciyi getir.
    
    Öğretmenler sadece kendi derslerindeki öğrencileri görebilir.
    Adminler tüm öğrencileri görebilir.
    """
    student = Student.query.get_or_404(student_id)
    logger.info(f"Öğrenci detay isteği: student_id={student_id}")
    
    # Öğretmen yetkisi kontrolü
    claims = get_jwt()
    role = claims.get('role', None)
    user_id = get_jwt_identity()
    
    if role == UserRole.TEACHER.value:
        # Öğretmeni user_id ile bul
        teacher = Teacher.query.join(User).filter(User.id == user_id).first()
        
        if not teacher:
            logger.error(f"Öğretmen bulunamadı: user_id={user_id}")
            return jsonify({'error': 'Öğretmen profili bulunamadı'}), 404
            
        teacher_id = teacher.id
        logger.info(f"Öğretmen bulundu: user_id={user_id}, teacher_id={teacher_id}")
        
        # Öğrencinin öğretmenin bir dersinde olup olmadığını kontrol et
        teacher_courses = Course.query.filter_by(teacher_id=teacher_id).all()
        student_in_teacher_course = False
        
        for course in teacher_courses:
            logger.info(f"Ders kontrolü: id={course.id}, name={course.name}")
            if student in course.students:
                student_in_teacher_course = True
                logger.info(f"Öğrenci {student_id}, {course.name} dersinde bulundu")
                break
                
        if not student_in_teacher_course:
            logger.warning(f"Öğrenci {student_id}, öğretmen {teacher_id}'nin hiçbir dersinde bulunamadı")
            return jsonify({'error': 'Bu öğrenciye erişim yetkiniz bulunmamaktadır'}), 403
    
    schema = StudentSchema()
    return jsonify(schema.dump(student)), 200

@bp.route('/', methods=['POST'])
@jwt_required()
@teacher_or_admin_required
def create_student():
    """Yeni öğrenci oluştur."""
    schema = StudentCreateSchema()
    data = schema.load(request.get_json())
    logger.info(f"Yeni öğrenci oluşturma isteği: email={data['email']}, student_number={data['student_number']}")
    
    # Öğretmen rolünü kontrol et
    claims = get_jwt()
    role = claims.get('role', None)
    user_id = get_jwt_identity()
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Bu email zaten kullanılıyor'}), 400
        
    if Student.query.filter_by(student_number=data['student_number']).first():
        return jsonify({'error': 'Bu öğrenci numarası zaten kullanılıyor'}), 400
    
    try:
        # Kullanıcı oluştur
        user = User(
            email=data['email'],
            password=generate_password_hash(data['password']),
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=UserRole.STUDENT
        )
        db.session.add(user)
        db.session.commit()
        
        # Öğrenci oluştur
        student = Student(
            user_id=user.id,
            student_number=data['student_number'],
            department=data['department']
        )
        db.session.add(student)
        db.session.commit()
        
        # Öğretmen ise, öğrenciyi kendi dersine ekle
        if role == UserRole.TEACHER.value:
            # Öğretmeni user_id ile bul
            teacher = Teacher.query.join(User).filter(User.id == user_id).first()
            
            if not teacher:
                logger.error(f"Öğretmen bulunamadı: user_id={user_id}")
                return jsonify({'error': 'Öğretmen profili bulunamadı'}), 404
                
            teacher_id = teacher.id
            logger.info(f"Öğretmen bulundu: user_id={user_id}, teacher_id={teacher_id}")
            
            # İsteğin body'sinden course_id'yi al
            course_id = None
            if 'course_id' in data:
                course_id = data['course_id']
            elif 'course_id' in request.get_json():
                course_id = request.get_json()['course_id']
            
            if course_id:
                course = Course.query.filter_by(id=course_id, teacher_id=teacher_id).first()
                if course:
                    logger.info(f"Öğrenci {data['student_number']}, kurs {course.name}'e ekleniyor")
                    course.students.append(student)
                    db.session.commit()
                    logger.info(f"Öğrenci başarıyla {course.name} dersine eklendi")
                else:
                    logger.warning(f"Kurs bulunamadı veya öğretmene ait değil: course_id={course_id}, teacher_id={teacher_id}")
            else:
                logger.warning("course_id belirtilmediği için öğrenci herhangi bir kursa eklenmedi. Öğretmen olarak giriş yaptıysanız, listelediğinizde bu öğrenciyi GÖREMEYECEKSİNİZ!")
        
        logger.info(f"Yeni öğrenci oluşturuldu: {student.student_number}")
        schema = StudentSchema()
        response = schema.dump(student)
        
        # Uyarı mesajı ekle
        messages = []
        if role == UserRole.TEACHER.value and 'course_id' not in data and 'course_id' not in request.get_json():
            messages.append("UYARI: Öğrenci hiçbir derse atanmadı. Öğretmen rolündeyseniz, bu öğrenciyi listenizde göremeyeceksiniz!")
        
        if messages:
            response['messages'] = messages
        
        return jsonify(response), 201
    except Exception as e:
        logger.error(f"Öğrenci oluşturma hatası: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Öğrenci oluşturulamadı'}), 500

@bp.route('/<int:student_id>', methods=['PUT'])
@jwt_required()
@teacher_or_admin_required
def update_student(student_id):
    """
    Öğrenci bilgilerini güncelle.
    
    Öğretmenler sadece kendi derslerindeki öğrencileri güncelleyebilir.
    Adminler tüm öğrencileri güncelleyebilir.
    """
    student = Student.query.get_or_404(student_id)
    logger.info(f"Öğrenci güncelleme isteği: student_id={student_id}")
    
    # Öğretmen yetkisi kontrolü
    claims = get_jwt()
    role = claims.get('role', None)
    user_id = get_jwt_identity()
    
    if role == UserRole.TEACHER.value:
        # Öğretmeni user_id ile bul
        teacher = Teacher.query.join(User).filter(User.id == user_id).first()
        
        if not teacher:
            logger.error(f"Öğretmen bulunamadı: user_id={user_id}")
            return jsonify({'error': 'Öğretmen profili bulunamadı'}), 404
            
        teacher_id = teacher.id
        logger.info(f"Öğretmen bulundu: user_id={user_id}, teacher_id={teacher_id}")
        
        # Öğrencinin öğretmenin bir dersinde olup olmadığını kontrol et
        teacher_courses = Course.query.filter_by(teacher_id=teacher_id).all()
        student_in_teacher_course = False
        
        for course in teacher_courses:
            logger.info(f"Ders kontrolü: id={course.id}, name={course.name}")
            if student in course.students:
                student_in_teacher_course = True
                logger.info(f"Öğrenci {student_id}, {course.name} dersinde bulundu")
                break
                
        if not student_in_teacher_course:
            logger.warning(f"Öğrenci {student_id}, öğretmen {teacher_id}'nin hiçbir dersinde bulunamadı")
            return jsonify({'error': 'Bu öğrenciyi güncelleme yetkiniz bulunmamaktadır'}), 403
    
    schema = StudentUpdateSchema()
    data = schema.load(request.get_json())
    
    try:
        # Kullanıcı bilgilerini güncelle
        if 'email' in data:
            student.user.email = data['email']
        if 'first_name' in data:
            student.user.first_name = data['first_name']
        if 'last_name' in data:
            student.user.last_name = data['last_name']
        if 'password' in data:
            student.user.password = generate_password_hash(data['password'])
            
        # Öğrenci bilgilerini güncelle
        if 'student_number' in data:
            student.student_number = data['student_number']
        
        db.session.commit()
        logger.info(f"Öğrenci güncellendi: {student.student_number}")
        schema = StudentSchema()
        return jsonify(schema.dump(student)), 200
    except Exception as e:
        logger.error(f"Öğrenci güncelleme hatası: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Öğrenci güncellenemedi'}), 500

@bp.route('/<int:student_id>/face', methods=['POST'])
@jwt_required()
@teacher_or_admin_required
def upload_face_photo(student_id):
    """
    Öğrenci yüz fotoğrafı yükle.
    
    Öğretmenler sadece kendi derslerindeki öğrencilerin fotoğraflarını yükleyebilir.
    Adminler tüm öğrencilerin fotoğraflarını yükleyebilir.
    """
    student = Student.query.get_or_404(student_id)
    logger.info(f"Öğrenci yüz fotoğrafı yükleme isteği: student_id={student_id}")
    
    # Öğretmen yetkisi kontrolü
    claims = get_jwt()
    role = claims.get('role', None)
    user_id = get_jwt_identity()
    
    if role == UserRole.TEACHER.value:
        # Öğretmeni user_id ile bul
        teacher = Teacher.query.join(User).filter(User.id == user_id).first()
        
        if not teacher:
            logger.error(f"Öğretmen bulunamadı: user_id={user_id}")
            return jsonify({'error': 'Öğretmen profili bulunamadı'}), 404
            
        teacher_id = teacher.id
        logger.info(f"Öğretmen bulundu: user_id={user_id}, teacher_id={teacher_id}")
        
        # Öğrencinin öğretmenin bir dersinde olup olmadığını kontrol et
        teacher_courses = Course.query.filter_by(teacher_id=teacher_id).all()
        student_in_teacher_course = False
        
        for course in teacher_courses:
            logger.info(f"Ders kontrolü: id={course.id}, name={course.name}")
            if student in course.students:
                student_in_teacher_course = True
                logger.info(f"Öğrenci {student_id}, {course.name} dersinde bulundu")
                break
                
        if not student_in_teacher_course:
            logger.warning(f"Öğrenci {student_id}, öğretmen {teacher_id}'nin hiçbir dersinde bulunamadı")
            return jsonify({'error': 'Bu öğrenciye yüz fotoğrafı ekleme yetkiniz bulunmamaktadır'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'Fotoğraf yüklenmedi'}), 400
        
    file = request.files['file']
    if not file:
        return jsonify({'error': 'Geçersiz dosya'}), 400
    
    try:
        # Dosya yolu oluştur
        filename = secure_filename(f"{student.student_number}.jpg")
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        
        # Dosyayı bytes olarak oku
        file_bytes = file.read()
        
        # Yüz özelliklerini çıkar
        face_encoding = face_service.encode_face(file_bytes)
        if face_encoding is None:
            return jsonify({'error': 'Fotoğrafta yüz tespit edilemedi'}), 400
            
        # Numpy array'i listeye dönüştür
        if hasattr(face_encoding, 'tolist'):
            face_encoding = face_encoding.tolist()
            
        # JSON formatına dönüştür
        face_encoding_json = json.dumps(face_encoding)
        
        # Dosyayı kaydet
        with open(filepath, 'wb') as f:
            f.write(file_bytes)
        
        # Öğrenci bilgilerini güncelle
        student.face_encoding = face_encoding_json
        student.face_photo_url = f"/uploads/{filename}"
        
        db.session.commit()
        logger.info(f"Öğrenci yüz fotoğrafı güncellendi: {student.student_number}")
        schema = StudentSchema()
        return jsonify(schema.dump(student)), 200
    except Exception as e:
        logger.error(f"Yüz fotoğrafı yükleme hatası: {str(e)}")
        db.session.rollback()
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': 'Yüz fotoğrafı yüklenemedi'}), 500

@bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Öğrenci şifre hatırlatma."""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email adresi gerekli'}), 400
            
        student = Student.query.join(User).filter(User.email == email, User.role == UserRole.STUDENT).first()
        if not student:
            return jsonify({'error': 'Bu email adresine sahip öğrenci bulunamadı'}), 404
            
        # Şifreyi veritabanından al
        user = student.user
        if not hasattr(user, 'plain_password'):
            # Eğer plain_password yoksa yeni şifre oluştur
            new_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
            user.password = generate_password_hash(new_password)
            user.plain_password = new_password
            db.session.commit()
            password_to_send = new_password
        else:
            password_to_send = user.plain_password
            
        # Email gönder
        if email_service.send_password_reset_email(email, student.user.first_name, password_to_send):
            logger.info(f"Şifre hatırlatma emaili gönderildi: {email}")
            return jsonify({'message': 'Şifreniz email adresinize gönderildi'}), 200
        else:
            return jsonify({'error': 'Email gönderilemedi'}), 500
            
    except Exception as e:
        logger.error(f"Şifre hatırlatma hatası: {str(e)}")
        return jsonify({'error': 'Şifre hatırlatma işlemi başarısız'}), 500

@bp.route('/bulk-import', methods=['POST'])
@jwt_required()
@teacher_or_admin_required
def bulk_import_students():
    """
    Excel dosyasından toplu öğrenci içe aktarma.
    
    Öğretmenler ve adminler toplu öğrenci ekleyebilir.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'Dosya yüklenmedi'}), 400
        
    file = request.files['file']
    if not file:
        return jsonify({'error': 'Geçersiz dosya'}), 400
    
    # JWT token'dan kullanıcı bilgilerini al
    claims = get_jwt()
    role = claims.get('role', None)
    user_id = get_jwt_identity()
        
    # Dosya uzantısını kontrol et
    if not file.filename.endswith(('.xlsx', '.xls')):
        return jsonify({'error': 'Sadece Excel dosyaları (.xlsx, .xls) desteklenmektedir'}), 400
    
    try:
        # Excel dosyasını oku
        df = pd.read_excel(file)
        
        # Gerekli sütunları kontrol et
        required_columns = ['Öğrenci No', 'Ad', 'Soyad', 'Email', 'Bölüm']
        for column in required_columns:
            if column not in df.columns:
                return jsonify({'error': f"'{column}' sütunu bulunamadı"}), 400
        
        # İşlem sonuçları
        results = {
            'total': len(df),
            'success': 0,
            'failed': 0,
            'errors': []
        }
        
        # Öğretmen ise, teacher_id'yi doğru şekilde al
        teacher_id = None
        if role == UserRole.TEACHER.value:
            teacher = Teacher.query.join(User).filter(User.id == user_id).first()
            if not teacher:
                logger.error(f"Öğretmen bulunamadı: user_id={user_id}")
                return jsonify({'error': 'Öğretmen profili bulunamadı'}), 404
            teacher_id = teacher.id
            logger.info(f"Öğretmen bulundu: user_id={user_id}, teacher_id={teacher_id}")
        
        # Her satır için işlem yap
        for index, row in df.iterrows():
            try:
                # Verileri al
                student_number = str(row['Öğrenci No'])
                first_name = row['Ad']
                last_name = row['Soyad']
                email = row['Email']
                department = row['Bölüm']
                password = row['Şifre'] if 'Şifre' in row and not pd.isna(row['Şifre']) else ''.join(
                    secrets.choice(string.ascii_letters + string.digits) for _ in range(8)
                )
                
                # Kayıt kontrolü
                if User.query.filter_by(email=email).first():
                    results['errors'].append({
                        'row': index + 2,  # Excel satır numarası (başlık + 1)
                        'email': email,
                        'reason': 'Bu email adresi zaten kullanılıyor'
                    })
                    results['failed'] += 1
                    continue
                    
                if Student.query.filter_by(student_number=student_number).first():
                    results['errors'].append({
                        'row': index + 2,
                        'student_number': student_number,
                        'reason': 'Bu öğrenci numarası zaten kullanılıyor'
                    })
                    results['failed'] += 1
                    continue
                
                # Yeni kullanıcı oluştur
                user = User(
                    email=email,
                    password=generate_password_hash(password),
                    first_name=first_name,
                    last_name=last_name,
                    role=UserRole.STUDENT,
                    plain_password=password  # Şifre gönderebilmek için
                )
                db.session.add(user)
                db.session.flush()
                
                # Yeni öğrenci oluştur
                student = Student(
                    user_id=user.id,
                    student_number=student_number,
                    department=department
                )
                db.session.add(student)
                
                # Öğretmen ise, kendi derslerine otomatik ekle
                if role == UserRole.TEACHER.value and teacher_id:
                    course_id = request.form.get('course_id')
                    
                    if course_id:
                        course = Course.query.filter_by(id=course_id, teacher_id=teacher_id).first()
                        if course:
                            logger.info(f"Öğrenci {student_number}, kurs {course.name}'e ekleniyor")
                            course.students.append(student)
                        else:
                            logger.warning(f"Kurs bulunamadı veya öğretmene ait değil: course_id={course_id}, teacher_id={teacher_id}")
                    else:
                        logger.warning(f"course_id belirtilmediği için öğrenci {student_number} herhangi bir kursa eklenmedi")
                
                # E-posta gönder
                email_service.send_welcome_email(
                    email, 
                    first_name, 
                    password, 
                    student_number
                )
                
                results['success'] += 1
                
            except Exception as e:
                logger.error(f"Satır {index+2} işleme hatası: {str(e)}")
                results['errors'].append({
                    'row': index + 2,
                    'student_number': str(row['Öğrenci No']) if 'Öğrenci No' in row else 'N/A',
                    'reason': str(e)
                })
                results['failed'] += 1
        
        # İşlem başarılı ise veritabanına kaydet
        if results['success'] > 0:
            db.session.commit()
            logger.info(f"Toplu öğrenci içe aktarma: {results['success']} başarılı, {results['failed']} başarısız")
        else:
            db.session.rollback()
        
        # Uyarı mesajı ekle
        message = f"{results['success']} öğrenci başarıyla içe aktarıldı"
        if role == UserRole.TEACHER.value and not request.form.get('course_id'):
            message += ". UYARI: course_id belirtilmediği için öğrenciler herhangi bir kursa eklenmedi. Öğrenci listesinde bu öğrencileri göremeyeceksiniz!"
            
        return jsonify({
            'message': message,
            'details': results
        }), 200
        
    except Exception as e:
        logger.error(f"Excel içe aktarma hatası: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Excel dosyası işlenemedi', 'details': str(e)}), 500

@bp.route('/course/<int:course_id>', methods=['GET'])
@jwt_required()
@teacher_or_admin_required
def get_students_by_course(course_id):
    """
    Belirli bir dersteki tüm öğrencileri getir.
    
    Öğretmenler sadece kendi derslerindeki öğrencileri görebilir.
    Adminler tüm derslerin öğrencilerini görebilir.
    """
    # Ders kontrolü
    course = Course.query.get_or_404(course_id)
    logger.info(f"Ders öğrenci listesi isteği: course_id={course_id}")
    
    # Öğretmen yetkisi kontrolü
    claims = get_jwt()
    role = claims.get('role', None)
    user_id = get_jwt_identity()
    
    if role == UserRole.TEACHER.value:
        # Öğretmeni user_id ile bul
        teacher = Teacher.query.join(User).filter(User.id == user_id).first()
        
        if not teacher:
            logger.error(f"Öğretmen bulunamadı: user_id={user_id}")
            return jsonify({'error': 'Öğretmen profili bulunamadı'}), 404
            
        teacher_id = teacher.id
        
        # Dersin öğretmene ait olup olmadığını kontrol et
        if course.teacher_id != teacher_id:
            logger.warning(f"Yetkisiz ders erişimi: course_id={course_id}, teacher_id={teacher_id}")
            return jsonify({'error': 'Bu dersin öğrencilerine erişim yetkiniz bulunmamaktadır'}), 403
    
    # Dersteki öğrencileri getir
    students = course.students
    logger.info(f"{course.name} dersindeki öğrenci sayısı: {len(students)}")
    
    schema = StudentListSchema(many=True)
    result = schema.dump(students)
    return jsonify(result), 200 