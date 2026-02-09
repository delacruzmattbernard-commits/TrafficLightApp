from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import cv2
import time
import threading
from audio_utils import AudioManager
from logger import setup_logger
from config import CLASS_NAMES, CAMERA_INDEX_DEFAULT, FPS, AUDIO_INTERVAL_RED, IDLE_TIMEOUT
from detector import TrafficLightDetector
from bluetooth_manager import BluetoothManager
import platform

class TrafficLightAppUI(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rows = 2
        self.cols = 1
        self.padding = 10
        self.spacing = 10

        # Set up logger
        self.logger = setup_logger()

        # Initialize detector
        self.detector = TrafficLightDetector(self.logger)

        # Initialize Bluetooth manager
        self.bluetooth_manager = BluetoothManager(self.logger)

        # Image widget to display camera feed
        self.image = Image(size_hint=(1, 0.9))
        self.add_widget(self.image)

        # Controls layout
        controls = BoxLayout(orientation='vertical', size_hint=(1, 0.1))

        # Button to start detection
        self.detect_button = Button(text='Start Detection', size_hint_y=None, height=50, background_color=(0.2, 0.6, 1, 1), color=(1, 1, 1, 1), font_size=18)
        self.detect_button.bind(on_press=self.start_detection)
        controls.add_widget(self.detect_button)

        # Vibration toggle button
        self.vibration_button = Button(text='Vibration: ON', size_hint_y=None, height=50, background_color=(0.6, 0.2, 1, 1), color=(1, 1, 1, 1), font_size=18)
        self.vibration_button.bind(on_press=self.toggle_vibration)
        controls.add_widget(self.vibration_button)

        # Audio toggle button
        self.audio_button = Button(text='Audio: ON', size_hint_y=None, height=50, background_color=(0.2, 1, 0.6, 1), color=(1, 1, 1, 1), font_size=18)
        self.audio_button.bind(on_press=self.toggle_audio)
        controls.add_widget(self.audio_button)

        # Bluetooth status button
        self.bluetooth_button = Button(text='Bluetooth: Not Connected', size_hint_y=None, height=50, background_color=(0.8, 0.8, 0.8, 1), color=(0, 0, 0, 1), font_size=16)
        self.bluetooth_button.bind(on_press=self.show_bluetooth_info)
        controls.add_widget(self.bluetooth_button)

        # Label for results
        self.result_label = Label(text='Detections will appear here', size_hint_y=None, height=50, font_size=16, color=(0, 0, 0, 1))
        controls.add_widget(self.result_label)

        self.add_widget(controls)

        self.detection_active = False
        self.cap = None
        self.conf_threshold = 0.7  # Default confidence threshold
        self.idle_timer = None  # Timer for idle timeout



        # Vibration module settings
        self.vibration_enabled = True
        self.last_audio_time = None  # Track last audio play time

        # Audio manager
        self.audio_manager = AudioManager()

        # Flag to track if red beep has been played for current red light detection
        self.red_beep_played = False

        # Check Bluetooth availability at startup
        self.bluetooth_available = self.bluetooth_manager.bluetooth_available
        if not self.bluetooth_available:
            self.show_popup("Bluetooth Unavailable", "Bluetooth libraries are not installed or available. Vibration features will be disabled.")
            self.vibration_enabled = False
            self.vibration_button.text = 'Vibration: DISABLED'
            self.vibration_button.disabled = True

    def start_detection(self, instance):
        if self.detector.model is None:
            self.result_label.text = 'Model not loaded. Cannot start detection.'
            return
        if not self.detection_active:
            self.detection_active = True
            self.detect_button.text = 'Stop Detection'
            # Ensure any previous capture is released
            if self.cap:
                self.cap.release()
                self.cap = None
            # Default to camera 0 with fallback
            camera_index = CAMERA_INDEX_DEFAULT
            try:
                self.cap = cv2.VideoCapture(camera_index)
                self.logger.info(f"Attempting to open camera {camera_index}")
                if not self.cap.isOpened():
                    self.logger.warning(f"Camera {camera_index} failed to open, trying alternatives")
                    # Try alternative camera indices
                    for alt_index in range(1, 11):
                        self.cap = cv2.VideoCapture(alt_index)
                        if self.cap.isOpened():
                            self.result_label.text = f'Opened camera {alt_index} instead of {camera_index}.'
                            self.logger.info(f"Successfully opened camera {alt_index}")
                            break
                    if not self.cap.isOpened():
                        self.result_label.text = 'Cannot open any camera. Check if camera is connected, not in use by another app, and try different camera indices (0-10).'
                        self.logger.error("Failed to open any camera")
                        self.detection_active = False
                        self.detect_button.text = 'Start Detection'
                        return
                else:
                    self.logger.info(f"Camera {camera_index} opened successfully")
            except Exception as e:
                self.result_label.text = f'Camera initialization error: {e}'
                self.logger.error(f"Camera initialization error: {e}")
                self.detection_active = False
                self.detect_button.text = 'Start Detection'
                if self.cap:
                    self.cap.release()
                    self.cap = None
                return
            Clock.schedule_interval(self.detect_traffic_lights, 1.0 / FPS)  # FPS from config
        else:
            self.detection_active = False
            self.detect_button.text = 'Start Detection'
            if self.cap:
                self.cap.release()
                self.cap = None
            Clock.unschedule(self.detect_traffic_lights)

    def detect_traffic_lights(self, dt):
        try:
            if self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    # Run inference using detector
                    detections = self.detector.detect_traffic_lights(frame)

                    # Annotate the frame with detections
                    annotated_frame = frame.copy()
                    for detection in detections:
                        x1, y1, x2, y2 = detection['bbox']
                        color_name = detection['color']
                        conf = detection['confidence']
                        # Draw bounding box
                        cv2.rectangle(annotated_frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                        # Draw label
                        label = f"{color_name}: {conf:.2f}"
                        cv2.putText(annotated_frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                    # Convert to texture for Kivy
                    try:
                        buf = cv2.flip(annotated_frame, 0).tobytes()
                        texture = Texture.create(size=(annotated_frame.shape[1], annotated_frame.shape[0]), colorfmt='bgr')
                        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                        self.image.texture = texture
                    except Exception as e:
                        self.result_label.text = f"Texture error: {e}"
                        return

                    # Process detections
                    colors = [d['color'] for d in detections]
                    detection_strings = [f"{d['color']}: {d['confidence']:.2f}" for d in detections]

                    if detections:
                        self.result_label.text = f"Detections: {len(detections)} - {', '.join(detection_strings)}"
                        # Reset idle timer on detection
                        if self.idle_timer:
                            self.idle_timer.cancel()
                        self.idle_timer = Clock.schedule_once(self.pause_detection, IDLE_TIMEOUT)
                        # Send vibration commands based on detected colors
                        current_time = time.time()
                        for color in colors:
                            if color == 'Red' and self.bluetooth_manager.last_vibration_color != 'RED':
                                self.bluetooth_manager.send_vibration_command('RED')
                            elif color == 'Yellow' and self.bluetooth_manager.last_vibration_color != 'YELLOW':
                                self.bluetooth_manager.send_vibration_command('YELLOW')
                            elif color == 'Green' and self.bluetooth_manager.last_vibration_color != 'GREEN':
                                self.bluetooth_manager.send_vibration_command('GREEN')

                        # Play red sound only once per red light detection, with interval check
                        if 'Red' in colors and not self.red_beep_played and (self.last_audio_time is None or (current_time - self.last_audio_time) >= AUDIO_INTERVAL_RED):
                            try:
                                self.audio_manager.play_sound('red')
                                self.red_beep_played = True
                            except Exception as e:
                                self.logger.error(f"Error playing audio: {e}")
                            self.last_audio_time = current_time
                        elif 'Red' not in colors:
                            self.red_beep_played = False
                    else:
                        self.result_label.text = "No traffic lights detected"
                        if self.bluetooth_manager.last_vibration_color != 'OFF':
                            self.bluetooth_manager.send_vibration_command('OFF')
                else:
                    self.result_label.text = "Failed to capture frame from camera."
            else:
                self.result_label.text = "Camera not opened."
        except Exception as e:
            self.result_label.text = f"Unexpected error: {e}"
            self.logger.error(f"Detection error: {e}")
            # Stop detection to prevent further crashes
            self.detection_active = False
            self.detect_button.text = 'Start Detection'
            if self.cap:
                self.cap.release()
            Clock.unschedule(self.detect_traffic_lights)

    def toggle_vibration(self, instance):
        self.vibration_enabled = not self.vibration_enabled
        self.vibration_button.text = f'Vibration: {"ON" if self.vibration_enabled else "OFF"}'
        if not self.vibration_enabled:
            self.bluetooth_manager.send_vibration_command('VIB_OFF')
        else:
            self.bluetooth_manager.send_vibration_command('VIB_ON')

    def pause_detection(self, dt):
        """Pause detection after idle timeout"""
        self.detection_active = False
        self.detect_button.text = 'Start Detection'
        if self.cap:
            self.cap.release()
        Clock.unschedule(self.detect_traffic_lights)
        self.result_label.text = 'Detection paused due to inactivity. Tap Start Detection to resume.'
        self.idle_timer = None

    def toggle_audio(self, instance):
        enabled = self.audio_manager.toggle_audio()
        self.audio_button.text = f'Audio: {"ON" if enabled else "OFF"}'

    def check_bluetooth_availability(self):
        """Check if Bluetooth libraries are available"""
        try:
            if platform.system() == 'Windows':
                import bleak
                return True
            else:
                from plyer import bluetooth
                return True
        except ImportError:
            return False

    def show_popup(self, title, message):
        """Show a popup with title and message"""
        popup = Popup(title=title, content=Label(text=message), size_hint=(None, None), size=(400, 200))
        popup.open()

    def show_bluetooth_info(self, instance):
        """Show Bluetooth connection information"""
        if self.bluetooth_manager.bluetooth_available and self.bluetooth_manager.chroma_address:
            message = f"Connected to: {self.bluetooth_manager.chroma_address}"
        else:
            message = "No Bluetooth device connected.\nBluetooth libraries not available or device not found."
        self.show_popup("Bluetooth Status", message)



class TrafficLightApp(App):
    def build(self):
        return TrafficLightAppUI()

if __name__ == '__main__':
    TrafficLightApp().run()
