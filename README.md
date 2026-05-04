# Simple-LLM-Chat-Offline
A high-performance local LLM interface powered by `llama-cpp-python` and `PyQt6`, designed for private, offline intelligence.

<p align="center">
  <img src="./img/start.png" width="48%" />
  <img src="./img/settings.png" width="48%" />
</p>
<p align="center">
  <img src="./img/memory.png" width="48%" />
  <img src="./img/chat.png" width="48%" />
</p>

## Overview
**Simple-LLM-Chat-Offline** is a minimalist desktop client for Large Language Models (LLMs). It allows users to run models like Qwen 2.5 locally without relying on external APIs. The software focuses on speed, privacy, and a clean, terminal-inspired interface.

The application features an automated model downloader and a dynamic parameter injection system, ensuring a seamless experience from setup to inference.

## Features
- **Local Inference:** 100% offline. Your data never leaves your machine.
- **Context Persistence:** Maintains a conversation history buffer, allowing the model to remember previous interactions within the session.
- **Automated Setup:** Built-in downloader for the Qwen 2.5 1.5B (GGUF) optimized model.
- **Real-time Streaming:** Smooth token-by-token text generation using PyQt6 signals for a responsive UI.
- **Advanced Config:** Fine-tune temperature, repeat penalty, and system prompts on the fly.
- **GGUF Support:** Compatible with any GGUF model via the internal file browser.

## Prerequisites
To run this project on your local machine, you need:

* **Python 3.10+**
* **Hardware:** 4GB+ RAM (8GB recommended for larger models).
* **C++ Compiler:** Required for building `llama-cpp-python` (Visual Studio tools on Windows or `gcc` on Linux).

## Installation

### Windows
```powershell
git clone https://github.com/BryanApolonio/Simple-LLM-Chat-Offline.git
cd Simple-LLM-Chat-Offline
pip install -r requirements.txt --break-system-packages
```

### Ubuntu/Debian
```bash
sudo apt install python3-pip python3-pyqt6 git -y
git clone https://github.com/BryanApolonio/Simple-LLM-Chat-Offline.git
cd Simple-LLM-Chat-Offline
pip install -r requirements.txt --break-system-packages
```

### macOS (Apple Silicon)
```bash
git clone https://github.com/BryanApolonio/Simple-LLM-Chat-Offline.git
cd Simple-LLM-Chat-Offline
CMAKE_ARGS="-DGGML_METAL=on" pip install llama-cpp-python --break-system-packages
pip install PyQt6 requests --break-system-packages
```

## Getting Started

1. **Run the application:**
```bash
python3 main.py
```

2. **Model Initialization:**
Click on **"Download Qwen 1.5B"** or use the **"Browse GGUF"** button to load a model you already have.

## Project Structure

```text 
├── main.py                 # Core Application Logic & UI (PyQt6)
├── requirements.txt        # Project Dependencies
├── LICENSE                 # MIT License
├── README.md               # Documentation
└── img/                    # UI Screenshots
```

## Configuration

Through the **Settings** menu, you can adjust:
- **System Prompt:** Define the AI's personality and constraints.
- **Temperature:** Control creativity (Lower is more analytical, higher is more creative).
- **Max Tokens:** Limit the length of the generated responses.

## Credits & Technologies

This project is built upon the hard work of the open-source AI community:
- **[llama-cpp-python](https://github.com/abetlen/llama-cpp-python):** Python bindings for `llama.cpp`.
- **[Qwen 2.5](https://huggingface.co/Qwen):** Powerful low-parameter models for efficient local use.
- **[PyQt6](https://riverbankcomputing.com/software/pyqt/):** Professional-grade GUI framework.

**Disclaimer:** This tool is for educational and research purposes. Ensure you have the rights to the models you download and use them according to their respective licenses.
