"""Background QThread for camera capture and YOLO inference."""
from __future__ import annotations

import threading
import time

import cv2
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage

from camera_manager import CameraManager
from config import DEFAULT_CONFIDENCE, DEFAULT_IMAGE_SIZE
from detector import BuoyDetector


class DetectionWorker(QThread):
    frame_ready = Signal(QImage)
    stats_updated = Signal(object)
    model_status = Signal(bool, str)
    camera_status = Signal(str)
    error_occurred = Signal(str)

    def __init__(
        self,
        camera_index: int,
        confidence: float = DEFAULT_CONFIDENCE,
        image_size: int = DEFAULT_IMAGE_SIZE,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.camera_index = int(camera_index)
        self._confidence = float(confidence)
        self._image_size = int(image_size)
        self._settings_lock = threading.Lock()
        self._frame_lock = threading.Lock()
        self._latest_frame = None
        self._stop_event = threading.Event()
        self.last_error = ""

    def stop(self) -> None:
        self._stop_event.set()

    def update_settings(self, confidence: float, image_size: int) -> None:
        with self._settings_lock:
            self._confidence = float(confidence)
            self._image_size = int(image_size)

    def get_latest_frame(self):
        with self._frame_lock:
            return self._latest_frame.copy() if self._latest_frame is not None else None

    def _get_settings(self) -> tuple[float, int]:
        with self._settings_lock:
            return self._confidence, self._image_size

    def run(self) -> None:
        capture = None
        try:
            capture, backend = CameraManager.open_camera(self.camera_index)
            if capture is None:
                message = (
                    f"Kamera indeks {self.camera_index} gagal dibuka. "
                    "Periksa koneksi, izin kamera, atau tutup aplikasi lain yang memakai kamera."
                )
                self.last_error = message
                self.error_occurred.emit(message)
                return

            capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            self.camera_status.emit(f"CAMERA {self.camera_index} CONNECTED · {backend}")

            detector = None
            try:
                detector = BuoyDetector()
                class_summary = ", ".join(detector.class_names.values()) or "No class names"
                self.model_status.emit(
                    True,
                    f"LOADED · {detector.model_path.name} · {detector.device_label}\nClasses: {class_summary}",
                )
            except Exception as exc:
                # Keep preview usable even if the custom model is absent or invalid.
                self.model_status.emit(False, f"MODEL ERROR · {exc}")

            previous_time = time.perf_counter()
            smoothed_fps = 0.0

            while not self._stop_event.is_set():
                ok, frame = capture.read()
                if not ok or frame is None:
                    message = "Kamera terhubung, tetapi frame gagal dibaca. Periksa kabel atau driver kamera."
                    self.last_error = message
                    self.error_occurred.emit(message)
                    break

                if detector is not None:
                    confidence, image_size = self._get_settings()
                    processed_frame, stats = detector.detect(frame, confidence, image_size)
                else:
                    processed_frame = frame
                    stats = {"red": 0, "green": 0, "total": 0, "classes": [], "device": "Unavailable"}

                current_time = time.perf_counter()
                instantaneous_fps = 1.0 / max(current_time - previous_time, 1e-6)
                previous_time = current_time
                smoothed_fps = instantaneous_fps if smoothed_fps == 0 else (0.82 * smoothed_fps + 0.18 * instantaneous_fps)
                stats["fps"] = smoothed_fps
                stats["model_loaded"] = detector is not None

                with self._frame_lock:
                    self._latest_frame = processed_frame.copy()

                height, width = processed_frame.shape[:2]
                rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                image = QImage(
                    rgb_frame.data,
                    width,
                    height,
                    int(rgb_frame.strides[0]),
                    QImage.Format.Format_RGB888,
                ).copy()
                self.frame_ready.emit(image)
                self.stats_updated.emit(stats)

        except Exception as exc:
            self.last_error = f"Kesalahan proses kamera/deteksi: {exc}"
            self.error_occurred.emit(self.last_error)
        finally:
            if capture is not None:
                capture.release()
            self.camera_status.emit("CAMERA STOPPED")
