from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
import os
from app.core.config import Config

# Veritabanı ve şema nesnelerini başlat
db = SQLAlchemy()
ma = Marshmallow()
jwt = JWTManager()
migrate = Migrate()

def create_app(config_class=Config):
    """Uygulama oluştur."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config['JSON_AS_ASCII'] = False
    app.config['CORS_SUPPORTS_CREDENTIALS'] = True
    
    # Uzantıları başlat
    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    
    # JWT hata yakalama
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        # Kullanıcı kimliğini string'e dönüştür
        return str(user) if user is not None else None
        
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        from app.models.user import User
        identity = jwt_data["sub"]
        if identity is None:
            return None
            
        # String kimliği integer'a çevir
        try:
            user_id = int(identity)
            return User.query.filter_by(id=user_id).one_or_none()
        except (ValueError, TypeError):
            return None
            
    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        from app.utils.logger import logger
        logger.warning(f"Geçersiz token: {error_string}")
        return jsonify({"error": "Geçersiz kimlik doğrulama token'ı"}), 401
        
    @jwt.expired_token_loader
    def expired_token_callback(_jwt_header, jwt_payload):
        return jsonify({"error": "Token süresi doldu"}), 401
        
    @jwt.unauthorized_loader
    def missing_token_callback(error_string):
        return jsonify({"error": "Kimlik doğrulama token'ı gerekli"}), 401
    
    # CORS ayarları
    CORS(app, 
         resources={
             r"/*": {
                 "origins": ["http://localhost:3000", "http://127.0.0.1:3000", 
                           "http://localhost:8000", "http://127.0.0.1:8000",
                           "http://192.168.1.3:8000", 
                           "https://*.herokuapp.com", "https://*.onrender.com"],
                 "methods": ["GET", "HEAD", "POST", "OPTIONS", "PUT", "PATCH", "DELETE"],
                 "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Origin",
                                 "Access-Control-Allow-Credentials", "X-Requested-With"],
                 "expose_headers": ["Content-Type", "Authorization"],
                 "supports_credentials": True
             }
         })
    
    # Blueprint'leri kaydet
    from app.routes.auth import bp as auth_bp
    from app.routes.students import bp as students_bp
    from app.routes.courses import bp as courses_bp
    from app.routes.attendance import bp as attendance_bp
    from app.routes.reports import bp as reports_bp
    from app.routes.teachers import bp as teachers_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(students_bp, url_prefix='/api/students')
    app.register_blueprint(courses_bp, url_prefix='/api/courses')
    app.register_blueprint(attendance_bp, url_prefix='/api/attendance')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')
    app.register_blueprint(teachers_bp, url_prefix='/api/teachers')
    
    # Swagger UI için statik dosyaları sunma
    @app.route('/api/docs/')
    @app.route('/api/docs')
    def swagger_ui():
        response = send_from_directory('static', 'swagger-ui.html')
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        return response
        
    @app.route('/api/swagger.json')
    def swagger_json():
        response = send_from_directory('static', 'swagger.json')
        response.headers['Content-Type'] = 'application/json'
        return response
        
    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin')
        allowed_origins = ["http://localhost:3000", "http://127.0.0.1:3000", 
                         "http://localhost:8000", "http://127.0.0.1:8000",
                         "http://192.168.1.3:8000"]
        
        # Heroku ve Render domain'lerini izin ver
        if origin and (origin in allowed_origins or 
                     origin.endswith('.herokuapp.com') or 
                     origin.endswith('.onrender.com')):
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            
        if request.method == 'OPTIONS':
            response.headers['Access-Control-Allow-Methods'] = 'GET, HEAD, POST, OPTIONS, PUT, PATCH, DELETE'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
            response.headers['Access-Control-Max-Age'] = '3600'
            
        return response
    
    return app 