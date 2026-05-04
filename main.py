import sys
import os
import requests
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit,
    QPushButton, QTextEdit, QHBoxLayout, QFileDialog, QLabel, 
    QProgressBar, QDialog, QDoubleSpinBox, QSpinBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from llama_cpp import Llama

DARK_STYLE = """
    QWidget {
        background-color: #121212;
        font-family: 'Segoe UI', Arial, sans-serif;
        color: #e0e0e0;
        outline: none;
    }

    QDialog {
        background-color: #121212;
    }

    QTextEdit, QLineEdit, QDoubleSpinBox, QSpinBox {
        background-color: #2a2a2a; 
        border: 1px solid #3d3d3d;
        border-radius: 6px;
        padding: 8px;
        color: #ffffff;
        selection-background-color: #0573e1;
    }

    QAbstractSpinBox::up-button, QAbstractSpinBox::down-button {
        background: transparent;
        border: none;
    }

    QPushButton {
        background-color: #333333;
        color: #ffffff;
        border: 1px solid #444444;
        border-radius: 6px;
        padding: 9px 100px; 
        font-weight: bold;
    }

    QPushButton:hover {
        background-color: #444444;
        border: 1px solid #0573e1;
    }

    QLabel { 
        color: #ffffff;
        font-size: 13px;
        margin-bottom: 2px;
    }
"""

MODEL_FILENAME = "qwen2.5-1.5b-instruct.gguf"
DEFAULT_MODEL_URL = "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf"

class SettingsDialog(QDialog):
    def __init__(self, current_settings):
        super().__init__()
        self.setWindowTitle("Model Configuration")
        self.setFixedSize(400, 480)
        self.setStyleSheet(DARK_STYLE)
        self.settings = current_settings
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("System Prompt:"))
        self.sys_prompt_input = QTextEdit()
        self.sys_prompt_input.setPlainText(self.settings['system_prompt'])
        self.sys_prompt_input.setMaximumHeight(100)
        layout.addWidget(self.sys_prompt_input)

        layout.addWidget(QLabel("Temperature (Creativity):"))
        self.temp_spin = QDoubleSpinBox()
        self.temp_spin.setRange(0.1, 1.5)
        self.temp_spin.setSingleStep(0.1)
        self.temp_spin.setValue(self.settings['temperature'])
        layout.addWidget(self.temp_spin)

        layout.addWidget(QLabel("Repeat Penalty:"))
        self.penalty_spin = QDoubleSpinBox()
        self.penalty_spin.setRange(1.0, 2.0)
        self.penalty_spin.setSingleStep(0.1)
        self.penalty_spin.setValue(self.settings['penalty'])
        layout.addWidget(self.penalty_spin)

        layout.addWidget(QLabel("Max Response Tokens:"))
        self.tokens_spin = QSpinBox()
        self.tokens_spin.setRange(32, 2048)
        self.tokens_spin.setValue(self.settings['max_tokens'])
        layout.addWidget(self.tokens_spin)

        btn_save = QPushButton("Apply")
        btn_save.clicked.connect(self.save_and_close)
        layout.addStretch()
        layout.addWidget(btn_save, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

    def save_and_close(self):
        self.settings['system_prompt'] = self.sys_prompt_input.toPlainText()
        self.settings['temperature'] = self.temp_spin.value()
        self.settings['penalty'] = self.penalty_spin.value()
        self.settings['max_tokens'] = self.tokens_spin.value()
        self.accept()

class DownloadThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)

    def run(self):
        try:
            with requests.get(DEFAULT_MODEL_URL, stream=True) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                downloaded = 0
                with open(MODEL_FILENAME, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size:
                            self.progress.emit(int((downloaded / total_size) * 100))
            self.finished.emit(MODEL_FILENAME)
        except Exception as e:
            self.finished.emit(f"Error: {e}")

class Chat(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple LLM Chat Offline - Local Chat")
        self.setGeometry(100, 100, 700, 700)
        self.setStyleSheet(DARK_STYLE)

        self.llm = None
        self.last_context = ""
        self.config = {
            'system_prompt': "Assistant running on software maintained by Bryan Apolonio",
            'temperature': 0.3,
            'penalty': 1.1,
            'max_tokens': 400
        }

        self.init_ui()
        self.check_existing_model()

    def init_ui(self):
        layout = QVBoxLayout()
        header_layout = QHBoxLayout()
        self.lbl_status = QLabel("Ready.")
        
        self.btn_action = QPushButton("Check Model")
        self.btn_action.clicked.connect(self.handle_model_action)
        
        self.btn_settings = QPushButton("Settings")
        self.btn_settings.clicked.connect(self.open_settings)

        btn_browse = QPushButton("Browse GGUF")
        btn_browse.clicked.connect(self.browse_model)

        header_layout.addWidget(self.lbl_status)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_action)
        header_layout.addWidget(btn_browse)
        header_layout.addWidget(self.btn_settings)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message...")
        self.input_field.returnPressed.connect(self.send_query)
        
        btn_send = QPushButton("Send")
        btn_send.setMinimumWidth(100) 
        btn_send.clicked.connect(self.send_query)

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(btn_send)

        layout.addLayout(header_layout)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.chat_display)
        layout.addLayout(input_layout)
        self.setLayout(layout)

    def check_existing_model(self):
        if os.path.exists(MODEL_FILENAME):
            self.btn_action.setText("Start Model")
            self.lbl_status.setText("Local model detected.")
        else:
            self.btn_action.setText("Download Qwen 1.5B")

    def open_settings(self):
        dialog = SettingsDialog(self.config)
        if dialog.exec():
            self.chat_display.append("<i>System: Settings updated successfully.</i>")

    def handle_model_action(self):
        if os.path.exists(MODEL_FILENAME):
            self.setup_llm(MODEL_FILENAME)
        else:
            self.start_download()

    def browse_model(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select GGUF", str(Path.home()), "GGUF (*.gguf)")
        if file_path:
            self.setup_llm(file_path)

    def start_download(self):
        self.btn_action.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.dl_thread = DownloadThread()
        self.dl_thread.progress.connect(self.progress_bar.setValue)
        self.dl_thread.finished.connect(self.on_download_complete)
        self.dl_thread.start()

    def on_download_complete(self, path):
        self.progress_bar.setVisible(False)
        self.btn_action.setEnabled(True)
        if "Error" not in path:
            self.check_existing_model()
            self.setup_llm(path)

    def setup_llm(self, path):
        try:
            self.chat_display.append(f"<i>System: Initializing {os.path.basename(path)}...</i>")
            QApplication.processEvents()
            self.llm = Llama(model_path=path, n_ctx=2048, n_threads=4, verbose=False)
            self.lbl_status.setText(f"Active: {os.path.basename(path)}")
            self.chat_display.append("<b>System:</b> Model is online.\n")
        except Exception as e:
            self.chat_display.append(f"<b>Error:</b> {str(e)}")

    def send_query(self):
        text = self.input_field.text().strip()
        
        if not text:
            return

        if not self.llm:
            self.chat_display.append("<b style='color: #ff4444;'>System:</b> Please start or download the model before chatting!")
            self.input_field.clear()
            return
            
        self.input_field.clear()
        self.chat_display.append(f"<b style='color: #0573e1;'>You:</b> {text}")
        self.chat_display.append("<b style='color: #00ff7f;'>AI:</b> ")
        self.scroll_to_bottom()

        prompt = f"System: {self.config['system_prompt']}\n{self.last_context}User: {text}\nAI:"
        
        try:
            stream = self.llm(
                prompt=prompt,
                max_tokens=self.config['max_tokens'],
                temperature=self.config['temperature'],
                repeat_penalty=self.config['penalty'],
                stream=True,
                stop=["User:", "System:"]
            )

            full_response = ""
            for output in stream:
                token = output['choices'][0]['text']
                full_response += token
                cursor = self.chat_display.textCursor()
                cursor.movePosition(cursor.MoveOperation.End)
                cursor.insertText(token)
                self.scroll_to_bottom()
                QApplication.processEvents()
            
            full_response = full_response.strip()
            self.last_context = f"User: {text}\nAI: {full_response}\n"
            self.chat_display.append("") 
            
        except Exception as e:
            self.chat_display.append(f"\n<b>System Error:</b> {str(e)}")

    def scroll_to_bottom(self):
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Chat()
    window.show()
    sys.exit(app.exec())
