from typing import List, Dict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from app.utils.logger import logger

class EmailService:
    """Email servisi."""

    def __init__(self):
        self.server = settings.SMTP_SERVER
        self.port = settings.SMTP_PORT
        self.username = settings.SMTP_USERNAME
        self.password = settings.SMTP_PASSWORD

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html: bool = False
    ) -> bool:
        """Email gönder."""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # SMTP sunucusuna bağlan
            server = smtplib.SMTP(self.server, self.port)
            server.starttls()
            server.login(self.username, self.password)
            
            # Emaili gönder
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email gönderildi: {to_email}")
            return True
        except Exception as e:
            logger.error(f"Email gönderme hatası: {str(e)}")
            return False

    def send_attendance_notification(
        self,
        email: str,
        course_name: str,
        status: bool
    ) -> bool:
        """Yoklama bildirimi gönder."""
        subject = f"Yoklama Bildirimi - {course_name}"
        status_text = "alındı" if status else "alınamadı"
        
        body = f"""
        Merhaba,
        
        {course_name} dersi için yoklamanız {status_text}.
        
        Saygılarımızla,
        Yoklama Sistemi
        """
        
        return self.send_email(email, subject, body)

    def send_bulk_attendance_notification(
        self,
        notifications: List[Dict[str, str]]
    ) -> None:
        """Toplu yoklama bildirimi gönder."""
        for notification in notifications:
            self.send_attendance_notification(
                notification['email'],
                notification['course_name'],
                notification['status']
            ) 