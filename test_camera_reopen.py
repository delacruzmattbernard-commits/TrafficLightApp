import cv2
import time

def test_camera_reopen():
    """Test camera reopening functionality similar to the app's start_detection method."""
    print("Testing camera reopening...")

    # Simulate the logic from start_detection
    cap = None
    camera_index = 0  # Default

    # First, open camera
    print("Opening camera for first time...")
    cap = cv2.VideoCapture(camera_index)
    if cap.isOpened():
        print("Camera opened successfully.")
        ret, frame = cap.read()
        if ret:
            print(f"Frame captured: {frame.shape}")
        else:
            print("Failed to capture frame.")
        cap.release()
        print("Camera released.")
    else:
        print("Failed to open camera.")
        return False

    # Simulate stopping and restarting
    print("\nSimulating stop and restart...")
    if cap:
        cap.release()
        cap = None

    # Reopen camera
    print("Reopening camera...")
    try:
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            print("Failed to reopen camera.")
            return False
        print("Camera reopened successfully.")
        ret, frame = cap.read()
        if ret:
            print(f"Frame captured after reopen: {frame.shape}")
        else:
            print("Failed to capture frame after reopen.")
        cap.release()
        print("Camera released again.")
    except Exception as e:
        print(f"Error reopening camera: {e}")
        return False

    print("Camera reopening test passed!")
    return True

if __name__ == '__main__':
    test_camera_reopen()
