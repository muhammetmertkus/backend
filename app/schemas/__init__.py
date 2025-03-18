"""
API şema modülleri.
"""
from app.schemas.auth import TokenSchema, LoginSchema
from app.schemas.user import UserSchema, UserCreateSchema, UserUpdateSchema
from app.schemas.student import StudentSchema, StudentCreateSchema, StudentUpdateSchema
from app.schemas.teacher import TeacherSchema, TeacherCreateSchema, TeacherUpdateSchema
from app.schemas.course import CourseSchema, CourseCreateSchema, CourseUpdateSchema
from app.schemas.attendance import AttendanceSchema, AttendanceCreateSchema

__all__ = [
    'TokenSchema', 'LoginSchema',
    'UserSchema', 'UserCreateSchema', 'UserUpdateSchema',
    'StudentSchema', 'StudentCreateSchema', 'StudentUpdateSchema',
    'TeacherSchema', 'TeacherCreateSchema', 'TeacherUpdateSchema',
    'CourseSchema', 'CourseCreateSchema', 'CourseUpdateSchema',
    'AttendanceSchema', 'AttendanceCreateSchema'
] 