import os
import time
from gradio_client import Client, handle_file
from pathlib import Path
from config.settings import API_URL, FIXED_OUTPUT_PATH, DEFAULT_SETTINGS

class TTSEngine:
    def __init__(self):
        self.client = Client(API_URL)
        self.reference_audio_path = None
        self.current_settings = DEFAULT_SETTINGS.copy()
        self.fixed_output_path = FIXED_OUTPUT_PATH
    
    def upload_reference_audio(self, file_path):
        self.reference_audio_path = file_path
        try:
            result = self.client.predict(
                api_name="/update_prompt_audio"
            )
            return True, "参考音频上传成功"
        except Exception as e:
            return False, f"上传参考音频失败: {str(e)}"
    
    def generate_speech(self, text, infer_mode):
        try:
            processed_text = self._clean_text(text)
            if not processed_text.strip():
                return False, "处理后的文本为空"
                
            result = self.client.predict(
                prompt=handle_file(self.reference_audio_path) if self.reference_audio_path else None,
                text=processed_text,
                infer_mode=infer_mode,
                max_text_tokens_per_sentence=self.current_settings["max_tokens"],
                sentences_bucket_max_size=self.current_settings["bucket_size"],
                param_5=self.current_settings["do_sample"],
                param_6=self.current_settings["top_p"],
                param_7=self.current_settings["top_k"],
                param_8=self.current_settings["temperature"],
                param_9=self.current_settings["length_penalty"],
                param_10=self.current_settings["num_beams"],
                param_11=self.current_settings["repetition_penalty"],
                param_12=self.current_settings["max_mel_tokens"],
                api_name="/gen_single" if self.reference_audio_path else "/on_input_text_change"
            )
            
            audio_filename = self._extract_filename(result)
            if audio_filename:
                full_path = os.path.join(self.fixed_output_path, audio_filename)
                return True, full_path
            return False, f"无法提取音频文件名: {result}"
            
        except Exception as e:
            return False, f"API调用错误: {str(e)}"
    
    def _clean_text(self, text):
        if text.startswith(('import ', 'def ', 'class ', 'from ', '//', '/*', '#')):
            return ""
        
        replacements = {'\n': '。', '\t': ' ', '  ': ' '}
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text[:500].strip()
    
    def _extract_filename(self, result):
        if isinstance(result, dict) and 'value' in result:
            value_str = result['value']
            if '.wav' in value_str:
                return value_str.split('\\')[-1]
        elif isinstance(result, (list, tuple)) and len(result) > 1:
            return os.path.basename(result[1] if self.reference_audio_path else result[0])
        return None
    
    def update_settings(self, new_settings):
        self.current_settings.update(new_settings)