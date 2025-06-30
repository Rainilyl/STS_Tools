import pyperclip
import time
import pyperclip
import time
import threading

class ClipboardMonitor:
    def __init__(self, callback, interval=0.5):
        self.callback = callback
        self.interval = interval
        self.last_text = ""
        self.is_running = False
        self.thread = None
    
    def start(self):
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(
                target=self._monitor,
                daemon=True
            )
            self.thread.start()
    
    def stop(self):
        self.is_running = False
    
    def _monitor(self):
        while self.is_running:
            try:
                text = pyperclip.paste()
                if text and text != self.last_text and text.strip():
                    self.last_text = text
                    self.callback(text)
            except Exception:
                pass
            time.sleep(self.interval)