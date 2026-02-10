import cv2
import numpy as np
from ultralytics import YOLO
from config import MODEL_PATH, CONFIDENCE_THRESHOLD, CLASS_NAMES

class TrafficLightDetector:
    def __init__(self, logger):
        self.logger = logger
        self.conf_threshold = CONFIDENCE_THRESHOLD
        self.class_names = CLASS_NAMES
        try:
            self.model = YOLO(MODEL_PATH)
            self.logger.info(f"Model loaded successfully from {MODEL_PATH}")
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            self.model = None

    def detect_traffic_lights(self, frame):
        """Detect traffic lights using YOLO model."""
        if self.model is None:
            self.logger.error("Model not loaded, cannot perform detection")
            return []

        try:
            # Run inference
            results = self.model(frame, conf=CONFIDENCE_THRESHOLD)

            detections = []
            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = box.conf[0].cpu().numpy()
                    cls = int(box.cls[0].cpu().numpy())

                    # Map class to color name
                    color = CLASS_NAMES.get(cls, f'class_{cls}')

                    detections.append({
                        'color': color,
                        'confidence': float(conf),
                        'bbox': (float(x1), float(y1), float(x2), float(y2))
                    })

            return detections
        except Exception as e:
            self.logger.error(f"Error during detection: {e}")
            return []
