import sounddevice as sd
import soundfile as sf
import queue
import threading
import numpy as np
import os

class AudioPlayer:
    def __init__(self):
        self.audio_queue = queue.Queue()
        self.output_device = None
        self.stream = None
        self.is_running = False
        self.playback_thread = None
    
    def start(self):
        self.is_running = True
        self.playback_thread = threading.Thread(
            target=self._playback_worker,
            daemon=True
        )
        self.playback_thread.start()
    
    def stop(self):
        self.is_running = False
        if self.stream:
            self.stream.stop()
            self.stream = None
        self.audio_queue.put((None, None))
    
    def set_output_device(self, device_id):
        self.output_device = device_id
    
    def play_file(self, file_path):
        try:
            data, sr = sf.read(file_path)
            if len(data.shape) > 1:
                data = data[:, 0]
            self.audio_queue.put((data.astype('float32'), sr))
            return True, f"播放: {os.path.basename(file_path)}"
        except Exception as e:
            return False, f"音频加载失败: {str(e)}"
    
    def _playback_worker(self):
        while self.is_running:
            try:
                data, sr = self.audio_queue.get()
                if data is None:
                    break
                
                if self.stream is None or self.stream.samplerate != sr:
                    if self.stream:
                        self.stream.stop()
                    self.stream = sd.OutputStream(
                        device=self.output_device,
                        channels=1,
                        samplerate=sr,
                        dtype='float32',
                        blocksize=1024,
                        latency='low'
                    )
                    self.stream.start()
                
                self.stream.write(data)
            except Exception:
                continue