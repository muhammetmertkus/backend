"""
API route modülleri.
"""
from app.routes.auth import bp as auth_bp
from app.routes.students import bp as students_bp
from app.routes.courses import bp as courses_bp
from app.routes.attendance import bp as attendance_bp
from app.routes.reports import bp as reports_bp
from app.routes.teachers import bp as teachers_bp

__all__ = ['auth', 'students', 'courses', 'attendance', 'reports', 'teachers'] 