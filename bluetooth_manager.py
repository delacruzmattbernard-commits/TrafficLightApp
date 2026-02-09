import platform
import asyncio
import threading
from config import BLUETOOTH_DEVICE_NAME, BLUETOOTH_TIMEOUT

class BluetoothManager:
    def __init__(self, logger):
        self.logger = logger
        self.bluetooth_available = self.check_bluetooth_availability()
        self.chroma_address = None
        self.bluetooth_socket = None
        self.last_vibration_color = None

    def check_bluetooth_availability(self):
        """Check if Bluetooth libraries are available."""
        try:
            if platform.system() == 'Windows':
                import bleak
                return True
            else:
                from plyer import bluetooth
                return True
        except ImportError:
            self.logger.warning("Bluetooth libraries not available.")
            return False

    def send_vibration_command(self, command):
        """Send vibration command via Bluetooth."""
        if not self.bluetooth_available:
            return
        if not self.check_bluetooth_availability():
            return  # Bluetooth not available
        # Run Bluetooth send in a separate thread to avoid blocking the UI
        threading.Thread(target=self._send_bluetooth_command, args=(command,)).start()

    def _send_bluetooth_command(self, command):
        try:
            if platform.system() == 'Windows':
                # For Windows, use Bleak or mock
                try:
                    import bleak
                    # Run async Bleak operations synchronously
                    asyncio.run(self._send_bleak_command(command))
                except ImportError:
                    import mock_bluetooth as bluetooth
                    if self.bluetooth_socket is None:
                        # Discover and connect to CHROMA_ESP32
                        nearby_devices = bluetooth.discover_devices()
                        for addr in nearby_devices:
                            if bluetooth.lookup_name(addr) == BLUETOOTH_DEVICE_NAME:
                                self.chroma_address = addr
                                self.bluetooth_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                                self.bluetooth_socket.connect((addr, 1))
                                break
                    if self.bluetooth_socket:
                        self.bluetooth_socket.send((command + '\n').encode())
                        self.last_vibration_color = command if command in ['RED', 'YELLOW', 'GREEN'] else self.last_vibration_color
                        self.logger.info(f"Bluetooth command sent: {command}")
            else:
                # For Android, use Pyjnius to access Android Bluetooth API
                from jnius import autoclass
                BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
                BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
                BluetoothSocket = autoclass('android.bluetooth.BluetoothSocket')

                adapter = BluetoothAdapter.getDefaultAdapter()
                if adapter is None or not adapter.isEnabled():
                    self.logger.error("Bluetooth adapter not available or not enabled")
                    return

                if self.chroma_address is None:
                    # Discover paired devices
                    paired_devices = adapter.getBondedDevices()
                    for device in paired_devices.toArray():
                        if device.getName() == BLUETOOTH_DEVICE_NAME:
                            self.chroma_address = device.getAddress()
                            break

                if self.chroma_address:
                    device = adapter.getRemoteDevice(self.chroma_address)
                    # Use RFCOMM for serial communication
                    socket = device.createRfcommSocketToServiceRecord(device.getUuids()[0].getUuid())
                    socket.connect()
                    output_stream = socket.getOutputStream()
                    output_stream.write((command + '\n').encode())
                    output_stream.flush()
                    socket.close()
                    self.last_vibration_color = command if command in ['RED', 'YELLOW', 'GREEN'] else self.last_vibration_color
                    self.logger.info(f"Bluetooth command sent: {command}")
                else:
                    self.logger.error(f"Device {BLUETOOTH_DEVICE_NAME} not found")
        except Exception as e:
            self.logger.error(f"Bluetooth error: {e}")

    async def _send_bleak_command(self, command):
        """Async function to send command via Bleak."""
        try:
            # Discover devices with timeout
            devices = await asyncio.wait_for(bleak.discover(), timeout=BLUETOOTH_TIMEOUT)
            target_device = None
            for device in devices:
                if device.name == BLUETOOTH_DEVICE_NAME:
                    target_device = device
                    break
            if not target_device:
                raise Exception(f"{BLUETOOTH_DEVICE_NAME} not found")

            # Connect and send data
            async with bleak.BleakClient(target_device.address) as client:
                # Assuming RFCOMM service
                service_uuid = "00001101-0000-1000-8000-00805F9B34FB"
                char_uuid = None
                for service in client.services:
                    if service.uuid == service_uuid:
                        for char in service.characteristics:
                            if "write" in char.properties:
                                char_uuid = char.uuid
                                break
                        break
                if char_uuid:
                    await client.write_gatt_char(char_uuid, (command + '\n').encode())
                    self.last_vibration_color = command if command in ['RED', 'YELLOW', 'GREEN'] else self.last_vibration_color
                    self.chroma_address = target_device.address
                    self.logger.info(f"Bleak command sent: {command}")
                else:
                    raise Exception("No writable characteristic found")
        except asyncio.TimeoutError:
            self.logger.error("Bleak discovery timed out")
        except Exception as e:
            self.logger.error(f"Bleak error: {e}")
