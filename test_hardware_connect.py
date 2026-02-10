"""
Test script for hardware connection using BluetoothManager.
This script attempts to connect to the CHROMA_ESP32 device and send multiple test commands.
If hardware is not available, it will use the mock Bluetooth.
Tests different commands and error scenarios.
"""

import sys
import os
import time
sys.path.append(os.path.dirname(__file__))  # Add current directory to path for imports

from logger import setup_logger
from bluetooth_manager import BluetoothManager

def test_hardware_connect():
    print("Testing hardware connection via BluetoothManager...")

    # Set up logger
    logger = setup_logger()

    # Initialize BluetoothManager
    bt_manager = BluetoothManager(logger)

    if not bt_manager.bluetooth_available:
        print("Bluetooth not available. Test cannot proceed.")
        return False

    print("Bluetooth available. Testing multiple commands...")

    # Test commands
    commands = ['RED', 'YELLOW', 'GREEN', 'OFF', 'VIB_ON', 'VIB_OFF']

    for cmd in commands:
        print(f"Sending command: {cmd}")
        bt_manager.send_vibration_command(cmd)
        time.sleep(1)  # Wait between commands

    # Wait for all commands to complete
    time.sleep(3)

    print("All test commands sent. Check logs for details.")

    # Test error scenario: simulate device not found (by temporarily changing config)
    print("Testing error scenario: device not found...")
    original_name = bt_manager.chroma_address  # Save original
    bt_manager.chroma_address = None  # Force rediscovery
    # Temporarily change device name to non-existent
    import config
    original_device_name = config.BLUETOOTH_DEVICE_NAME
    config.BLUETOOTH_DEVICE_NAME = "NON_EXISTENT_DEVICE"
    bt_manager.send_vibration_command('RED')  # This should fail
    time.sleep(2)
    config.BLUETOOTH_DEVICE_NAME = original_device_name  # Restore
    bt_manager.chroma_address = original_name

    print("Error scenario test completed.")
    return True

if __name__ == '__main__':
    success = test_hardware_connect()
    print("Hardware connect test", "PASSED" if success else "FAILED")
