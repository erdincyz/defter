# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__date__ = '10/10/24'
__author__ = 'Erdinç Yılmaz'

from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QTextEdit,
                               QPushButton, QWidget, QSplitter, QCheckBox,
                               QListWidget, QLineEdit)
from PySide6.QtCore import QUrl, QByteArray, Qt, Slot, Signal, QSettings, QTimer
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
import json

from ..yw.yuzenWidget import YuzenWidget
from .ollamaServe import OllamaServerKontrol


#######################################################################
class YzYW(YuzenWidget):
    cevapHazir = Signal(str)

    # ---------------------------------------------------------------------
    def __init__(self, parent=None):
        super(YzYW, self).__init__(kapatilabilir_mi=False, parent=parent)
        self.yazBaslik(self.tr("AI Assistant"))

        # self.cevapTE.setStyleSheet(
        #     "QTextEdit { font-family: 'Segoe UI', sans-serif; font-size: 11pt; } code { font-family: 'Consolas', monospace; color: #d63384; }")

        self.settings = QSettings("Defter", "YZ_Modulu")
        self.nm = QNetworkAccessManager(self)

        # --- ZAMANLAYICI (POLLING) ---
        # Ollama sunucusu başlatılınca hazır olup olmadığını kontrol eder
        self.pollTimer = QTimer(self)
        self.pollTimer.timeout.connect(self.check_ollama_readiness)

        self.messages = []
        self.current_reply = None
        self.biriken_veri_buffer = b""
        self.gecici_cevap_metni = ""

        # --- ARKA PLANDA OLLAMA KONTROLCÜSÜ ---
        # Bu widget'ı oluşturuyoruz ama doğrudan eklemiyoruz.
        # İçindeki parçaları (Log ekranı, Label vb.) söküp kendi arayüzümüze takacağız.
        self.ollamaServerW = OllamaServerKontrol(self)
        self.ollamaServerW.hide()  # Ana widget gizli kalsın, parçalarını kullanacağız

        # ============================================================
        # ANA PANEL (temelW)
        # ============================================================
        temelW = QWidget(self)
        # Temel layout artık yok, her şeyi Splitter yönetecek

        # ------------------------------------------------------------
        # 1. BÖLÜM: SERVER LOG EKRANI (Üst Parça)
        # ------------------------------------------------------------
        # Log ekranını OllamaServerKontrol'den alıyoruz
        self.logTextEdit = self.ollamaServerW.text_output
        # Yeni bir container içine koyalım ki kenar boşluklarını yönetebilelim
        self.serverLogContainer = QWidget()
        logLay = QVBoxLayout(self.serverLogContainer)
        logLay.setContentsMargins(0, 0, 0, 0)
        logLay.addWidget(self.logTextEdit)

        # ------------------------------------------------------------
        # 2. BÖLÜM: CHAT ARAYÜZÜ (Alt Parça - Container)
        # ------------------------------------------------------------
        self.chatInterfaceContainer = QWidget()
        chatInterfaceLay = QVBoxLayout(self.chatInterfaceContainer)
        chatInterfaceLay.setContentsMargins(2, 2, 2, 2)
        chatInterfaceLay.setSpacing(5)

        # --- TOOLBAR (Provider, Start/Stop, Model) ---
        toolbarLay = QHBoxLayout()
        toolbarLay.setContentsMargins(0, 0, 0, 0)

        self.providerCB = QComboBox(self)
        self.providerCB.addItems(["Ollama (Local)", "Google Gemini (Cloud)"])
        self.providerCB.currentIndexChanged.connect(self.arayuz_guncelle)
        toolbarLay.addWidget(self.providerCB)

        # -- Google Widget --
        self.googleWidget = QWidget()
        googleLay = QHBoxLayout(self.googleWidget)
        googleLay.setContentsMargins(0, 0, 0, 0)
        self.apiKeyLE = QLineEdit(self)
        self.apiKeyLE.setPlaceholderText("Google API Key")
        self.apiKeyLE.setEchoMode(QLineEdit.EchoMode.Password)
        self.apiKeyLE.setText(self.settings.value("google_api_key", ""))
        self.apiKeyLE.textChanged.connect(lambda: self.settings.setValue("google_api_key", self.apiKeyLE.text()))
        googleLay.addWidget(self.apiKeyLE)
        toolbarLay.addWidget(self.googleWidget)

        # -- Ollama Widget --
        self.ollamaWidget = QWidget()
        ollamaLay = QHBoxLayout(self.ollamaWidget)
        ollamaLay.setContentsMargins(0, 0, 0, 0)

        self.btnToggleLog = QPushButton("📝", self)
        self.btnToggleLog.setToolTip("Toggle Server Log")
        self.btnToggleLog.setCheckable(True)
        self.btnToggleLog.setMaximumWidth(30)
        self.btnToggleLog.clicked.connect(self.act_toggle_log)

        self.btnStartOllama = QPushButton("▶", self)
        self.btnStartOllama.setToolTip("Start Ollama Server")
        self.btnStartOllama.setMaximumWidth(30)
        self.btnStartOllama.setStyleSheet("color: green; font-weight: bold;")
        self.btnStartOllama.clicked.connect(self.act_start_ollama_process)  # ÖZEL FONKSİYON

        self.btnStopOllama = QPushButton("⏹", self)
        self.btnStopOllama.setToolTip("Stop Ollama Server")
        self.btnStopOllama.setMaximumWidth(30)
        self.btnStopOllama.setStyleSheet("color: red; font-weight: bold;")
        self.btnStopOllama.clicked.connect(self.act_stop_ollama_process)  # ÖZEL FONKSİYON

        self.lblOllamaStatus = self.ollamaServerW.lblDurum
        self.lblOllamaStatus.setParent(self.ollamaWidget)

        ollamaLay.addWidget(self.btnToggleLog)
        ollamaLay.addWidget(self.btnStartOllama)
        ollamaLay.addWidget(self.btnStopOllama)
        ollamaLay.addWidget(self.lblOllamaStatus)

        toolbarLay.addWidget(self.ollamaWidget)

        toolbarLay.addStretch()
        toolbarLay.addWidget(QLabel("Model:"))
        self.modelCB = QComboBox(self)
        self.modelCB.setMinimumWidth(100)
        toolbarLay.addWidget(self.modelCB)

        self.btnYenile = QPushButton("⟳", self)
        self.btnYenile.setMaximumWidth(25)
        self.btnYenile.clicked.connect(self.act_model_listele)
        toolbarLay.addWidget(self.btnYenile)

        chatInterfaceLay.addLayout(toolbarLay)

        # --- CHAT SPLITTER (Çıktı / Girdi) ---
        self.chatSplitter = QSplitter(Qt.Orientation.Vertical, self)
        self.cevapTE = QTextEdit(self)
        self.cevapTE.setReadOnly(True)
        self.cevapTE.setPlaceholderText(self.tr("AI responses will appear here..."))

        self.input_text = QTextEdit(self)
        self.input_text.setPlaceholderText(self.tr("Type message... (Ctrl+Enter to send)"))

        self.chatSplitter.addWidget(self.cevapTE)
        self.chatSplitter.addWidget(self.input_text)
        self.chatSplitter.setStretchFactor(0, 4)
        self.chatSplitter.setStretchFactor(1, 1)
        chatInterfaceLay.addWidget(self.chatSplitter)

        # --- ALT KONTROLLER ---
        altLay = QHBoxLayout()
        self.systemPromptLE = QLineEdit(self)
        self.systemPromptLE.setPlaceholderText("System Prompt")
        self.systemPromptLE.setText(self.settings.value("system_prompt", ""))
        self.systemPromptLE.textChanged.connect(
            lambda: self.settings.setValue("system_prompt", self.systemPromptLE.text()))

        self.streamCB = QCheckBox("Stream", self)
        self.streamCB.setChecked(True)

        self.btnClearContext = QPushButton("🧹", self)
        self.btnClearContext.setToolTip("Clear History")
        self.btnClearContext.setMaximumWidth(30)
        self.btnClearContext.clicked.connect(self.act_gecmisi_temizle)

        self.btnGonder = QPushButton(self.tr("Send"), self)
        self.btnGonder.clicked.connect(self.act_gonder_tiklandi)

        altLay.addWidget(self.streamCB)
        altLay.addWidget(self.systemPromptLE, 1)
        altLay.addWidget(self.btnClearContext)
        altLay.addWidget(self.btnGonder)
        chatInterfaceLay.addLayout(altLay)

        # ============================================================
        # DİKEY SPLITTER (LOG EKRANI + CHAT ARAYÜZÜ)
        # ============================================================
        self.mainVerticalSplitter = QSplitter(Qt.Orientation.Vertical, self)
        self.mainVerticalSplitter.addWidget(self.serverLogContainer)
        self.mainVerticalSplitter.addWidget(self.chatInterfaceContainer)
        # Log başlangıçta kapalı (size=0)
        self.serverLogContainer.hide()

        # Temel Layout'a bu splitterı ekle
        anaVLayout = QVBoxLayout(temelW)
        anaVLayout.setContentsMargins(0, 0, 0, 0)
        anaVLayout.addWidget(self.mainVerticalSplitter)

        # ============================================================
        # YATAY SPLITTER (GEÇMİŞ + ANA PANEL)
        # ============================================================
        self.historyLW = QListWidget(self)
        self.historyLW.hide()  # İsteğe bağlı açılabilir

        self.anaSplitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.anaSplitter.addWidget(self.historyLW)
        self.anaSplitter.addWidget(temelW)
        self.anaSplitter.setStretchFactor(1, 1)

        self.ekleWidget(self.anaSplitter)

        # Başlangıç durumu ayarla
        self.arayuz_guncelle()

    # ---------------------------------------------------------------------
    def act_toggle_log(self, checked):
        # Splitter içindeki widget'ı gizleyip gösterir
        self.serverLogContainer.setVisible(checked)

    # ---------------------------------------------------------------------
    def act_start_ollama_process(self):
        """Sunucuyu başlatır ve kontrol mekanizmasını devreye sokar."""
        self.ollamaServerW.start_ollama_serve()

        # Görsel geri bildirim
        self.lblOllamaStatus.setText("Status: Starting...")
        self.lblOllamaStatus.setStyleSheet("color: orange; font-weight: bold;")

        # Eğer log kapalıysa açalım ki kullanıcı ne olduğunu görsün
        if not self.btnToggleLog.isChecked():
            self.btnToggleLog.setChecked(True)
            self.serverLogContainer.setVisible(True)

        # Timer'ı başlat: Her 2 saniyede bir kontrol et
        self.pollTimer.start(2000)

    # ---------------------------------------------------------------------
    def act_stop_ollama_process(self):
        """Sunucuyu durdurur ve timer'ı kapatır."""
        self.pollTimer.stop()
        self.ollamaServerW.stop_ollama_serve()
        # lblDurum güncellemelerini OllamaServerKontrol kendi içinde yapıyor ama
        # biz yine de emin olalım
        self.lblOllamaStatus.setText("Status: Stopped")
        self.lblOllamaStatus.setStyleSheet("color: red; font-weight: bold;")

    # ---------------------------------------------------------------------
    def check_ollama_readiness(self):
        """Timer tarafından çağrılır. Sunucu cevap verene kadar modelleri listelemeye çalışır."""
        # Provider Google ise timer'ı durdur
        if self.providerCB.currentText() == "Google Gemini (Cloud)":
            self.pollTimer.stop()
            return

        # Model listelemeyi dene (Sessizce)
        url = QUrl("http://localhost:11434/api/tags")
        request = QNetworkRequest(url)
        reply = self.nm.get(request)
        reply.finished.connect(self._on_readiness_check_finished)

    # ---------------------------------------------------------------------
    def _on_readiness_check_finished(self):
        reply = self.sender()
        if reply.error() == QNetworkReply.NetworkError.NoError:
            # BAŞARILI! Sunucu ayağa kalkmış.
            self.pollTimer.stop()  # Artık sormayı bırak

            self.lblOllamaStatus.setText("Status: Running")
            self.lblOllamaStatus.setStyleSheet("color: green; font-weight: bold;")
            self.ollamaServerW.text_output.append(
                "<br><b><span style='color:green'>Server is ready! Models listed below.</span></b><br>")

            # Modelleri combobox'a doldur
            try:
                data = json.loads(reply.readAll().data())
                self.modelCB.clear()
                models = [m["name"] for m in data.get("models", [])]
                self.modelCB.addItems(models)

                # Son seçileni geri yükle
                last = self.settings.value("last_model", "")
                idx = self.modelCB.findText(last)
                if idx >= 0: self.modelCB.setCurrentIndex(idx)
            except:
                pass

        else:
            # Hata varsa (henüz açılmadıysa) devam et, timer tekrar soracak.
            # Log ekranına sürekli hata basmayalım, sadece bekleyelim.
            pass

        reply.deleteLater()

    def keyPressEvent(self, event):
        if self.input_text.hasFocus() and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self.act_gonder_tiklandi()
                return
        super(YzYW, self).keyPressEvent(event)

    def closeEvent(self, event):
        self.pollTimer.stop()  # Timer'ı durdur
        if hasattr(self, 'ollamaServerW'):
            self.ollamaServerW.stop_ollama_serve()
        super(YzYW, self).closeEvent(event)

    def arayuz_guncelle(self):
        is_google = self.providerCB.currentText() == "Google Gemini (Cloud)"
        self.googleWidget.setVisible(is_google)
        self.ollamaWidget.setVisible(not is_google)

        if is_google:
            self.serverLogContainer.setVisible(False)
            self.btnToggleLog.setChecked(False)
            self.pollTimer.stop()

        self.modelCB.clear()
        if is_google:
            self.modelCB.addItems(["gemini-pro", "gemini-1.5-flash"])
        else:
            self.act_model_listele()

    def act_model_listele(self):
        if self.providerCB.currentText() == "Google Gemini (Cloud)": return
        # self.lblDurum yok artık, status label OllamaWidget içinde
        url = QUrl("http://localhost:11434/api/tags")
        request = QNetworkRequest(url)
        reply = self.nm.get(request)
        reply.finished.connect(self._on_model_list_finished)

    def _on_model_list_finished(self):
        reply = self.sender()
        if reply.error() == QNetworkReply.NetworkError.NoError:
            try:
                data = json.loads(reply.readAll().data())
                self.modelCB.clear()
                models = [m["name"] for m in data.get("models", [])]
                self.modelCB.addItems(models)
                last = self.settings.value("last_model", "")
                idx = self.modelCB.findText(last)
                if idx >= 0: self.modelCB.setCurrentIndex(idx)
            except:
                pass
        else:
            # Manuel yenilemede hata olursa kullanıcıya bildir
            if not self.pollTimer.isActive():
                self.lblOllamaStatus.setText("Unreachable")
                self.lblOllamaStatus.setStyleSheet("color: red;")
        reply.deleteLater()

    def act_gecmisi_temizle(self):
        self.messages = []
        self.cevapTE.clear()
        self.cevapTE.append(f"<i>{self.tr('Context cleared.')}</i>")

    @Slot()
    def act_gonder_tiklandi(self):
        prompt = self.input_text.toPlainText().strip()
        if not prompt: return

        # Kullanıcı mesajını ekle
        self.cevapTE.append(f"\n<b>User:</b> {prompt}")
        self.cevapTE.append(f"<b>AI ({self.modelCB.currentText()}):</b> ")

        # AI cevabının başlayacağı yeri kaydediyoruz.
        # QTextEdit'in sonuna git ve pozisyonu al.
        cursor = self.cevapTE.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.response_start_pos = cursor.position()

        self.input_text.clear()
        self.btnGonder.setEnabled(False)

        if self.providerCB.currentText() != "Google Gemini (Cloud)":
            self.settings.setValue("last_model", self.modelCB.currentText())

        if self.providerCB.currentText() == "Google Gemini (Cloud)":
            self._google_chat_request(prompt)
        else:
            self._ollama_chat_request(prompt)

    def disardan_prompt_gonder(self, prompt, system_prompt_override=None):
        self.show()
        self.buyult()
        self.input_text.setPlainText(prompt)
        if system_prompt_override:
            self.systemPromptLE.setText(system_prompt_override)
        self.act_gonder_tiklandi()

    # --- OLLAMA LOGIC ---
    def _ollama_chat_request(self, prompt):
        if not self.messages:
            sys_msg = self.systemPromptLE.text().strip()
            if sys_msg: self.messages.append({"role": "system", "content": sys_msg})

        self.messages.append({"role": "user", "content": prompt})
        url = QUrl("http://localhost:11434/api/chat")
        request = QNetworkRequest(url)
        request.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json")
        data = {"model": self.modelCB.currentText(), "messages": self.messages, "stream": self.streamCB.isChecked()}
        self.current_reply = self.nm.post(request, QByteArray(json.dumps(data).encode("utf-8")))
        self.gecici_cevap_metni = ""
        self.biriken_veri_buffer = b""
        if self.streamCB.isChecked():
            self.current_reply.readyRead.connect(self._on_ollama_stream_ready_read)
        self.current_reply.finished.connect(self._on_request_finished)

    def _on_ollama_stream_ready_read(self):
        if not self.current_reply: return
        self.biriken_veri_buffer += self.current_reply.readAll().data()
        try:
            while b'\n' in self.biriken_veri_buffer:
                line, self.biriken_veri_buffer = self.biriken_veri_buffer.split(b'\n', 1)
                if not line.strip(): continue
                response_obj = json.loads(line)
                if "message" in response_obj:
                    chunk = response_obj["message"].get("content", "")
                    self.gecici_cevap_metni += chunk
                    self._texte_ekle(chunk)
        except:
            pass

    # --- GOOGLE LOGIC ---
    def _google_chat_request(self, prompt):
        api_key = self.apiKeyLE.text().strip()
        if not api_key:
            self.cevapTE.append("<font color='red'>API Key missing!</font>")
            self.btnGonder.setEnabled(True)
            return

        # 1. Google Formatına Uygun Geçmiş Hazırla
        google_contents = []

        # Eğer sistem mesajı varsa (Google sistem mesajını ayrı parametre ister ama
        # basitlik için ilk user mesajı gibi davranabiliriz veya şimdilik atlayabiliriz)
        # Biz basitçe mevcut self.messages listesini Google formatına çevirelim:

        for msg in self.messages:
            role = "user" if msg["role"] == "user" else "model"
            # Sistem mesajını user gibi ekleyebiliriz ya da atlayabiliriz
            if msg["role"] == "system": continue

            google_contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })

        # 2. Şu anki mesajı ekle
        google_contents.append({
            "role": "user",
            "parts": [{"text": prompt}]
        })

        # Mesajı kendi yerel geçmişimize de ekleyelim (Ollama mantığıyla aynı kalsın)
        self.messages.append({"role": "user", "content": prompt})

        model = self.modelCB.currentText()
        url = QUrl(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?key={api_key}")

        request = QNetworkRequest(url)
        request.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json")

        # 3. Payload'ı güncelle
        payload = {"contents": google_contents}

        self.current_reply = self.nm.post(request, QByteArray(json.dumps(payload).encode("utf-8")))
        self.gecici_cevap_metni = ""

        self.current_reply.readyRead.connect(self._on_google_stream_ready_read)
        self.current_reply.finished.connect(self._on_request_finished)

    def _on_google_stream_ready_read(self):
        if not self.current_reply: return
        raw_data = self.current_reply.readAll().data()
        try:
            text_chunk = raw_data.decode("utf-8")
            import re
            matches = re.findall(r'"text":\s*"(.*?)"', text_chunk)
            for match in matches:
                clean_text = bytes(match, "utf-8").decode("unicode_escape")
                self.gecici_cevap_metni += clean_text
                self._texte_ekle(clean_text)
        except:
            pass

    # --- SHARED ---
    def _on_request_finished(self):
        reply = self.sender()

        if reply.error() != QNetworkReply.NetworkError.NoError:
            self.cevapTE.append(f"\n<font color='red'>Error: {reply.errorString()}</font>")
        else:
            # Eğer stream açıksa ve elimizde bir metin varsa
            if self.streamCB.isChecked() and self.gecici_cevap_metni:
                cursor = self.cevapTE.textCursor()

                # 1. Başlangıç pozisyonuna git
                cursor.setPosition(self.response_start_pos)

                # 2. Sona kadar (stream edilen ham metni) seç
                cursor.movePosition(cursor.MoveOperation.End, cursor.MoveMode.KeepAnchor)

                # 3. Seçili ham metni sil
                cursor.removeSelectedText()

                # 4. Aynı metni Markdown olarak formatlayıp ekle
                cursor.insertMarkdown(self.gecici_cevap_metni)

            self.cevapTE.append("\n" + "-" * 30 + "\n")

            if self.providerCB.currentText() != "Google Gemini (Cloud)":
                self.messages.append({"role": "assistant", "content": self.gecici_cevap_metni})

            self.cevapHazir.emit(self.gecici_cevap_metni)

        self.btnGonder.setEnabled(True)
        reply.deleteLater()
        self.current_reply = None
    # ---------------------------------------------------------------------
    def _texte_ekle(self, text):
        cursor = self.cevapTE.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.cevapTE.setTextCursor(cursor)
        self.cevapTE.insertPlainText(text)
        self.cevapTE.verticalScrollBar().setValue(self.cevapTE.verticalScrollBar().maximum())

    # ---------------------------------------------------------------------
    def force_server_shutdown(self):
        """
        Uygulama kapanırken ana pencereden çağrılır.
        Her şeyi durdurur ve sunucuyu öldürür.
        """
        # 1. Timer'ı durdur (Artık kontrol etme)
        if hasattr(self, 'pollTimer'):
            self.pollTimer.stop()

        # 2. Eğer sunucu kontrolcüsü varsa durdur
        if hasattr(self, 'ollamaServerW'):
            # Log ekranına yazmaya çalışmasın (çünkü widget yok ediliyor olabilir)
            # Bu yüzden direkt process'e erişip durdurmak daha güvenli olabilir
            # ama mevcut stop metodunuz güvenliyse onu çağıralım.
            self.ollamaServerW.stop_ollama_serve()
