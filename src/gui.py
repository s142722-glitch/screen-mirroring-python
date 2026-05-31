"""
PyQt6 GUI — control panel for the AirPlay receiver.

Provides start/stop controls, status display, and a log viewer.
Video rendering is handled by UxPlay+GStreamer in its own window;
this GUI is the management dashboard.
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox, QGroupBox,
    QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QFont

from .mdns_service import AirPlayMDNSService
from .uxplay_manager import UxPlayManager


class LogSignal(QObject):
    message = pyqtSignal(str)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AirPlay Receiver")
        self.setMinimumSize(560, 420)

        self._mdns: AirPlayMDNSService | None = None
        self._uxplay: UxPlayManager | None = None
        self._running = False
        self._log_signal = LogSignal()
        self._log_signal.message.connect(self._append_log)

        self._build_ui()

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)

        # --- Settings group ---
        settings_box = QGroupBox("Settings")
        settings_layout = QVBoxLayout(settings_box)

        name_row = QHBoxLayout()
        name_row.addWidget(QLabel("Device Name:"))
        self._name_input = QLineEdit("PC-AirPlay")
        name_row.addWidget(self._name_input)
        settings_layout.addLayout(name_row)

        res_row = QHBoxLayout()
        res_row.addWidget(QLabel("Resolution:"))
        self._res_combo = QComboBox()
        self._res_combo.addItems(["1920x1080", "1280x720", "3840x2160"])
        res_row.addWidget(self._res_combo)
        settings_layout.addLayout(res_row)

        layout.addWidget(settings_box)

        # --- Controls ---
        btn_row = QHBoxLayout()
        self._start_btn = QPushButton("Start Receiver")
        self._start_btn.setFixedHeight(40)
        self._start_btn.clicked.connect(self._toggle)
        btn_row.addWidget(self._start_btn)
        layout.addLayout(btn_row)

        # --- Status ---
        self._status_label = QLabel("Status: Stopped")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(11)
        self._status_label.setFont(font)
        layout.addWidget(self._status_label)

        # --- Log ---
        log_box = QGroupBox("Log")
        log_layout = QVBoxLayout(log_box)
        self._log_view = QTextEdit()
        self._log_view.setReadOnly(True)
        self._log_view.setFont(QFont("Consolas", 9))
        log_layout.addWidget(self._log_view)
        layout.addWidget(log_box)

    def _append_log(self, text: str):
        self._log_view.append(text)

    def _log(self, text: str):
        self._log_signal.message.emit(text)

    def _toggle(self):
        if self._running:
            self._stop()
        else:
            self._start()

    def _start(self):
        name = self._name_input.text().strip() or "PC-AirPlay"
        resolution = self._res_combo.currentText()

        self._mdns = AirPlayMDNSService(name=name)
        try:
            ip = self._mdns.start()
        except Exception as e:
            QMessageBox.critical(self, "mDNS Error", str(e))
            return

        self._log(f"mDNS broadcasting '{name}' on {ip}")

        self._uxplay = UxPlayManager(
            name=name,
            resolution=resolution,
            on_log=self._log,
        )
        try:
            self._uxplay.start()
        except FileNotFoundError as e:
            self._log(f"WARNING: {e}")
            self._log("Running in mDNS-only mode (iPad will see this PC but mirroring requires UxPlay).")

        self._running = True
        self._start_btn.setText("Stop Receiver")
        self._status_label.setText(f"Status: Running — {name} on {ip}")
        self._name_input.setEnabled(False)
        self._res_combo.setEnabled(False)

    def _stop(self):
        if self._uxplay:
            self._uxplay.stop()
            self._uxplay = None
        if self._mdns:
            self._mdns.stop()
            self._mdns = None

        self._running = False
        self._start_btn.setText("Start Receiver")
        self._status_label.setText("Status: Stopped")
        self._name_input.setEnabled(True)
        self._res_combo.setEnabled(True)
        self._log("Receiver stopped.")

    def closeEvent(self, event):
        self._stop()
        event.accept()


def run_gui():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
