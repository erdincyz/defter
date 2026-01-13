import os
import re
import platform
from PySide6.QtWidgets import (
    QVBoxLayout, QPushButton, QTextEdit, QWidget, QHBoxLayout, QLabel
)
from PySide6.QtCore import QProcess

ANSI_ESCAPE = re.compile(r'(?:\x1B[@-_][0-?]*[ -/]*[@-~])')

ANSI_TO_HTML_COLOR = {
    30: 'black', 31: 'red', 32: 'green', 33: '#d4d400',  # yellow
    34: 'blue', 35: 'magenta', 36: 'cyan', 37: 'white',
    90: 'gray', 91: 'red', 92: 'green', 93: 'yellow',
    94: 'blue', 95: 'magenta', 96: 'cyan', 97: 'white'
}


def ansi_to_html(text):
    """
    Terminalden gelen ANSI renk kodlarını HTML formatına çevirir.
    """

    def replace_ansi(match):
        ansi_code = match.group(0)
        # Renk kodlarını yakala (Örn: \x1B[31m)
        color_match = re.search(r'\x1B\[(\d+);?(\d+)?m', ansi_code)
        if color_match:
            color_code = int(color_match.group(1))
            html_color = ANSI_TO_HTML_COLOR.get(color_code, None)
            if html_color:
                return f'<span style="color:{html_color};">'
            elif ansi_code == '\x1B[0m':  # Reset
                return '</span>'
        return ''

    # HTML taglerini escape et (XSS veya format bozulmasını önlemek için)
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # Satır sonlarını <br> yap
    text = text.replace("\n", "<br>")

    # ANSI kodlarını HTML span'lerine çevir
    html_text = ANSI_ESCAPE.sub(replace_ansi, text)
    return html_text


class OllamaServerKontrol(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Başlık ve Durum
        header_layout = QHBoxLayout()
        self.lblDurum = QLabel("Status: Stopped", self)
        self.lblDurum.setStyleSheet("color: red; font-weight: bold;")
        header_layout.addWidget(self.lblDurum)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Terminal Çıktı Alanı
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        self.text_output.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4; font-family: Consolas, Monospace;")
        layout.addWidget(self.text_output)

        # Butonlar
        btn_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Server")
        self.start_button.clicked.connect(self.start_ollama_serve)
        self.start_button.setStyleSheet("background-color: #2da44e; color: white;")

        self.stop_button = QPushButton("Stop Server")
        self.stop_button.clicked.connect(self.stop_ollama_serve)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("background-color: #cf222e; color: white;")

        btn_layout.addWidget(self.start_button)
        btn_layout.addWidget(self.stop_button)
        layout.addLayout(btn_layout)

        # QProcess Ayarları
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)

    def __del__(self):
        """Nesne silinirken (Garbage Collection) çalışır."""
        try:
            if hasattr(self, 'process') and self.process.state() != QProcess.ProcessState.NotRunning:
                self.process.kill()  # Beklemeden öldür
        except:
            pass

    # ---------------------------------------------------------------------
    def start_ollama_serve(self):
        """Ollama sunucusunu başlatır."""
        self.text_output.clear()
        self.text_output.append("<b>Attempting to start 'ollama serve'...</b><br>")

        # Ortam Değişkenleri
        env = self.process.processEnvironment()
        # Renkli çıktı için zorla
        env.insert("FORCE_COLOR", "1")
        # Ollama'nın host ayarı (Gerekirse değiştirilebilir)
        env.insert("OLLAMA_HOST", "127.0.0.1:11434")

        # Kullanıcı ev dizini (Linux/Mac için önemli olabilir)
        home_dir = os.path.expanduser("~")
        env.insert("HOME", home_dir)

        self.process.setProcessEnvironment(env)

        # Platform Kontrolü
        if platform.system() == "Windows":
            # Windows'ta script komutu yoktur, direkt çalıştırılır
            program = "ollama"
            arguments = ["serve"]
        else:
            # Linux/Mac için 'script' komutu TTY emülasyonu sağlar (renkler için iyidir)
            # Ancak 'script' bazen sorun çıkarabilir, direkt çalıştırmak daha güvenlidir.
            # Şimdilik direkt çalıştırıyoruz, FORCE_COLOR genellikle yeterlidir.
            program = "ollama"
            arguments = ["serve"]

            # Eğer mutlaka 'script' kullanmak isterseniz:
            # program = "script"
            # arguments = ["-q", "/dev/null", "-c", "ollama serve"]

        self.process.start(program, arguments)

        self.lblDurum.setText("Status: Starting...")
        self.lblDurum.setStyleSheet("color: orange; font-weight: bold;")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    # ---------------------------------------------------------------------
    def stop_ollama_serve(self):
        """Sunucuyu durdurur."""
        if self.process.state() == QProcess.ProcessState.Running:
            self.text_output.append("<br><b>Stopping server...</b><br>")
            self.process.terminate()

            # 2 saniye bekle, kapanmazsa zorla kapat
            if not self.process.waitForFinished(2000):
                self.process.kill()

    # ---------------------------------------------------------------------
    def handle_stdout(self):
        """Standart çıktıyı okur."""
        data = self.process.readAllStandardOutput()
        # 'replace' karakter hatası almamak için
        text = data.data().decode("utf-8", errors="replace")
        html = ansi_to_html(text)

        # Cursor'ı sona taşı
        cursor = self.text_output.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.text_output.setTextCursor(cursor)

        self.text_output.insertHtml(html)
        self.text_output.ensureCursorVisible()

    # ---------------------------------------------------------------------
    def handle_stderr(self):
        """Hata çıktısını okur."""
        data = self.process.readAllStandardError()
        text = data.data().decode("utf-8", errors="replace")
        html = ansi_to_html(text)

        self.text_output.append(f"<span style='color:orange;'>{html}</span>")

    # ---------------------------------------------------------------------
    def process_finished(self):
        """İşlem bittiğinde tetiklenir."""
        self.lblDurum.setText("Status: Stopped")
        self.lblDurum.setStyleSheet("color: red; font-weight: bold;")
        self.text_output.append("<br><b>Server stopped.</b><br>")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    # ---------------------------------------------------------------------
    def closeEvent(self, event):
        """Widget kapanırken sunucuyu da kapat."""
        self.stop_ollama_serve()
        super().closeEvent(event)