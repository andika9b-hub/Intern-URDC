"""YOLOv8 custom-model loading, class mapping, and frame annotation."""
from __future__ import annotations

from pathlib import Path
import re
from typing import Any

import cv2
import torch
from ultralytics import YOLO

from config import (
    CLASS_NAME_MAP,
    GREEN_CLASS_ALIASES,
    MODEL_PATH,
    RED_CLASS_ALIASES,
)


class BuoyDetector:
    """Loads a local Ultralytics .pt model and runs inference on frames."""

    RED_BGR = (45, 55, 235)
    GREEN_BGR = (55, 205, 105)
    OTHER_BGR = (225, 180, 70)

    def __init__(self, model_path: str | Path = MODEL_PATH) -> None:
        self.model_path = Path(model_path)
        if not self.model_path.is_file():
            raise FileNotFoundError(
                f"Model tidak ditemukan: {self.model_path}\n"
                "Letakkan file hasil training Roboflow bernama best.pt di folder weights."
            )

        self.device = 0 if torch.cuda.is_available() else "cpu"
        self.device_label = (
            f"GPU: {torch.cuda.get_device_name(0)}" if torch.cuda.is_available() else "CPU"
        )
        self.model = YOLO(str(self.model_path))
        self.class_names = self._read_class_names(self.model.names)

    @staticmethod
    def _read_class_names(names: Any) -> dict[int, str]:
        if isinstance(names, dict):
            return {int(key): str(value) for key, value in names.items()}
        if isinstance(names, (list, tuple)):
            return {index: str(value) for index, value in enumerate(names)}
        return {}

    @staticmethod
    def _normalise_name(name: str) -> str:
        value = name.strip().lower().replace("_", " ").replace("-", " ")
        return re.sub(r"\s+", " ", value)

    @classmethod
    def _resolve_kind(cls, class_name: str) -> str:
        """Map a model class to red/green using config overrides then aliases."""
        normalised = cls._normalise_name(class_name)
        explicit_map = {
            cls._normalise_name(str(key)): str(value).strip().lower()
            for key, value in CLASS_NAME_MAP.items()
        }
        mapped = explicit_map.get(normalised)
        if mapped in ("red", "green"):
            return mapped

        red_aliases = {cls._normalise_name(value) for value in RED_CLASS_ALIASES}
        green_aliases = {cls._normalise_name(value) for value in GREEN_CLASS_ALIASES}
        if normalised in red_aliases:
            return "red"
        if normalised in green_aliases:
            return "green"
        return "other"

    def detect(
        self,
        frame,
        confidence: float = 0.45,
        image_size: int = 640,
    ) -> tuple[Any, dict[str, Any]]:
        """Return an annotated BGR frame and current-frame detection statistics."""
        results = self.model.predict(
            source=frame,
            conf=float(confidence),
            imgsz=int(image_size),
            device=self.device,
            verbose=False,
        )

        annotated = frame.copy()
        red_count = 0
        green_count = 0
        total_count = 0
        labels: list[str] = []

        if results:
            boxes = results[0].boxes
            if boxes is not None:
                for box in boxes:
                    class_id = int(box.cls[0].item())
                    confidence_value = float(box.conf[0].item())
                    class_name = self.class_names.get(class_id, f"class_{class_id}")
                    kind = self._resolve_kind(class_name)
                    xyxy = box.xyxy[0].tolist()
                    x1, y1, x2, y2 = [int(value) for value in xyxy]

                    if kind == "red":
                        color = self.RED_BGR
                        red_count += 1
                    elif kind == "green":
                        color = self.GREEN_BGR
                        green_count += 1
                    else:
                        color = self.OTHER_BGR

                    total_count += 1
                    label = f"{class_name}  {confidence_value * 100:.1f}%"
                    labels.append(class_name)
                    cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)

                    # Draw a filled label background while keeping it inside the frame.
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    font_scale = 0.58
                    thickness = 2
                    (text_w, text_h), baseline = cv2.getTextSize(label, font, font_scale, thickness)
                    label_top = max(0, y1 - text_h - baseline - 8)
                    cv2.rectangle(
                        annotated,
                        (x1, label_top),
                        (min(annotated.shape[1] - 1, x1 + text_w + 10), y1),
                        color,
                        -1,
                    )
                    cv2.putText(
                        annotated,
                        label,
                        (x1 + 5, max(text_h + 2, y1 - baseline - 5)),
                        font,
                        font_scale,
                        (255, 255, 255),
                        thickness,
                        cv2.LINE_AA,
                    )

        stats = {
            "red": red_count,
            "green": green_count,
            "total": total_count,
            "classes": labels,
            "device": self.device_label,
        }
        return annotated, stats
