import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger
from app.core.config import settings

# Log dizini oluştur
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Logger yapılandırması
logger = logging.getLogger("yoklama")
logger.setLevel(settings.LOG_LEVEL)

# JSON formatter
class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['level'] = record.levelname
        log_record['logger'] = record.name

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(CustomJsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s'))
logger.addHandler(console_handler)

# File handler
file_handler = RotatingFileHandler(
    log_dir / "app.log",
    maxBytes=10485760,  # 10MB
    backupCount=5,
    encoding="utf-8"
)
file_handler.setFormatter(CustomJsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s'))
logger.addHandler(file_handler)

# Error file handler
error_handler = RotatingFileHandler(
    log_dir / "error.log",
    maxBytes=10485760,  # 10MB
    backupCount=5,
    encoding="utf-8"
)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(CustomJsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s'))
logger.addHandler(error_handler) 