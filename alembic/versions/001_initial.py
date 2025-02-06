"""initial

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# postgresql'e özgü JSON tipini kaldırıyoruz
# from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Users tablosu
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password', sa.String(255), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('surname', sa.String(100), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),  # Enum yerine String kullanıyoruz
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('idx_users_email', 'users', ['email'])

    # Students tablosu
    op.create_table(
        'students',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('student_number', sa.String(20), nullable=False),
        sa.Column('department', sa.String(100), nullable=False),
        sa.Column('face_encodings', sa.Text(), nullable=True),  # JSON yerine Text kullanıyoruz
        sa.Column('face_photo_url', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('student_number')
    )
    op.create_index('idx_students_number', 'students', ['student_number'])

    # Teachers tablosu
    op.create_table(
        'teachers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('department', sa.String(100), nullable=False),
        sa.Column('title', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Courses tablosu
    op.create_table(
        'courses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(20), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('teacher_id', sa.Integer(), nullable=False),
        sa.Column('semester', sa.String(20), nullable=False),
        sa.Column('schedule', sa.Text(), nullable=True),  # JSON yerine Text kullanıyoruz
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['teacher_id'], ['teachers.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index('idx_courses_code', 'courses', ['code'])

    # Attendance tablosu
    op.create_table(
        'attendance',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('type', sa.String(20), nullable=False),  # Enum yerine String kullanıyoruz
        sa.Column('photo_url', sa.String(255), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),  # JSON yerine Text kullanıyoruz
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_attendance_course_date', 'attendance', ['course_id', 'date'])

    # AttendanceDetail tablosu
    op.create_table(
        'attendance_details',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('attendance_id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Boolean(), default=False),
        sa.Column('emotion_data', sa.Text(), nullable=True),  # JSON yerine Text kullanıyoruz
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['attendance_id'], ['attendance.id']),
        sa.ForeignKeyConstraint(['student_id'], ['students.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_attendance_details_student', 'attendance_details', ['student_id'])

    # EmotionHistory tablosu
    op.create_table(
        'emotion_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('emotion', sa.String(50), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['students.id']),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_emotion_history_student', 'emotion_history', ['student_id'])
    op.create_index('idx_emotion_history_date', 'emotion_history', ['date'])

def downgrade():
    op.drop_table('emotion_history')
    op.drop_table('attendance_details')
    op.drop_table('attendance')
    op.drop_table('courses')
    op.drop_table('teachers')
    op.drop_table('students')
    op.drop_table('users') 