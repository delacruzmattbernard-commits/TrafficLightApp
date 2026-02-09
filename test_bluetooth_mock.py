"""
Test script for Bluetooth mock functionality.
Simulates the Bluetooth manager's behavior using mock_bluetooth.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))  # Add current directory to path for imports

import mock_bluetooth as bluetooth
from config import BLUETOOTH_DEVICE_NAME

def test_bluetooth_mock():
    print("Testing Bluetooth Mock...")

    # Test discovery
    print("Discovering devices...")
    nearby_devices = bluetooth.discover_devices()
    print(f"Discovered devices: {nearby_devices}")

    # Test lookup
    for addr in nearby_devices:
        name = bluetooth.lookup_name(addr)
        print(f"Device {addr}: {name}")
        if name == BLUETOOTH_DEVICE_NAME:
            print(f"Found target device: {name} at {addr}")
            target_addr = addr
            break
    else:
        print(f"Target device {BLUETOOTH_DEVICE_NAME} not found.")
        return False

    # Test connection and sending
    try:
        print("Connecting to device...")
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        sock.connect((target_addr, 1))
        print("Connected successfully.")

        # Send test commands
        commands = ['RED', 'YELLOW', 'GREEN', 'OFF']
        for cmd in commands:
            sock.send((cmd + '\n').encode())
            print(f"Sent command: {cmd}")

        sock.close()
        print("Disconnected.")
        return True
    except Exception as e:
        print(f"Error during connection/send: {e}")
        return False

if __name__ == '__main__':
    success = test_bluetooth_mock()
    print("Bluetooth Mock test", "PASSED" if success else "FAILED")
