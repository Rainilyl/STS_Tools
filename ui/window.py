import tkinter as tk
from tkinter import ttk, filedialog
import sounddevice as sd
from pathlib import Path
import time
import os
import sys
from config.settings import DEFAULT_SETTINGS

class Window:
    def __init__(self, root, tts_engine, audio_player, clipboard_monitor):
        self.root = root
        self.root.title("STS Tools")
        
        self._set_window_icon()
        
        self.tts = tts_engine
        self.audio = audio_player
        self.clipboard = clipboard_monitor
        
        self.is_running = False
        self._setup_ui()
        self._setup_devices()
        self.audio.start()
    
    def _set_window_icon(self):

        try:

            def get_resource_path(relative_path):

                try:
                    base_path = sys._MEIPASS
                except AttributeError:
                    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                return os.path.join(base_path, relative_path)
            
            icon_path = get_resource_path(os.path.join('ico', 'SST_Tools.ico'))
            
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
                print(f"成功加载图标: {icon_path}")
            else:
                print(f"图标文件不存在: {icon_path}")
        except Exception as e:
            print(f"加载图标时出错: {str(e)}")

    def _setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        ttk.Label(control_frame, text="输出设备:").pack(anchor=tk.W)
        self.device_combobox = ttk.Combobox(control_frame, state="readonly", width=30)
        self.device_combobox.pack(fill=tk.X, pady=(0,10))
        
        ttk.Button(control_frame, text="上传参考音频", command=self._upload_audio).pack(fill=tk.X)
        self.audio_label = ttk.Label(control_frame, text="未选择参考音频", foreground="gray")
        self.audio_label.pack(fill=tk.X, pady=(0,10))
        
        ttk.Label(control_frame, text="推理模式:").pack(anchor=tk.W)
        self.infer_mode = tk.StringVar(value=DEFAULT_SETTINGS["infer_mode"])
        ttk.Radiobutton(control_frame, text="普通推理", variable=self.infer_mode, value="普通推理").pack(anchor=tk.W)
        ttk.Radiobutton(control_frame, text="批次推理", variable=self.infer_mode, value="批次推理").pack(anchor=tk.W)
        
        ttk.Button(control_frame, text="高级参数设置", command=self._show_settings).pack(fill=tk.X, pady=(10,0))
        
        self.status_label = ttk.Label(control_frame, text="状态: 停止", foreground="red")
        self.status_label.pack(fill=tk.X, pady=(10,0))
        
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X, pady=(10,0))
        self.start_btn = ttk.Button(btn_frame, text="开始推理", command=self.start)
        self.start_btn.pack(side=tk.LEFT, expand=True)
        self.stop_btn = ttk.Button(btn_frame, text="停止推理", command=self.stop, state="disabled")
        self.stop_btn.pack(side=tk.LEFT, expand=True)
        
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        ttk.Label(log_frame, text="运行日志:").pack(anchor=tk.W)
        self.log = tk.Text(log_frame, height=20, state="disabled")
        self.log.pack(fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(log_frame, command=self.log.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log['yscrollcommand'] = scrollbar.set
    
    def _setup_devices(self):
        devices = sd.query_devices()
        self.device_combobox['values'] = [
            f"{i}: {d['name']}" 
            for i, d in enumerate(devices) 
            if d['max_output_channels'] > 0
        ]
    
    def _upload_audio(self):
        path = filedialog.askopenfilename(
            filetypes=[("音频文件", "*.wav *.mp3 *.ogg *.flac")]
        )
        if path:
            success, msg = self.tts.upload_reference_audio(path)
            self._log(msg)
            if success:
                self.audio_label.config(
                    text=f"已选择: {Path(path).name}",
                    foreground="green"
                )
    
    def _show_settings(self):
        settings_win = tk.Toplevel(self.root)
        settings_win.title("高级参数设置")
        
        ttk.Label(settings_win, text="分句最大Token数:").grid(row=0, column=0)
        slider = ttk.Scale(
            settings_win, 
            from_=10, 
            to=200, 
            value=self.tts.current_settings["max_tokens"]
        )
        slider.grid(row=0, column=1)
        var = tk.IntVar(value=self.tts.current_settings["max_tokens"])
        ttk.Label(settings_win, textvariable=var).grid(row=0, column=2)
        slider.config(command=lambda v: var.set(int(float(v))))
        
        ttk.Button(
            settings_win,
            text="保存",
            command=lambda: self._save_settings(settings_win, {"max_tokens": var.get()})
        ).grid(row=1, column=0, columnspan=3)
    
    def _save_settings(self, window, settings):
        self.tts.update_settings(settings)
        window.destroy()
        self._log("参数设置已保存")
    
    def _log(self, message):
        self.log.config(state="normal")
        self.log.insert("end", f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.log.see("end")
        self.log.config(state="disabled")
    
    def start(self):
        if not self.device_combobox.get():
            self._log("请选择输出设备")
            return
        
        device_id = int(self.device_combobox.get().split(":")[0])
        self.audio.set_output_device(device_id)
        
        self.is_running = True
        self.status_label.config(text="状态: 运行中", foreground="green")
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        
        self.clipboard.start()
        self._log("开始监视剪贴板...")
    
    def stop(self):
        self.is_running = False
        self.clipboard.stop()
        self.status_label.config(text="状态: 停止", foreground="red")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self._log("停止监视剪贴板")
    
    def process_text(self, text):
        self._log(f"检测到新文本: {text[:50]}...")
        success, result = self.tts.generate_speech(text, self.infer_mode.get())
        if success:
            self._log(f"生成音频: {result}")
            play_success, msg = self.audio.play_file(result)
            if not play_success:
                self._log(msg)
        else:
            self._log(result)
    
    def on_closing(self):
        self.stop()
        self.audio.stop()
        self.root.destroy()