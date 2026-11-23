"""Camera discovery and OpenCV camera opening helpers."""
from __future__ import annotations

from typing import Optional

import cv2

from config import CAMERA_BACKENDS, CAMERA_SCAN_RANGE


class CameraManager:
    """Utility class for probing and opening local cameras."""

    @staticmethod
    def _backend_id(backend_name: str) -> int:
        backend_map = {
            "DSHOW": cv2.CAP_DSHOW,
            "MSMF": cv2.CAP_MSMF,
            "ANY": cv2.CAP_ANY,
        }
        return backend_map.get(backend_name, cv2.CAP_ANY)

    @classmethod
    def open_camera(cls, camera_index: int) -> tuple[Optional[cv2.VideoCapture], str]:
        """Try Windows backends in order and return an opened capture."""
        errors = []
        for backend_name in CAMERA_BACKENDS:
            cap = None
            try:
                cap = cv2.VideoCapture(int(camera_index), cls._backend_id(backend_name))
                if cap is not None and cap.isOpened():
                    # Check that the backend can actually deliver a frame before
                    # accepting it; some drivers report isOpened() but return no data.
                    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    ok, _test_frame = cap.read()
                    if ok:
                        return cap, backend_name
                errors.append(backend_name)
            except Exception:
                errors.append(backend_name)
            if cap is not None:
                cap.release()
        return None, ", ".join(errors) or "No backend available"

    @classmethod
    def list_available_cameras(cls) -> list[dict[str, int | str]]:
        """Probe camera indexes; release every temporary VideoCapture."""
        found: list[dict[str, int | str]] = []
        for index in CAMERA_SCAN_RANGE:
            cap, backend = cls.open_camera(index)
            if cap is None:
                continue
            try:
                # Opening is not enough: some drivers report opened but cannot read.
                ok, _frame = cap.read()
                if ok:
                    found.append({"index": index, "name": f"Camera {index}", "backend": backend})
            finally:
                cap.release()
        return found
