import cv2
import numpy as np

class TrafficLightDetector:
    def __init__(self, logger):
        self.logger = logger

    def detect_traffic_lights(self, frame):
        """Simple color-based detection for traffic lights."""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Define color ranges for red, green, yellow
        red_lower1 = np.array([0, 50, 50])
        red_upper1 = np.array([10, 255, 255])
        red_lower2 = np.array([160, 50, 50])
        red_upper2 = np.array([180, 255, 255])

        green_lower = np.array([40, 50, 50])
        green_upper = np.array([80, 255, 255])

        yellow_lower = np.array([20, 50, 50])
        yellow_upper = np.array([40, 255, 255])

        # Create masks
        mask_red1 = cv2.inRange(hsv, red_lower1, red_upper1)
        mask_red2 = cv2.inRange(hsv, red_lower2, red_upper2)
        mask_red = cv2.bitwise_or(mask_red1, mask_red2)

        mask_green = cv2.inRange(hsv, green_lower, green_upper)
        mask_yellow = cv2.inRange(hsv, yellow_lower, yellow_upper)

        detections = []

        # Find contours for red
        contours_red, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours_red:
            area = cv2.contourArea(cnt)
            if area > 100:  # Minimum area
                x, y, w, h = cv2.boundingRect(cnt)
                detections.append({
                    'color': 'Red',
                    'confidence': 0.8,
                    'bbox': (x, y, x+w, y+h)
                })

        # Find contours for green
        contours_green, _ = cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours_green:
            area = cv2.contourArea(cnt)
            if area > 100:
                x, y, w, h = cv2.boundingRect(cnt)
                detections.append({
                    'color': 'Green',
                    'confidence': 0.8,
                    'bbox': (x, y, x+w, y+h)
                })

        # Find contours for yellow
        contours_yellow, _ = cv2.findContours(mask_yellow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours_yellow:
            area = cv2.contourArea(cnt)
            if area > 100:
                x, y, w, h = cv2.boundingRect(cnt)
                detections.append({
                    'color': 'Yellow',
                    'confidence': 0.8,
                    'bbox': (x, y, x+w, y+h)
                })

        return detections
