import logging
from app.domain.common.logger import AbstractLogger

class AppLogger(AbstractLogger):

    def __init__(self, name: str = "app") -> None:
        self.logger = logging.getLogger(name=name)
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def info(self, message: str) -> None:
        self.logger.info(message)
    
    def error(self, message: str) -> None:
        self.logger.error(message)
    
    def debug(self, message: str) -> None:
        self.logger.debug(message)
    
    def warning(self, message: str) -> None:
        self.logger.warning(message)

def get_logger(name: str = "app") -> AbstractLogger:
    return AppLogger(name=name)