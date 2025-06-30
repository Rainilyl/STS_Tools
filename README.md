# STS_Tools

![工具界面](Example.PNG)  
*语音转文本转语音工具界面*

## 📖 项目概述
**STS_Tools** 是一个正在开发中的多功能语音处理工具。

graph LR
    %% 输入层（粉紫）
    A[多模态输入源] --> B[统一文本提取]
    A1[🎤 语音输入] --> B
    A2[📹 视频音频] --> B
    A3[🖥️ OCR屏幕] --> B
    A4[📝 会议记录] --> B

    %% 处理层（橙色）
    B --> C[文本标准化处理]
    C --> D[TTS推理引擎]
    
    %% TTS引擎池（浅粉）
    D --> D1[IndexTTS]
    D --> D2[自定义TTS API]
    D --> D3[其他引擎]

    %% 统一输出（浅橙）
    D1 --> E[音频输出系统]
    D2 --> E
    D3 --> E
    E --> E1[🔊 实时播放]
    E --> E2[💾 保存音频]

    %% 配色方案
    classDef input fill:#ffccff,stroke:#333;
    classDef process fill:#ff9966,stroke:#333;
    classDef tts fill:#ffccff,stroke:#333;
    classDef output fill:#ffcc99,stroke:#333;
    class A,A1,A2,A3,A4 input;
    class B,C process;
    class D,D1,D2,D3 tts;
    class E,E1,E2 output;

- **用途**:
  - 语音转录与转换
  - 会议记录自动化
  - 无障碍辅助工具开发

- **核心功能**:
  ✅ 已实现:
  - 语音转文本(STT)
  - 通过IndexTTS实现的文本转语音(TTS)
  
  🔜 规划中:
  - 屏幕OCR文字输入
  - 会议音频自动处理
  - 多TTS引擎支持

## 🚀 快速开始

### 环境要求
- Python 3.8+
- 音频输入设备
- 音频输出设备

### 运行步骤
```bash
git clone https://github.com/your-repo/STS_Tools.git
cd STS_Tools
pip install -r requirements.txt
启动indextts
python main.py
