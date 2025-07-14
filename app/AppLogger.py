import logging
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger  # (опционально)
from typing import Optional, Dict, Any

class AppLogger:
    def __init__(
        self,
        name: str = "app",
        log_file: str = "app.log",
        level: int = logging.INFO,
        max_bytes: int = 10 * 1024 * 1024,  # 10 MB
        backup_count: int = 5,
        json_format: bool = False,
    ):
        """Метод инициализации класса"""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Форматтер (текстовый или JSON)
        if json_format:
            formatter = jsonlogger.JsonFormatter(
                "%(asctime)s %(name)s %(levelname)s %(message)s"
            )
        else:
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        
        # Файловый обработчик с ротацией
        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def log(
        self,
        level: int,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
        exc_info: bool = False,
    ):
        """Общий метод для логирования.\n
        Уровни Логирования:\n
        NOTSET    0	    Не установлен (используется уровень родительского логгера).\n
        DEBUG     10	Подробная информация для отладки (разработка, тестирование).\n
        INFO      20	Информационные сообщения (нормальная работа приложения).\n
        WARNING   30	Предупреждения (потенциальные проблемы, но приложение работает).\n
        ERROR     40	Ошибки (серьёзные проблемы, часть функционала не работает).\n
        CRITICAL  50	Критические ошибки (приложение может полностью остановиться).\n
        """
        self.logger.log(level, message, extra=extra, exc_info=exc_info)

    # Вариативное исполнение каждого отдельного уровня 
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        self.log(logging.INFO, message, extra=extra)

    def error(self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info: bool = False):
        self.log(logging.ERROR, message, extra=extra, exc_info=exc_info)

    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        self.log(logging.WARNING, message, extra=extra)

    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        self.log(logging.DEBUG, message, extra=extra)

    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None):
        self.log(logging.CRITICAL, message, extra=extra)