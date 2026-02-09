# Configuration settings for TrafficLightApp

# Model settings
MODEL_PATH = 'chroma-trafficlightmodel (2).pt'
CONFIDENCE_THRESHOLD = 0.7
CLASS_NAMES = {0: 'Red', 1: 'Green', 2: 'Off', 3: 'Yellow'}

# Camera settings
CAMERA_INDEX_DEFAULT = 0
FPS = 15

# Audio settings
AUDIO_INTERVAL_RED = 0.3  # seconds

# Bluetooth settings
BLUETOOTH_DEVICE_NAME = 'CHROMA_ESP32'
BLUETOOTH_TIMEOUT = 5.0  # seconds for discovery

# UI settings
IDLE_TIMEOUT = 30  # seconds

# Logging settings
LOG_LEVEL = 'INFO'
LOG_DIR = 'logs'
