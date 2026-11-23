"""PySide6 desktop interface for the Buoy Detection System."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import cv2
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QCloseEvent, QPixmap, QImage
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from camera_manager import CameraManager
from config import (
    AVAILABLE_IMAGE_SIZES,
    CAPTURES_DIR,
    DEFAULT_CONFIDENCE,
    DEFAULT_IMAGE_SIZE,
    MODEL_PATH,
)
from worker import DetectionWorker


APP_STYLE = """
QWidget { background-color: #071321; color: #e8f0f8; font-family: 'Segoe UI'; font-size: 10pt; }
QFrame#header { background: #0b1d31; border: 1px solid #1b3855; border-radius: 14px; }
QFrame#panel { background: #0c1d2e; border: 1px solid #1a3550; border-radius: 14px; }
QFrame#videoPanel { background: #050d16; border: 1px solid #1b3a56; border-radius: 14px; }
QLabel#appTitle { color: #f4f8fc; font-size: 19pt; font-weight: 800; letter-spacing: 1px; }
QLabel#subtitle { color: #91a9c0; font-size: 9pt; }
QLabel#sectionTitle { color: #84a7c7; font-size: 9pt; font-weight: 700; letter-spacing: 1px; }
QLabel#fieldLabel { color: #a9bfd3; font-size: 9pt; font-weight: 600; }
QLabel#statusPill { background: #183a55; color: #80d7ff; border-radius: 9px; padding: 7px 13px; font-weight: 800; }
QLabel#statusPill[state='running'] { background: #123e34; color: #63e6ae; }
QLabel#statusPill[state='error'] { background: #4b2029; color: #ff8793; }
QLabel#videoPlaceholder { color: #6e879e; font-size: 15pt; font-weight: 700; background: transparent; }
QLabel#metricCard { background: #10263a; border: 1px solid #20415f; border-radius: 12px; padding: 12px; }
QLabel#metricLabel { color: #8ea8bf; font-size: 8pt; font-weight: 700; letter-spacing: 1px; }
QLabel#metricValue { color: #f1f7fc; font-size: 22pt; font-weight: 800; }
QLabel#redValue { color: #ff6675; font-size: 22pt; font-weight: 800; }
QLabel#greenValue { color: #5de3a1; font-size: 22pt; font-weight: 800; }
QLabel#smallInfo { color: #8ea8bf; font-size: 8pt; }
QComboBox { background: #071625; border: 1px solid #294966; border-radius: 8px; padding: 9px; min-height: 20px; }
QComboBox:hover { border-color: #3d83b4; }
QComboBox QAbstractItemView { background: #10263a; selection-background-color: #1d5276; color: #e8f0f8; }
QPushButton { background: #153d5e; color: #f4f8fc; border: 1px solid #2b638d; border-radius: 9px; padding: 10px 12px; font-weight: 700; }
QPushButton:hover { background: #1b527b; }
QPushButton:disabled { color: #60758a; background: #162536; border-color: #243648; }
QPushButton#startButton { background: #137a5a; border-color: #23a77e; }
QPushButton#startButton:hover { background: #18936b; }
QPushButton#stopButton { background: #682d38; border-color: #9b4656; }
QPushButton#stopButton:hover { background: #833b49; }
QPushButton#captureButton { background: #25486a; border-color: #467eaa; }
QSlider::groove:horizontal { height: 6px; background: #1b354c; border-radius: 3px; }
QSlider::handle:horizontal { background: #49b6e8; width: 16px; margin: -5px 0; border-radius: 8px; }
QListWidget { background: #071625; border: 1px solid #1c3a54; border-radius: 8px; padding: 5px; color: #b8c9d8; }
QListWidget::item { padding: 5px; border-bottom: 1px solid #162c40; }
QFrame#footer { background: #091a29; border: 1px solid #18344d; border-radius: 9px; }
QLabel#footerText { color: #7f9ab2; font-size: 8pt; }
"""


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Buoy Detection System")
        self.setMinimumSize(QSize(1120, 720))
        self.resize(1480, 900)
        self.setStyleSheet(APP_STYLE)

        self.worker: DetectionWorker | None = None
        self.pending_camera_index: int | None = None
        self.closing = False
        self.refreshing_cameras = False
        self.last_image: QImage | None = None
        self.last_counts = (0, 0, 0)
        self.last_error = ""

        self._build_interface()
        self._refresh_model_path_status()
        self.refresh_cameras()

    def _build_interface(self) -> None:
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(18, 16, 18, 14)
        root_layout.setSpacing(12)

        # Header
        header = QFrame(objectName="header")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 13, 20, 13)
        title_box = QVBoxLayout()
        title = QLabel("BUOY DETECTION SYSTEM", objectName="appTitle")
        subtitle = QLabel("REAL-TIME OBJECT DETECTION USING YOLOv8", objectName="subtitle")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header_layout.addLayout(title_box)
        header_layout.addStretch(1)
        self.system_status = QLabel("READY", objectName="statusPill")
        self.system_status.setProperty("state", "ready")
        header_layout.addWidget(self.system_status, 0, Qt.AlignmentFlag.AlignVCenter)
        root_layout.addWidget(header)

        body = QHBoxLayout()
        body.setSpacing(12)

        # Sidebar controls
        sidebar = QFrame(objectName="panel")
        sidebar.setFixedWidth(270)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(16, 16, 16, 16)
        side.setSpacing(10)

        side.addWidget(QLabel("CAMERA CONTROL", objectName="sectionTitle"))
        side.addWidget(QLabel("Select camera", objectName="fieldLabel"))
        self.camera_combo = QComboBox()
        self.camera_combo.currentIndexChanged.connect(self._on_camera_changed)
        side.addWidget(self.camera_combo)
        self.refresh_button = QPushButton("↻  Refresh Camera")
        self.refresh_button.clicked.connect(self.refresh_cameras)
        side.addWidget(self.refresh_button)
        self.camera_info = QLabel("Camera: not selected", objectName="smallInfo")
        self.camera_info.setWordWrap(True)
        side.addWidget(self.camera_info)

        self._add_separator(side)
        side.addWidget(QLabel("DETECTION SETTINGS", objectName="sectionTitle"))
        conf_row = QHBoxLayout()
        conf_row.addWidget(QLabel("Confidence threshold", objectName="fieldLabel"))
        conf_row.addStretch(1)
        self.confidence_value = QLabel(f"{int(DEFAULT_CONFIDENCE * 100)}%")
        self.confidence_value.setStyleSheet("color: #5cc8f2; font-weight: 800;")
        conf_row.addWidget(self.confidence_value)
        side.addLayout(conf_row)
        self.confidence_slider = QSlider(Qt.Orientation.Horizontal)
        self.confidence_slider.setRange(10, 95)
        self.confidence_slider.setValue(int(DEFAULT_CONFIDENCE * 100))
        self.confidence_slider.valueChanged.connect(self._on_confidence_changed)
        side.addWidget(self.confidence_slider)
        side.addWidget(QLabel("Model input size", objectName="fieldLabel"))
        self.image_size_combo = QComboBox()
        for size in AVAILABLE_IMAGE_SIZES:
            self.image_size_combo.addItem(f"{size} × {size}", size)
        default_index = self.image_size_combo.findData(DEFAULT_IMAGE_SIZE)
        self.image_size_combo.setCurrentIndex(max(0, default_index))
        self.image_size_combo.currentIndexChanged.connect(self._on_settings_changed)
        side.addWidget(self.image_size_combo)

        self._add_separator(side)
        side.addWidget(QLabel("MODEL INFORMATION", objectName="sectionTitle"))
        self.model_status_label = QLabel("MODEL: NOT LOADED", objectName="smallInfo")
        self.model_status_label.setWordWrap(True)
        side.addWidget(self.model_status_label)
        self.model_path_label = QLabel(f"Weights: {MODEL_PATH.name}", objectName="smallInfo")
        self.model_path_label.setWordWrap(True)
        side.addWidget(self.model_path_label)

        self._add_separator(side)
        side.addWidget(QLabel("SYSTEM ACTIONS", objectName="sectionTitle"))
        self.start_button = QPushButton("▶  Start Detection", objectName="startButton")
        self.start_button.clicked.connect(self.start_detection)
        side.addWidget(self.start_button)
        self.stop_button = QPushButton("■  Stop Detection", objectName="stopButton")
        self.stop_button.clicked.connect(self.stop_detection)
        self.stop_button.setEnabled(False)
        side.addWidget(self.stop_button)
        self.capture_button = QPushButton("◎  Capture Image", objectName="captureButton")
        self.capture_button.clicked.connect(self.capture_image)
        self.capture_button.setEnabled(False)
        side.addWidget(self.capture_button)
        side.addStretch(1)
        side.addWidget(QLabel("LOCAL INFERENCE · YOLO / OPENCV", objectName="smallInfo"))
        body.addWidget(sidebar)

        # Main display
        center = QVBoxLayout()
        center.setSpacing(10)
        video_panel = QFrame(objectName="videoPanel")
        video_layout = QVBoxLayout(video_panel)
        video_layout.setContentsMargins(8, 8, 8, 8)
        self.video_label = QLabel("NO CAMERA CONNECTED", objectName="videoPlaceholder")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setMinimumSize(480, 360)
        self.video_label.setStyleSheet("background: #050d16; border-radius: 9px;")
        video_layout.addWidget(self.video_label, 1)
        center.addWidget(video_panel, 1)

        # Bottom metric cards
        metrics = QHBoxLayout()
        metrics.setSpacing(10)
        self.red_metric = self._metric_card("RED BUOY", "0", "redValue")
        self.green_metric = self._metric_card("GREEN BUOY", "0", "greenValue")
        self.total_metric = self._metric_card("TOTAL OBJECTS", "0", "metricValue")
        self.fps_metric = self._metric_card("FPS", "0.0", "metricValue")
        for card in (self.red_metric, self.green_metric, self.total_metric, self.fps_metric):
            metrics.addWidget(card, 1)
        center.addLayout(metrics)
        body.addLayout(center, 1)

        # Right panel: detection log / quick status
        right_panel = QFrame(objectName="panel")
        right_panel.setFixedWidth(220)
        right = QVBoxLayout(right_panel)
        right.setContentsMargins(14, 16, 14, 14)
        right.setSpacing(10)
        right.addWidget(QLabel("DETECTION SUMMARY", objectName="sectionTitle"))
        self.summary_label = QLabel("Waiting for camera frames", objectName="smallInfo")
        self.summary_label.setWordWrap(True)
        right.addWidget(self.summary_label)
        self._add_separator(right)
        right.addWidget(QLabel("EVENT LOG", objectName="sectionTitle"))
        self.event_log = QListWidget()
        self.event_log.setMinimumHeight(180)
        right.addWidget(self.event_log, 1)
        self._add_separator(right)
        right.addWidget(QLabel("PROCESSING DEVICE", objectName="sectionTitle"))
        self.device_label = QLabel("Not detected", objectName="smallInfo")
        self.device_label.setWordWrap(True)
        right.addWidget(self.device_label)
        body.addWidget(right_panel)

        root_layout.addLayout(body, 1)

        # Footer
        footer = QFrame(objectName="footer")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(12, 8, 12, 8)
        self.footer_camera = QLabel("CAMERA: DISCONNECTED", objectName="footerText")
        self.footer_model = QLabel("MODEL: CHECKING", objectName="footerText")
        footer_local = QLabel("● RUNNING LOCALLY · NO CLOUD STREAMING", objectName="footerText")
        footer_layout.addWidget(self.footer_camera)
        footer_layout.addStretch(1)
        footer_layout.addWidget(self.footer_model)
        footer_layout.addStretch(1)
        footer_layout.addWidget(footer_local)
        root_layout.addWidget(footer)

        self.setCentralWidget(root)

    @staticmethod
    def _add_separator(layout) -> None:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #203b53; background: #203b53; max-height: 1px;")
        layout.addWidget(line)

    @staticmethod
    def _metric_card(title: str, value: str, value_object_name: str) -> QFrame:
        card = QFrame(objectName="metricCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(2)
        label = QLabel(title, objectName="metricLabel")
        number = QLabel(value, objectName=value_object_name)
        number.setProperty("metricValue", True)
        layout.addWidget(label)
        layout.addWidget(number)
        card.value_label = number
        return card

    def _refresh_model_path_status(self) -> None:
        if MODEL_PATH.is_file():
            self.model_path_label.setText(f"Weights found: {MODEL_PATH.name}")
            self.model_status_label.setText("MODEL: READY TO LOAD")
            self.footer_model.setText("MODEL: FILE FOUND")
        else:
            self.model_path_label.setText(f"Missing: {MODEL_PATH}")
            self.model_status_label.setText("MODEL: best.pt belum ditemukan. Preview kamera tetap bisa digunakan.")
            self.footer_model.setText("MODEL: FILE NOT FOUND")

    def refresh_cameras(self) -> None:
        self.refreshing_cameras = True
        previous_value = self.camera_combo.currentData()
        self.camera_combo.clear()
        self.camera_info.setText("Scanning camera indexes 0–5...")
        self.refresh_button.setEnabled(False)
        try:
            cameras = CameraManager.list_available_cameras()
            if cameras:
                for camera in cameras:
                    self.camera_combo.addItem(
                        f"{camera['name']}  ·  {camera['backend']}",
                        int(camera["index"]),
                    )
                previous_index = self.camera_combo.findData(previous_value)
                if previous_index >= 0:
                    self.camera_combo.setCurrentIndex(previous_index)
                self.camera_info.setText(f"{len(cameras)} camera(s) detected")
            else:
                self.camera_combo.addItem("No camera detected", None)
                self.camera_info.setText("No camera found. Connect a webcam and refresh.")
                self.video_label.setText("NO CAMERA CONNECTED")
                self.video_label.setPixmap(QPixmap())
        except Exception as exc:
            self.camera_combo.addItem("Camera scan failed", None)
            self.camera_info.setText(f"Camera scan error: {exc}")
        finally:
            self.refresh_button.setEnabled(True)
            self.refreshing_cameras = False

    def _on_camera_changed(self, _index: int) -> None:
        if self.refreshing_cameras:
            return
        camera_index = self.camera_combo.currentData()
        if camera_index is None:
            return
        self.camera_info.setText(f"Selected camera index: {camera_index}")
        if self.worker is not None and self.worker.isRunning():
            self.pending_camera_index = int(camera_index)
            self.worker.stop()
            self.system_status.setText("SWITCHING CAMERA")
            self.system_status.setProperty("state", "ready")
            self._repolish_status()

    def _on_confidence_changed(self, value: int) -> None:
        self.confidence_value.setText(f"{value}%")
        self._on_settings_changed()

    def _on_settings_changed(self, *_args) -> None:
        if self.worker is not None and self.worker.isRunning():
            self.worker.update_settings(
                self.confidence_slider.value() / 100.0,
                int(self.image_size_combo.currentData()),
            )

    def start_detection(self) -> None:
        camera_index = self.camera_combo.currentData()
        if camera_index is None:
            QMessageBox.warning(
                self,
                "Camera not found",
                "Tidak ada kamera yang terdeteksi. Hubungkan kamera lalu klik Refresh Camera.",
            )
            return
        if self.worker is not None and self.worker.isRunning():
            return
        self._start_worker(int(camera_index))

    def _start_worker(self, camera_index: int) -> None:
        if self.closing:
            return
        if self.worker is not None:
            if self.worker.isRunning():
                return
            self.worker.deleteLater()
            self.worker = None

        self.last_error = ""
        self.last_counts = (0, 0, 0)
        self._set_metrics(0, 0, 0, 0.0)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.capture_button.setEnabled(False)
        self.system_status.setText("STARTING")
        self.system_status.setProperty("state", "ready")
        self._repolish_status()
        self.footer_camera.setText(f"CAMERA: OPENING INDEX {camera_index}")
        self.worker = DetectionWorker(
            camera_index=camera_index,
            confidence=self.confidence_slider.value() / 100.0,
            image_size=int(self.image_size_combo.currentData()),
        )
        self.worker.frame_ready.connect(self._on_frame_ready)
        self.worker.stats_updated.connect(self._on_stats_updated)
        self.worker.model_status.connect(self._on_model_status)
        self.worker.camera_status.connect(self._on_camera_status)
        self.worker.error_occurred.connect(self._on_worker_error)
        self.worker.finished.connect(self._on_worker_finished)
        self.worker.start()

    def stop_detection(self) -> None:
        self.pending_camera_index = None
        if self.worker is not None and self.worker.isRunning():
            self.worker.stop()
            self.stop_button.setEnabled(False)
            self.system_status.setText("STOPPING")
            self.system_status.setProperty("state", "ready")
            self._repolish_status()
        else:
            self._set_idle_state()

    def _on_frame_ready(self, image: QImage) -> None:
        self.last_image = image
        pixmap = QPixmap.fromImage(image)
        self.video_label.setPixmap(
            pixmap.scaled(
                self.video_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        self.capture_button.setEnabled(True)

    def _on_stats_updated(self, stats: dict) -> None:
        red = int(stats.get("red", 0))
        green = int(stats.get("green", 0))
        total = int(stats.get("total", 0))
        fps = float(stats.get("fps", 0.0))
        self._set_metrics(red, green, total, fps)
        self.summary_label.setText(
            f"Current frame\nRed buoy: {red}\nGreen buoy: {green}\nAll objects: {total}"
        )
        device = stats.get("device", "Unavailable")
        self.device_label.setText(str(device))

        new_counts = (red, green, total)
        if new_counts != self.last_counts and total > 0:
            timestamp = datetime.now().strftime("%H:%M:%S")
            classes = ", ".join(stats.get("classes", []))
            self.event_log.insertItem(0, f"{timestamp}  R:{red}  G:{green}  T:{total}\n{classes}")
            while self.event_log.count() > 8:
                self.event_log.takeItem(self.event_log.count() - 1)
        self.last_counts = new_counts

    def _set_metrics(self, red: int, green: int, total: int, fps: float) -> None:
        self.red_metric.value_label.setText(str(red))
        self.green_metric.value_label.setText(str(green))
        self.total_metric.value_label.setText(str(total))
        self.fps_metric.value_label.setText(f"{fps:.1f}")

    def _on_model_status(self, loaded: bool, message: str) -> None:
        self.model_status_label.setText(message)
        self.footer_model.setText("MODEL: LOADED" if loaded else "MODEL: ERROR / MISSING")

    def _on_camera_status(self, message: str) -> None:
        self.footer_camera.setText(message)
        if "CONNECTED" in message and "STOPPED" not in message:
            self.system_status.setText("RUNNING")
            self.system_status.setProperty("state", "running")
            self._repolish_status()

    def _on_worker_error(self, message: str) -> None:
        self.last_error = message
        self.system_status.setText("ERROR")
        self.system_status.setProperty("state", "error")
        self._repolish_status()
        self.summary_label.setText(message)

    def _on_worker_finished(self) -> None:
        finished_worker = self.worker
        self.worker = None
        if finished_worker is not None:
            finished_worker.deleteLater()

        if self.closing:
            return
        if self.pending_camera_index is not None:
            next_index = self.pending_camera_index
            self.pending_camera_index = None
            self._start_worker(next_index)
            return

        if self.last_error:
            self.system_status.setText("ERROR")
            self.system_status.setProperty("state", "error")
        else:
            self._set_idle_state()
        self._repolish_status()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.capture_button.setEnabled(False)

    def _set_idle_state(self) -> None:
        self.system_status.setText("READY")
        self.system_status.setProperty("state", "ready")
        self.footer_camera.setText("CAMERA: DISCONNECTED")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.capture_button.setEnabled(False)

    def _repolish_status(self) -> None:
        self.system_status.style().unpolish(self.system_status)
        self.system_status.style().polish(self.system_status)

    def capture_image(self) -> None:
        if self.worker is None:
            QMessageBox.information(self, "Capture", "Belum ada frame kamera untuk disimpan.")
            return
        frame = self.worker.get_latest_frame()
        if frame is None:
            QMessageBox.information(self, "Capture", "Frame kamera belum tersedia.")
            return
        CAPTURES_DIR.mkdir(parents=True, exist_ok=True)
        filename = f"buoy_capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        output_path = CAPTURES_DIR / filename
        if cv2.imwrite(str(output_path), frame):
            self.summary_label.setText(f"Capture saved:\n{output_path.name}")
            self.event_log.insertItem(0, f"{datetime.now().strftime('%H:%M:%S')}  CAPTURE SAVED\n{filename}")
        else:
            QMessageBox.critical(self, "Capture failed", "OpenCV gagal menyimpan gambar capture.")

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self.last_image is not None:
            self.video_label.setPixmap(
                QPixmap.fromImage(self.last_image).scaled(
                    self.video_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )

    def closeEvent(self, event: QCloseEvent) -> None:
        self.closing = True
        self.pending_camera_index = None
        if self.worker is not None and self.worker.isRunning():
            self.worker.stop()
            # Wait until the current inference call returns and the camera is
            # released; destroying a running QThread can terminate the process.
            self.worker.wait()
        event.accept()
