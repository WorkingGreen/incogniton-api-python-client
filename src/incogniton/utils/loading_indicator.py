import sys
import threading
import time
from typing import Optional

class LoadingAnimation:
    def __init__(self, message: str = "Loading", chars: str = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"):
        self.message = message
        self.chars = chars
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.current_char_index = 0

    def start(self) -> None:
        """Start the loading animation."""
        self.running = True
        self.thread = threading.Thread(target=self._animate)
        self.thread.daemon = True
        self.thread.start()

    def stop(self) -> None:
        """Stop the loading animation and clear the line."""
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join()
            sys.stdout.write('\r' + ' ' * (len(self.message) + 2) + '\r')
            sys.stdout.flush()

    def _animate(self) -> None:
        """Animate the loading indicator."""
        while self.running:
            sys.stdout.write(f'\r{self.chars[self.current_char_index]} {self.message}')
            sys.stdout.flush()
            self.current_char_index = (self.current_char_index + 1) % len(self.chars)
            time.sleep(0.1)

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()