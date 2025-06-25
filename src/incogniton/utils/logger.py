import logging
import sys
from typing import Optional

class Logger:
    HEADER = '\033[95m'
    INFO = '\033[94m'
    SUCCESS = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

    _instance: Optional['Logger'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize the logger with custom formatting."""
        self.logger = logging.getLogger('incogniton')
        self.logger.setLevel(logging.INFO)

        # Console handler with colored output
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            logging.Formatter('%(message)s')
        )
        self.logger.addHandler(console_handler)

    def info(self, message: str) -> None:
        """Log an info message."""
        self.logger.info(f"{self.INFO}{message}{self.ENDC}")

    def success(self, message: str) -> None:
        """Log a success message."""
        self.logger.info(f"{self.SUCCESS}{message}{self.ENDC}")

    def warning(self, message: str) -> None:
        """Log a warning message."""
        self.logger.warning(f"{self.WARNING}{message}{self.ENDC}")

    def error(self, message: str) -> None:
        """Log an error message."""
        self.logger.error(f"{self.ERROR}{message}{self.ENDC}")

    def header(self, message: str) -> None:
        """Log a header message."""
        self.logger.info(f"{self.HEADER}{self.BOLD}{message}{self.ENDC}")

# Create a singleton instance
logger = Logger()
