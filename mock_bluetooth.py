"""
Mock Bluetooth module for testing when pybluez is not available.
Simulates discovery and connection for CHROMA_ESP32.
"""

class BluetoothSocket:
    def __init__(self, protocol):
        self.connected = False
        self.protocol = protocol

    def connect(self, addr_port):
        # Simulate connection to CHROMA_ESP32
        addr, port = addr_port
        if addr == "MOCK_CHROMA_ADDR":  # Mock address
            self.connected = True
            print(f"Mock Bluetooth: Connected to {addr} on port {port}")
        else:
            raise Exception("Mock Bluetooth: Device not found")

    def send(self, data):
        if self.connected:
            print(f"Mock Bluetooth: Sent {data.decode().strip()}")
        else:
            raise Exception("Mock Bluetooth: Not connected")

    def close(self):
        self.connected = False
        print("Mock Bluetooth: Disconnected")

def discover_devices():
    # Simulate discovering CHROMA_ESP32
    return ["MOCK_CHROMA_ADDR"]

def lookup_name(addr):
    if addr == "MOCK_CHROMA_ADDR":
        return "CHROMA_ESP32"
    return None

RFCOMM = "RFCOMM"  # Mock constant
