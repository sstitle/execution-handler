import logging
import coloredlogs
from .singleton import SingletonMeta

class Logger(metaclass=SingletonMeta):
    """Thread-safe singleton logger with colored output."""

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._logger = logging.getLogger("execution-handler")
            self._logger.setLevel(logging.INFO)

            # Clear any existing handlers to avoid duplicates
            self._logger.handlers.clear()

            # Set up colored logging
            fmt = (
                "%(asctime)s %(processName)s[%(process)d] %(threadName)s[%(thread)d] "
                "%(name)s %(levelname)s: %(message)s"
            )
            field_styles = {
                "asctime": {"color": "cyan"},
                "processName": {"color": "magenta", "bold": True},
                "process": {"color": "magenta"},
                "threadName": {"color": "blue", "bold": True},
                "thread": {"color": "blue"},
                "name": {"color": "green", "bold": True},
                "levelname": {"color": "white", "bold": True},
            }
            level_styles = {
                "info": {"color": "cyan", "bold": True},
                "warning": {"color": "yellow", "bold": True},
                "error": {"color": "red", "bold": True},
                "critical": {"color": "red", "bold": True, "background": "white"},
                "debug": {"color": "white"},
            }

            coloredlogs.install(
                level=logging.INFO,
                logger=self._logger,
                fmt=fmt,
                field_styles=field_styles,
                level_styles=level_styles,
            )

            self._initialized = True

    def get_logger(self) -> logging.Logger:
        """Get the underlying logging.Logger instance."""
        return self._logger

    def info(self, message: str) -> None:
        """Log an info message."""
        self._logger.info(message)

    def debug(self, message: str) -> None:
        """Log a debug message."""
        self._logger.debug(message)

    def warning(self, message: str) -> None:
        """Log a warning message."""
        self._logger.warning(message)

    def error(self, message: str) -> None:
        """Log an error message."""
        self._logger.error(message)

    def critical(self, message: str) -> None:
        """Log a critical message."""
        self._logger.critical(message)

logger = Logger()