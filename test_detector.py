"""
Test script for TrafficLightDetector.
Tests model loading and inference on a sample frame.
"""

import sys
import os
import numpy as np
import cv2
sys.path.append(os.path.dirname(__file__))  # Add current directory to path for imports

from detector import TrafficLightDetector
from logger import setup_logger

def test_detector():
    print("Testing TrafficLightDetector...")

    # Set up logger
    logger = setup_logger()

    # Initialize detector
    print("Initializing detector...")
    detector = TrafficLightDetector(logger)

    if detector.model is None:
        print("Model failed to load. Check MODEL_PATH in config.py.")
        return False

    print("Model loaded successfully.")

    # Create a dummy frame (black image with some noise to simulate a real frame)
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    # Add some random noise
    noise = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    frame = cv2.addWeighted(frame, 0.5, noise, 0.5, 0)

    print("Running inference on dummy frame...")
    try:
        detections = detector.detect_traffic_lights(frame)
        print(f"Inference successful. Detections: {len(detections)}")
        for det in detections:
            print(f"  - {det}")
        return True
    except Exception as e:
        print(f"Inference failed: {e}")
        return False

if __name__ == '__main__':
    success = test_detector()
    print("Detector test", "PASSED" if success else "FAILED")
