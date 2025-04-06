import sys
import time
from bluetooth.device_manager import DeviceManager
from bluetooth.audio_streamer import AudioStreamer
from utils.sync_helper import calculate_delay
from config.settings import DEFAULT_DELAY

class AudioBroadcaster:
    def __init__(self):
        self.device_manager = DeviceManager()
        self.audio_streamer = AudioStreamer()
        self.connected_devices = []

    def discover_devices(self):
        print("Discovering Bluetooth devices...")
        self.connected_devices = self.device_manager.discover_devices()
        print("Available devices:")
        for idx, device in enumerate(self.connected_devices):
            print(f"{idx + 1}: {device['name']} - {device['address']}")

    def connect_to_device(self, device_index):
        if 0 <= device_index < len(self.connected_devices):
            device = self.connected_devices[device_index]
            self.device_manager.connect(device['address'])
            print(f"Connected to {device['name']}")

    def broadcast_audio(self, delay):
        print("Starting audio broadcast...")
        for device in self.connected_devices:
            self.audio_streamer.start_stream(device['address'], delay)
            print(f"Streaming to {device['name']} with a delay of {delay} seconds")

    def run(self):
        self.discover_devices()
        device_index = int(input("Select a device to connect (number): ")) - 1
        self.connect_to_device(device_index)
        delay = float(input(f"Enter delay in seconds (default {DEFAULT_DELAY}): ") or DEFAULT_DELAY)
        self.broadcast_audio(delay)

if __name__ == "__main__":
    broadcaster = AudioBroadcaster()
    broadcaster.run()