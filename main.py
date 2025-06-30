import tkinter as tk
from core.tts_engine import TTSEngine
from core.audio_player import AudioPlayer
from core.clipboard import ClipboardMonitor
from ui.window import Window

def main():
    root = tk.Tk()
    
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    
    tts = TTSEngine()
    audio = AudioPlayer()
    
    def process_text(text):
        window.process_text(text)
    
    clipboard = ClipboardMonitor(process_text)
    window = Window(root, tts, audio, clipboard)
    
    root.protocol("WM_DELETE_WINDOW", window.on_closing)
    
    root.mainloop()

if __name__ == "__main__":
    main()