import sys
import threading
import time
from typing import Optional

class LoadingAnimation:
    def __init__(self, message: str = "Loading", chars: str = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"):
        self.message = zmessage
        self.chars = chars
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.current_char_index = 0

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def run(self):
        while self.running:
            self.current_char_index = (self.current_char_index + 1) % len(self.chars)
            sys.stdout.write(self.chars[self.current_char_index])
            sys.stdout.flush()
            time.sleep(0.2)

    def stop(self):
        self.running = False
        self.thread.join()