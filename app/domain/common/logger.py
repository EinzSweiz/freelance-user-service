from abc import ABC, abstractmethod

class AbstractLogger(ABC):

    @abstractmethod
    def info(self, message: str) -> None:
        ...
    
    @abstractmethod
    def warning(self, message: str) -> None:
        ...

    @abstractmethod
    def error(self, message: str) -> None:
        ...

    @abstractmethod
    def debug(self, message: str) -> None:
        ...