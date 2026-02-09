import cv2
from ultralytics import YOLO
import os
from config import MODEL_PATH, CONFIDENCE_THRESHOLD, CLASS_NAMES

class TrafficLightDetector:
    def __init__(self, logger):
        self.logger = logger
        self.model = None
        self.load_model()

    def load_model(self):
        """Load the YOLO model with validation."""
        if os.path.exists(MODEL_PATH):
            try:
                self.model = YOLO(MODEL_PATH)
                if hasattr(self.model, 'names') and len(self.model.names) >= 4:
                    self.logger.info("Model loaded successfully.")
                else:
                    self.model = None
                    self.logger.error("Model validation failed: insufficient classes.")
            except Exception as e:
                self.model = None
                self.logger.error(f"Model loading failed: {e}")
        else:
            self.logger.error(f"Model file '{MODEL_PATH}' not found.")

    def detect_traffic_lights(self, frame):
        """Run detection on a frame and return detections."""
        if self.model is None:
            return []

        try:
            results = self.model(frame, conf=CONFIDENCE_THRESHOLD)
        except Exception as e:
            self.logger.error(f"Inference error: {e}")
            return []

        detections = []
        if results:
            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = box.conf[0].cpu().numpy()
                    cls = int(box.cls[0].cpu().numpy())
                    color_name = CLASS_NAMES.get(cls, f'Unknown ({cls})')
                    detections.append({
                        'color': color_name,
                        'confidence': conf,
                        'bbox': (x1, y1, x2, y2)
                    })
        return detections
